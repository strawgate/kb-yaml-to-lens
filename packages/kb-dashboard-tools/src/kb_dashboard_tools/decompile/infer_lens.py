"""Lens and ES|QL chart inference.

Builds chart config dicts from parsed Kibana Lens and ES|QL visualization
panels — resolving chart types, extracting metrics/dimensions/breakdowns,
legend settings, axis configuration, and appearance options.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from kb_dashboard_core.panels.charts.config import ESQLPanelConfig, LensPanelConfig
from pydantic import TypeAdapter, ValidationError

from .kbn_raw_models.shared.view import KbnReference
from .parse_shared import (
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_list,
    get_number,
    get_str,
    validate_view_model,
    visualization_model_type,
)
from .tables import (
    KIBANA_AXIS_EXTENT_MODE_TO_YAML,
    KIBANA_CURVE_TYPE_TO_YAML,
    KIBANA_DEFAULT_FILL_OPACITY,
    KIBANA_END_VALUE_TO_YAML,
    KIBANA_FITTING_FUNCTION_TO_YAML,
    KIBANA_GAUGE_DEFAULT_SHAPE,
    KIBANA_GAUGE_SHAPE_TO_YAML,
    KIBANA_LEGEND_SIZE_TO_YAML,
    KIBANA_PARTITION_NUMBER_DISPLAY_TO_YAML,
    KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML,
    KIBANA_PIE_NUMBER_DISPLAY_TO_YAML,
    LENS_VISUALIZATION_TYPES,
    OPERATION_TYPE_MAP,
    PARTITION_CHART_TYPES,
    PIE_SHAPES,
    SKIP_OPERATION_TYPES,
    XY_SERIES_TYPES,
    XY_STACKING_MODES,
)

__all__ = ['_infer_lens_chart']

logger = logging.getLogger(__name__)

_lens_panel_adapter: TypeAdapter[LensPanelConfig] = TypeAdapter(LensPanelConfig)
_esql_panel_adapter: TypeAdapter[ESQLPanelConfig] = TypeAdapter(ESQLPanelConfig)

# Chart-type classification sets (reused across functions)
_XY_CHART_TYPES = frozenset({'line', 'bar', 'area'})
_SINGULAR_METRIC_TYPES = frozenset({'gauge', 'tagcloud', 'waffle', 'mosaic', 'treemap'})
_SINGULAR_DIM_TYPES = frozenset({'metric', 'tagcloud', 'waffle', 'mosaic'})
_PARTITION_TYPES = frozenset({'pie', 'treemap'})
_PLURAL_METRIC_TYPES = frozenset({'pie', 'datatable', 'line', 'bar', 'area'})

# Sentinel field name Kibana uses for record-count metrics
_RECORDS_FIELD = 'Records'


# ---------------------------------------------------------------------------
# Internal parsed types (implementation details of this module)
# ---------------------------------------------------------------------------


@dataclass
class _ParsedColumn:
    """A single parsed datasource column (form-based)."""

    column_id: str
    operation_type: str
    source_field: str | None = None
    label: str | None = None
    custom_label: bool = False
    is_bucketed: bool = False
    data_type: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    filter_query: str | None = None
    filter_language: str | None = None


@dataclass
class _ParsedESQLColumn:
    """A single parsed ES|QL column."""

    column_id: str
    field_name: str
    label: str | None = None
    custom_label: bool = False
    meta_type: str | None = None


@dataclass
class _ParsedFormLayer:
    """A parsed form-based datasource layer."""

    layer_id: str
    columns: dict[str, _ParsedColumn] = field(default_factory=dict)
    column_order: list[str] = field(default_factory=list)
    index_pattern_id: str | None = None


@dataclass
class _ParsedESQLLayer:
    """A parsed ES|QL datasource layer."""

    layer_id: str
    query: str
    columns: list[_ParsedESQLColumn] = field(default_factory=list)
    time_field: str = '@timestamp'


@dataclass
class _ParsedVisualizationLayerRole:
    """Accessor roles for a single visualization layer."""

    layer_id: str
    metric_ids: list[str] = field(default_factory=list)
    dimension_id: str | None = None
    breakdown_id: str | None = None
    accessors: list[str] = field(default_factory=list)


@dataclass
class _ParsedVisualizationState:
    """Parsed visualization state with resolved chart type."""

    raw_type: str | None = None
    preferred_series_type: str | None = None
    shape: str | None = None
    layer_roles: dict[str, _ParsedVisualizationLayerRole] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    view_model: Any = None


@dataclass
class _InferredLensPanel:
    """Intermediate structure for lens/esql panel inference."""

    panel_type: str  # 'lens' or 'esql'
    visualization_state: _ParsedVisualizationState | None = None
    form_layers: dict[str, _ParsedFormLayer] = field(default_factory=dict)
    esql_layers: dict[str, _ParsedESQLLayer] = field(default_factory=dict)
    data_view_id: str | None = None
    esql_query: str | None = None


# ---------------------------------------------------------------------------
# Panel parsing helpers (previously in parse_panels.py)
# ---------------------------------------------------------------------------


def _parse_column(col_id: str, col: dict[str, Any]) -> _ParsedColumn:
    op_type = get_str(col, 'operationType')
    data_type = get_str(col, 'dataType')
    parsed = _ParsedColumn(
        column_id=col_id,
        operation_type=op_type if op_type is not None else 'unknown',
        is_bucketed=bool(col.get('isBucketed')),
        data_type=data_type,
    )
    source_field = get_str(col, 'sourceField')
    if source_field is not None:
        parsed.source_field = source_field
    label = get_str(col, 'label')
    if label is not None:
        parsed.label = label
    parsed.custom_label = bool(col.get('customLabel'))
    params = get_dict(col, 'params')
    if params is not None:
        parsed.params = params

    col_filter = get_dict(col, 'filter')
    if col_filter is not None:
        q = get_str(col_filter, 'query')
        lang = get_str(col_filter, 'language')
        if q is not None:
            parsed.filter_query = q
            parsed.filter_language = lang
    return parsed


def _parse_esql_column(raw: dict[str, Any]) -> _ParsedESQLColumn | None:
    col_id = get_str(raw, 'columnId')
    field_name = get_str(raw, 'fieldName')
    if col_id is None or field_name is None:
        return None
    parsed = _ParsedESQLColumn(column_id=col_id, field_name=field_name)
    label = get_str(raw, 'label')
    if label is not None:
        parsed.label = label
    parsed.custom_label = bool(raw.get('customLabel'))
    meta = get_dict(raw, 'meta')
    if meta is not None:
        mt = get_str(meta, 'type')
        if mt is not None:
            parsed.meta_type = mt
    return parsed


def _dedupe_ids(ids: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for i in ids:
        if i not in seen:
            result.append(i)
            seen.add(i)
    return result


def _collect_accessor_ids(source: dict[str, Any], scalar_keys: tuple[str, ...]) -> list[str]:
    ids: list[str] = []
    for key in scalar_keys:
        value = get_str(source, key)
        if value is not None:
            ids.append(value)
    list_accessors = get_list(source, 'accessors')
    if list_accessors is not None:
        ids.extend([a for a in list_accessors if isinstance(a, str)])
    return _dedupe_ids(ids)


def _get_datasource_layers(state: dict[str, Any], datasource_key: str) -> dict[str, Any] | None:
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return None
    datasource = get_dict(ds_states, datasource_key)
    if datasource is None:
        return None
    return get_dict(datasource, 'layers')


def _extract_data_view_from_refs(refs: list[KbnReference]) -> str | None:
    for ref in refs:
        if ref.type == 'index-pattern':
            return ref.id
    return None


def _parse_multi_layer_roles(parsed_vis: _ParsedVisualizationState, visualization: dict[str, Any]) -> None:
    vis_layers = get_list(visualization, 'layers')
    if vis_layers is None:
        return
    for vis_layer_obj in vis_layers:
        vis_layer = as_dict(vis_layer_obj)
        if vis_layer is None:
            continue
        layer_id = get_str(vis_layer, 'layerId')
        if layer_id is None:
            continue
        role = _ParsedVisualizationLayerRole(layer_id=layer_id)
        raw_accessors = get_list(vis_layer, 'accessors')
        if raw_accessors is not None:
            role.metric_ids = [v for v in raw_accessors if isinstance(v, str)]
        x_accessor = get_str(vis_layer, 'xAccessor')
        if x_accessor is not None:
            role.dimension_id = x_accessor
        split_accessor = get_str(vis_layer, 'splitAccessor')
        if split_accessor is not None:
            role.breakdown_id = split_accessor
        role.accessors = _dedupe_ids(
            [
                *_collect_accessor_ids(vis_layer, ('xAccessor', 'splitAccessor')),
                *role.metric_ids,
            ]
        )
        parsed_vis.layer_roles[layer_id] = role


def _parse_single_layer_roles(
    parsed_vis: _ParsedVisualizationState,
    visualization: dict[str, Any],
) -> None:
    single_layer_id = get_str(visualization, 'layerId')
    if single_layer_id is None:
        return
    role = parsed_vis.layer_roles.setdefault(single_layer_id, _ParsedVisualizationLayerRole(layer_id=single_layer_id))
    for key in ('metricAccessor', 'secondaryAccessor', 'accessor'):
        value = get_str(visualization, key)
        if value is not None and value not in role.metric_ids:
            role.metric_ids.append(value)
    raw_accessors = get_list(visualization, 'accessors')
    if raw_accessors is not None:
        for v in raw_accessors:
            if isinstance(v, str) and v not in role.metric_ids:
                role.metric_ids.append(v)
    x_accessor = get_str(visualization, 'xAccessor')
    if x_accessor is not None:
        role.dimension_id = x_accessor
    split_accessor = get_str(visualization, 'splitAccessor')
    if split_accessor is not None:
        role.breakdown_id = split_accessor
    if not role.accessors:
        role.accessors = _collect_accessor_ids(
            visualization,
            ('xAccessor', 'metricAccessor', 'splitAccessor', 'secondaryAccessor', 'accessor'),
        )


def _parse_visualization_state(state: dict[str, Any], vis_type: str | None, *, is_esql: bool) -> _ParsedVisualizationState:
    parsed_vis = _ParsedVisualizationState(raw_type=vis_type)
    visualization = get_dict(state, 'visualization')
    if visualization is None:
        return parsed_vis

    parsed_vis.raw = visualization
    parsed_vis.preferred_series_type = get_str(visualization, 'preferredSeriesType')
    parsed_vis.shape = get_str(visualization, 'shape')

    model_cls = visualization_model_type(vis_type, visualization, is_esql=is_esql)
    if model_cls is not None:
        parsed_vis.view_model = validate_view_model(model_cls, visualization)

    _parse_multi_layer_roles(parsed_vis, visualization)
    _parse_single_layer_roles(parsed_vis, visualization)

    return parsed_vis


def _parse_form_based_layers(state: dict[str, Any]) -> dict[str, _ParsedFormLayer]:
    layers_raw = _get_datasource_layers(state, 'formBased')
    if layers_raw is None:
        return {}

    layers: dict[str, _ParsedFormLayer] = {}
    for layer_id, layer in layers_raw.items():  # pyright: ignore[reportAny]
        layer_dict = as_dict(layer)  # pyright: ignore[reportAny]
        if layer_dict is None:
            continue
        parsed_layer = _ParsedFormLayer(layer_id=layer_id, index_pattern_id=get_str(layer_dict, 'indexPatternId'))
        column_order = get_list(layer_dict, 'columnOrder')
        if column_order is not None:
            parsed_layer.column_order = [c for c in column_order if isinstance(c, str)]
        cols = get_dict(layer_dict, 'columns') or {}
        for col_id, col_val in cols.items():  # pyright: ignore[reportAny]
            col = as_dict(col_val)  # pyright: ignore[reportAny]
            if col is not None:
                parsed_layer.columns[col_id] = _parse_column(col_id, col)
        layers[layer_id] = parsed_layer
    return layers


def _extract_esql_query_from_state(state: dict[str, Any]) -> str | None:
    top_query = get_dict(state, 'query')
    if top_query is not None:
        esql = get_str(top_query, 'esql')
        if esql is not None:
            return esql
    layers_raw = _get_datasource_layers(state, 'textBased')
    if layers_raw is None:
        return None
    for layer_obj in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_obj)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = get_dict(layer, 'query')
        if query is not None:
            esql = get_str(query, 'esql')
            if esql is not None:
                return esql
    return None


def _has_text_based_query(state: dict[str, Any]) -> bool:
    top_query = get_dict(state, 'query')
    if top_query is not None and get_str(top_query, 'esql') is not None:
        return True
    layers_raw = _get_datasource_layers(state, 'textBased')
    if layers_raw is None:
        return False
    for layer_obj in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_obj)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = get_dict(layer, 'query')
        if query is not None and get_str(query, 'esql') is not None:
            return True
    return False


def _parse_esql_layers(state: dict[str, Any]) -> dict[str, _ParsedESQLLayer]:
    layers_raw = _get_datasource_layers(state, 'textBased')
    if layers_raw is None:
        return {}

    top_esql = _extract_esql_query_from_state(state)
    layers: dict[str, _ParsedESQLLayer] = {}
    for layer_id, layer_obj in layers_raw.items():  # pyright: ignore[reportAny]
        layer = as_dict(layer_obj)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query_obj = get_dict(layer, 'query')
        esql = get_str(query_obj, 'esql') if query_obj is not None else top_esql
        if esql is None:
            continue
        parsed_layer = _ParsedESQLLayer(layer_id=layer_id, query=esql)
        time_field = get_str(layer, 'timeField')
        if time_field is not None:
            parsed_layer.time_field = time_field
        for col_list_key in ('columns', 'allColumns'):
            col_list = get_list(layer, col_list_key)
            if col_list is None:
                continue
            for raw_col in col_list:
                col = as_dict(raw_col)
                if col is None:
                    continue
                parsed_col = _parse_esql_column(col)
                if parsed_col is None:
                    continue
                if parsed_col.column_id not in {c.column_id for c in parsed_layer.columns}:
                    parsed_layer.columns.append(parsed_col)
        layers[layer_id] = parsed_layer
    return layers


def _build_inferred_lens_panel(panel_dict: dict[str, Any]) -> _InferredLensPanel:
    """Extract typed intermediate data from a raw Lens or ES|QL panel dict."""
    # Use base panel for grid/index info only; access embeddableConfig via raw dict
    # (KbnLensPanel enforces type='lens' literal which fails for 'esql' panels)
    ec_dict = get_dict(panel_dict, 'embeddableConfig') or {}
    attrs_dict = get_dict(ec_dict, 'attributes') or {}
    state_dict = get_dict(attrs_dict, 'state') or {}

    raw_panel_type = get_str(panel_dict, 'type') or ''
    is_esql = raw_panel_type == 'esql' or _has_text_based_query(state_dict)
    panel_type = 'esql' if is_esql else 'lens'

    vis_type = get_str(attrs_dict, 'visualizationType')

    vis_state = _parse_visualization_state(state_dict, vis_type, is_esql=is_esql)
    form_layers = _parse_form_based_layers(state_dict) if not is_esql else {}
    esql_layers = _parse_esql_layers(state_dict) if is_esql else {}
    esql_query = _extract_esql_query_from_state(state_dict) if is_esql else None

    # Resolve data view from references — try attributes.references first, then embeddableConfig.references
    refs: list[KbnReference] = []
    for refs_source in (get_list(attrs_dict, 'references'), get_list(ec_dict, 'references')):
        if refs_source is not None:
            for r in refs_source:
                r_dict = as_dict(r)
                if r_dict is not None:
                    try:
                        refs.append(KbnReference.model_validate(r_dict))
                    except ValidationError:
                        logger.warning('Skipping malformed Kibana reference in panel payload: %s', r_dict)
            break  # use first source that is non-None

    data_view_id = _extract_data_view_from_refs(refs)

    return _InferredLensPanel(
        panel_type=panel_type,
        visualization_state=vis_state,
        form_layers=form_layers,
        esql_layers=esql_layers,
        data_view_id=data_view_id,
        esql_query=esql_query,
    )


# ---------------------------------------------------------------------------
# Chart type resolution
# ---------------------------------------------------------------------------


def _merge_appearance(chart: dict[str, Any], new_appearance: dict[str, Any] | None) -> None:
    """Merge appearance settings into chart, updating existing if present."""
    if new_appearance is None:
        return
    existing = as_dict(chart.get('appearance'))
    if existing is not None:
        existing.update(new_appearance)
    else:
        chart['appearance'] = new_appearance


def _resolve_chart_type(vis_state: _ParsedVisualizationState) -> str | None:
    """Map Kibana visualization type + series preferences to a YAML chart type."""
    raw = vis_state.raw_type
    if raw is None:
        return None
    normalized = LENS_VISUALIZATION_TYPES.get(raw.lower())
    if raw.lower() in {'lnsxy', 'xy'}:
        pst = vis_state.preferred_series_type
        if pst is not None:
            return XY_SERIES_TYPES.get(pst, 'line')
        return 'line'
    if raw.lower() in {'lnspie', 'pie'}:
        shape = vis_state.shape
        if shape is not None:
            resolved = PIE_SHAPES.get(shape)
            if resolved is not None and resolved != 'pie':
                return resolved
    return normalized


def _resolve_stacking_mode(vis_state: _ParsedVisualizationState, chart_type: str | None) -> str | None:
    """Determine stacking mode (stacked/percentage) for bar and area charts."""
    if chart_type not in {'bar', 'area'}:
        return None
    pst = vis_state.preferred_series_type
    if pst is None:
        return None
    return XY_STACKING_MODES.get(pst)


# ---------------------------------------------------------------------------
# Metric / dimension / breakdown extraction (form-based)
# ---------------------------------------------------------------------------


def _extract_metric_filter(col: _ParsedColumn) -> dict[str, str] | None:
    """Extract the metric-level KQL/Lucene filter from a column, if present."""
    if col.filter_query is not None:
        if col.filter_language == 'kuery':
            return {'kql': col.filter_query}
        if col.filter_language == 'lucene':
            return {'lucene': col.filter_query}
    kql = get_str(col.params, 'kql')
    if kql is not None and len(kql) > 0:
        return {'kql': kql}
    return None


def _extract_metric_format(col: _ParsedColumn) -> dict[str, Any] | None:
    """Extract number/byte/percent format configuration from a column."""
    format_config = get_dict(col.params, 'format')
    if format_config is None:
        return None
    format_type = get_str(format_config, 'id')
    if format_type is None or format_type not in {'number', 'bytes', 'bits', 'percent', 'duration', 'custom'}:
        return None
    fmt: dict[str, Any] = {'type': format_type}
    format_params = get_dict(format_config, 'params')
    if format_params is None:
        if format_type == 'custom':
            return None
        return fmt
    for key in ('decimals', 'suffix', 'compact', 'pattern'):
        val = format_params.get(key)
        if val is not None:
            fmt[key] = val
    # custom format requires a pattern; fall back to number if none is present
    if format_type == 'custom' and 'pattern' not in fmt:
        fmt['type'] = 'number'
    return fmt


def _build_metric_dict(col: _ParsedColumn) -> dict[str, Any] | None:
    """Build a metric config dict from a form-based column. Returns None if skipped."""
    if col.operation_type in SKIP_OPERATION_TYPES:
        return None

    # Formula metrics bypass the normal aggregation mapping
    if col.operation_type == 'formula':
        formula_str = get_str(col.params, 'formula')
        if formula_str is None:
            return None
        metric: dict[str, Any] = {'formula': formula_str}
        if col.label is not None and len(col.label) > 0:
            metric['label'] = col.label
        fmt = _extract_metric_format(col)
        if fmt is not None:
            metric['format'] = fmt
        return metric

    aggregation = OPERATION_TYPE_MAP.get(col.operation_type)
    if aggregation is None:
        return None

    metric = {'aggregation': aggregation}
    if col.source_field is not None and col.source_field != _RECORDS_FIELD:
        metric['field'] = col.source_field
    if col.label is not None and len(col.label) > 0:
        metric['label'] = col.label

    # Extract percentile-specific parameters
    if col.operation_type == 'percentile':
        percentile_val = get_number(col.params, 'percentile')
        if percentile_val is not None:
            metric['percentile'] = int(percentile_val)
    elif col.operation_type == 'percentile_rank':
        rank_val = get_number(col.params, 'value')
        if rank_val is not None:
            metric['rank'] = rank_val

    filt = _extract_metric_filter(col)
    if filt is not None:
        metric['filter'] = filt
    fmt = _extract_metric_format(col)
    if fmt is not None:
        metric['format'] = fmt
    return metric


def _build_dimension_dict(col: _ParsedColumn) -> tuple[str, dict[str, Any]] | None:
    """Build a dimension or breakdown dict. Returns (category, dict) or None."""
    if col.operation_type == 'date_histogram':
        dim: dict[str, Any] = {'type': 'date_histogram'}
        if col.source_field is not None:
            dim['field'] = col.source_field
        interval = get_str(col.params, 'interval')
        if interval is not None and interval not in {'auto', ''}:
            # Kibana stores bare units like 'm'; compiler expects '1m'
            if re.match(r'^(ms|s|m|h|d|w|M|q|y)$', interval):
                interval = f'1{interval}'
            dim['minimum_interval'] = interval
        return 'dimension', dim

    if col.operation_type == 'terms':
        bd: dict[str, Any] = {'type': 'values'}
        if col.source_field is not None:
            bd['field'] = col.source_field
        size = get_int(col.params, 'size')
        if size is not None:
            bd['size'] = size
        return 'breakdown', bd

    if col.operation_type == 'filters':
        filters_list: list[dict[str, Any]] = []
        raw_filters = get_list(col.params, 'filters')
        if raw_filters is not None:
            for f in raw_filters:
                f_dict = as_dict(f)
                if f_dict is not None:
                    f_entry: dict[str, Any] = {}
                    label = get_str(f_dict, 'label')
                    if label is not None:
                        f_entry['label'] = label
                    inp = get_dict(f_dict, 'input')
                    if inp is not None:
                        query = get_str(inp, 'query')
                        language = get_str(inp, 'language')
                        if query is not None:
                            if language == 'lucene':
                                f_entry['query'] = {'lucene': query}
                            else:
                                f_entry['query'] = {'kql': query}
                    if 'query' in f_entry:
                        filters_list.append(f_entry)
        if not filters_list:
            filters_list = [{'query': {'kql': '*'}}]
        return 'breakdown', {'type': 'filters', 'filters': filters_list}

    return None


def _classify_form_columns(
    layer: _ParsedFormLayer,
    layer_role: _ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Classify form-based columns into metrics, dimensions, breakdowns, skipped."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []
    skipped: list[str] = []

    # Determine iteration order: prefer visualization accessor order
    if layer_role is not None and layer_role.accessors:
        ordered_ids = list(dict.fromkeys([*layer_role.accessors, *layer.column_order, *list(layer.columns.keys())]))
    elif layer.column_order:
        ordered_ids = layer.column_order
    else:
        ordered_ids = list(layer.columns.keys())

    for col_id in ordered_ids:
        col = layer.columns.get(col_id)
        if col is None:
            continue
        if col.is_bucketed:
            result = _build_dimension_dict(col)
            if result is not None:
                category, stub = result
                if category == 'dimension':
                    dimensions.append(stub)
                else:
                    breakdowns.append(stub)
        else:
            metric = _build_metric_dict(col)
            if metric is not None:
                metrics.append(metric)
            else:
                skipped.append(col.operation_type)

    return metrics, dimensions, breakdowns, skipped


# ---------------------------------------------------------------------------
# ES|QL column extraction
# ---------------------------------------------------------------------------


def _esql_column_entry(col: _ParsedESQLColumn) -> dict[str, Any]:
    """Build an ES|QL column reference dict from a parsed column."""
    entry: dict[str, Any] = {'field': col.field_name}
    if col.label is not None and col.label != col.field_name:
        entry['label'] = col.label
    return entry


def _classify_esql_columns(
    layer: _ParsedESQLLayer,
    layer_role: _ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify ES|QL columns into metrics, dimensions, breakdowns using layer roles."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []

    columns_by_id: dict[str, _ParsedESQLColumn] = {c.column_id: c for c in layer.columns}

    if layer_role is None:
        return metrics, dimensions, breakdowns

    for metric_id in layer_role.metric_ids:
        col = columns_by_id.get(metric_id)
        if col is not None:
            metrics.append(_esql_column_entry(col))

    if layer_role.dimension_id is not None:
        col = columns_by_id.get(layer_role.dimension_id)
        if col is not None:
            dimensions.append(_esql_column_entry(col))

    if layer_role.breakdown_id is not None:
        col = columns_by_id.get(layer_role.breakdown_id)
        if col is not None:
            breakdowns.append(_esql_column_entry(col))

    return metrics, dimensions, breakdowns


# ---------------------------------------------------------------------------
# Legend extraction
# ---------------------------------------------------------------------------


def _extract_legend_common(  # noqa: PLR0913
    source: dict[str, Any],
    *,
    visible_key: str = 'isVisible',
    visible_is_bool: bool = True,
    position_key: str = 'position',
    truncate_key: str = 'shouldTruncate',
    max_lines_key: str = 'maxLines',
) -> dict[str, Any]:
    """Extract common legend settings from a source dict.

    Returns a (possibly empty) dict of legend settings.
    """
    legend: dict[str, Any] = {}

    if visible_is_bool:
        is_visible = get_bool(source, visible_key)
        if is_visible is not None:
            legend['visible'] = 'show' if is_visible else 'hide'
    else:
        display = get_str(source, visible_key)
        if display in ('show', 'hide'):
            legend['visible'] = display

    position = get_str(source, position_key)
    if position is not None and position != 'right':
        legend['position'] = position

    show_single = get_bool(source, 'showSingleSeries')
    if show_single is not None and show_single:
        legend['show_single_series'] = True

    legend_size = get_str(source, 'legendSize')
    if legend_size is not None and legend_size in KIBANA_LEGEND_SIZE_TO_YAML:
        legend['width'] = KIBANA_LEGEND_SIZE_TO_YAML[legend_size]

    should_truncate = get_bool(source, truncate_key)
    max_lines = get_int(source, max_lines_key)
    if should_truncate is not None and not should_truncate:
        legend['truncate_labels'] = 0
    elif max_lines is not None and max_lines > 0:
        legend['truncate_labels'] = max_lines

    return legend


def _extract_xy_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from an XY visualization state."""
    legend_raw = get_dict(vis_raw, 'legend')
    if legend_raw is None:
        return None
    legend = _extract_legend_common(legend_raw)
    return legend if legend else None


def _extract_partition_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from a partition chart (pie, waffle, mosaic, treemap) visualization layer."""
    layers = get_list(vis_raw, 'layers')
    if layers is None or len(layers) == 0:
        return None
    layer = as_dict(layers[0])
    if layer is None:
        return None
    legend = _extract_legend_common(
        layer,
        visible_key='legendDisplay',
        visible_is_bool=False,
        position_key='legendPosition',
        truncate_key='truncateLegend',
        max_lines_key='legendMaxLines',
    )
    nested_legend = get_bool(layer, 'nestedLegend')
    if nested_legend is not None and nested_legend:
        legend['nested'] = True
    return legend if legend else None


# ---------------------------------------------------------------------------
# XY Appearance extraction
# ---------------------------------------------------------------------------


def _extract_axis_config(
    vis_raw: dict[str, Any],
    scale_key: str,
    title_key: str,
    extent_key: str,
    title_visibility_axis: str,
) -> dict[str, Any] | None:
    """Extract axis configuration (scale, title, extent) for a single axis."""
    axis: dict[str, Any] = {}

    # Axis title visibility — False hides the title regardless of custom text
    title_hidden = False
    axis_vis_settings = get_dict(vis_raw, 'axisTitlesVisibilitySettings')
    if axis_vis_settings is not None:
        show_title = get_bool(axis_vis_settings, title_visibility_axis)
        if show_title is not None and not show_title:
            axis['title'] = False
            title_hidden = True

    # Custom axis title (skip if visibility is explicitly hidden)
    if not title_hidden:
        title_val = get_str(vis_raw, title_key)
        if title_val is not None and len(title_val) > 0:
            axis['title'] = title_val

    # Scale
    scale_val = get_str(vis_raw, scale_key)
    if scale_val is not None and scale_val != 'linear':
        axis['scale'] = scale_val

    # Extent
    extent_raw = get_dict(vis_raw, extent_key)
    if extent_raw is not None:
        mode = get_str(extent_raw, 'mode')
        if mode is not None and mode != 'full':
            extent: dict[str, Any] = {}
            yaml_mode = KIBANA_AXIS_EXTENT_MODE_TO_YAML.get(mode, mode)
            extent['mode'] = yaml_mode
            if mode == 'custom':
                lower = get_number(extent_raw, 'lowerBound')
                upper = get_number(extent_raw, 'upperBound')
                if lower is not None:
                    extent['min'] = lower
                if upper is not None:
                    extent['max'] = upper
            axis['extent'] = extent

    return axis if axis else None


def _extract_xy_appearance(vis_raw: dict[str, Any], chart_type: str | None) -> dict[str, Any] | None:
    """Extract appearance settings from an XY visualization state."""
    appearance: dict[str, Any] = {}

    # Missing values (fitting function) -- line/area only
    if chart_type in {'line', 'area'}:
        fitting = get_str(vis_raw, 'fittingFunction')
        if fitting is not None and fitting in KIBANA_FITTING_FUNCTION_TO_YAML:
            appearance['missing_values'] = KIBANA_FITTING_FUNCTION_TO_YAML[fitting]

        emphasize = get_bool(vis_raw, 'emphasizeFitting')
        if emphasize is not None and emphasize:
            appearance['show_as_dotted'] = True

        end_value = get_str(vis_raw, 'endValue')
        if end_value is not None and end_value in KIBANA_END_VALUE_TO_YAML:
            appearance['end_values'] = KIBANA_END_VALUE_TO_YAML[end_value]

        curve_type = get_str(vis_raw, 'curveType')
        if curve_type is not None and curve_type in KIBANA_CURVE_TYPE_TO_YAML:
            appearance['line_style'] = KIBANA_CURVE_TYPE_TO_YAML[curve_type]

        show_time_marker = get_bool(vis_raw, 'showCurrentTimeMarker')
        if show_time_marker is not None and show_time_marker:
            appearance['show_current_time_marker'] = True

        hide_endzones = get_bool(vis_raw, 'hideEndzones')
        if hide_endzones is not None and hide_endzones:
            appearance['hide_endzones'] = True

    # Fill opacity -- area only
    if chart_type == 'area':
        fill_opacity = get_number(vis_raw, 'fillOpacity')
        if fill_opacity is not None and fill_opacity != KIBANA_DEFAULT_FILL_OPACITY:
            appearance['fill_opacity'] = fill_opacity

    # Min bar height -- bar only
    if chart_type == 'bar':
        min_bar_height = get_number(vis_raw, 'minBarHeight')
        if min_bar_height is not None and min_bar_height > 0:
            appearance['min_bar_height'] = min_bar_height

    # Value labels
    value_labels = get_str(vis_raw, 'valueLabels')
    if value_labels is not None and value_labels == 'show':
        appearance.setdefault('values', {})['visible'] = True

    # Axis configs
    y_left = _extract_axis_config(vis_raw, 'yLeftScale', 'yTitle', 'yLeftExtent', 'yLeft')
    y_left_fallback = _extract_axis_config(vis_raw, 'yLeftScale', 'yLeftTitle', 'yLeftExtent', 'yLeft')
    if y_left is not None and y_left_fallback is not None:
        # Prefer yLeftTitle when present (newer Kibana), while preserving scale/extent fields.
        y_left.update(y_left_fallback)
    elif y_left_fallback is not None:
        y_left = y_left_fallback
    if y_left is not None:
        appearance['y_left_axis'] = y_left

    y_right = _extract_axis_config(vis_raw, 'yRightScale', 'yRightTitle', 'yRightExtent', 'yRight')
    if y_right is not None:
        appearance['y_right_axis'] = y_right

    x_axis = _extract_axis_config(vis_raw, 'xScale', 'xTitle', 'xExtent', 'x')
    if x_axis is not None:
        appearance['x_axis'] = x_axis

    return appearance if appearance else None


# ---------------------------------------------------------------------------
# Gauge / partition / datatable appearance extraction
# ---------------------------------------------------------------------------


def _extract_gauge_settings(
    vis_raw: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Extract gauge appearance and titles_and_text from visualization state raw dict.

    Returns (appearance_dict, titles_and_text_dict) — either may be None.
    """
    appearance: dict[str, Any] = {}
    titles: dict[str, Any] = {}

    shape = get_str(vis_raw, 'shape')
    if shape is not None and shape in KIBANA_GAUGE_SHAPE_TO_YAML and shape != KIBANA_GAUGE_DEFAULT_SHAPE:
        appearance['shape'] = KIBANA_GAUGE_SHAPE_TO_YAML[shape]

    ticks_pos = get_str(vis_raw, 'ticksPosition')
    if ticks_pos is not None and ticks_pos != 'auto':
        appearance['ticks_position'] = ticks_pos

    label_major_mode = get_str(vis_raw, 'labelMajorMode')
    label_major = get_str(vis_raw, 'labelMajor')
    if label_major_mode == 'none':
        titles['title'] = False
    elif label_major_mode in ('custom', None) and label_major is not None and len(label_major) > 0:
        titles['title'] = label_major

    label_minor = get_str(vis_raw, 'labelMinor')
    if label_minor is not None and len(label_minor) > 0:
        titles['subtitle'] = label_minor

    return (appearance if appearance else None), (titles if titles else None)


def _extract_partition_appearance(vis_raw: dict[str, Any], chart_type: str | None = None) -> dict[str, Any] | None:
    """Extract appearance settings from a partition chart (pie/treemap/waffle/mosaic) visualization state."""
    layers = get_list(vis_raw, 'layers')
    if layers is None or len(layers) == 0:
        return None
    layer = as_dict(layers[0])
    if layer is None:
        return None

    appearance: dict[str, Any] = {}

    number_display = get_str(layer, 'numberDisplay')
    if number_display is not None:
        # Pie and treemap use 'integer' for the raw Kibana 'value'; mosaic and waffle use 'value'
        number_display_map = (
            KIBANA_PIE_NUMBER_DISPLAY_TO_YAML if chart_type in (None, 'pie', 'treemap') else KIBANA_PARTITION_NUMBER_DISPLAY_TO_YAML
        )
        if number_display in number_display_map:
            yaml_val = number_display_map[number_display]
            if yaml_val != 'percent':  # percent is Kibana default — omit
                appearance.setdefault('values', {})['format'] = yaml_val

    percent_decimals = get_int(layer, 'percentDecimals')
    if percent_decimals is not None:
        appearance.setdefault('values', {})['decimal_places'] = percent_decimals

    category_display = get_str(layer, 'categoryDisplay')
    if category_display is not None and category_display in KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML:
        yaml_val = KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML[category_display]
        if yaml_val != 'auto':  # auto is Kibana default — omit
            appearance.setdefault('categories', {})['position'] = yaml_val

    return appearance if appearance else None


def _extract_datatable_options(
    vis_raw: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Extract sorting, paging, and appearance from datatable visualization state.

    Returns (sorting_dict, paging_dict, appearance_dict) — any may be None.
    """
    sorting: dict[str, Any] | None = None
    paging: dict[str, Any] | None = None
    appearance: dict[str, Any] = {}

    sorting_raw = get_dict(vis_raw, 'sorting')
    if sorting_raw is not None:
        col_id = get_str(sorting_raw, 'columnId')
        direction = get_str(sorting_raw, 'direction')
        if col_id is not None and direction is not None and direction != 'none':
            sorting = {'column_id': col_id, 'direction': direction}

    paging_raw = get_dict(vis_raw, 'paging')
    if paging_raw is not None:
        enabled = get_bool(paging_raw, 'enabled')
        size = get_int(paging_raw, 'size')
        if enabled is not None and size is not None:
            paging = {'enabled': enabled, 'page_size': size}

    row_height = get_str(vis_raw, 'rowHeight')
    if row_height is not None and row_height != 'auto':
        appearance['row_height'] = row_height

    row_height_lines = get_int(vis_raw, 'rowHeightLines')
    if row_height_lines is not None:
        appearance['row_height_lines'] = row_height_lines

    header_row_height = get_str(vis_raw, 'headerRowHeight')
    if header_row_height is not None and header_row_height != 'auto':
        appearance['header_row_height'] = header_row_height

    header_row_height_lines = get_int(vis_raw, 'headerRowHeightLines')
    if header_row_height_lines is not None:
        appearance['header_row_height_lines'] = header_row_height_lines

    density = get_str(vis_raw, 'density')
    if density is not None and density != 'normal':
        appearance['density'] = density

    return sorting, paging, (appearance if appearance else None)


# ---------------------------------------------------------------------------
# Metrics / dimensions / defaults assignment
# ---------------------------------------------------------------------------


def _assign_metrics_and_dimensions(
    chart: dict[str, Any],
    chart_type: str,
    all_metrics: list[dict[str, Any]],
    all_dimensions: list[dict[str, Any]],
    all_breakdowns: list[dict[str, Any]],
) -> None:
    """Assign extracted metrics, dimensions, and breakdowns to the chart dict based on chart type."""
    is_xy = chart_type in _XY_CHART_TYPES
    is_heatmap = chart_type == 'heatmap'

    # -- Metrics --
    if chart_type == 'metric':
        if len(all_metrics) > 0:
            chart['primary'] = all_metrics[0]
        if len(all_metrics) > 1:
            chart['secondary'] = all_metrics[1]
    elif is_heatmap or chart_type in _SINGULAR_METRIC_TYPES:
        if len(all_metrics) > 0:
            chart['metric'] = all_metrics[0]
    elif chart_type in _PLURAL_METRIC_TYPES and len(all_metrics) > 0:
        chart['metrics'] = all_metrics

    # -- Dimensions --
    if is_xy:
        if len(all_dimensions) > 0:
            chart['dimension'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['breakdown'] = all_breakdowns[0]
    elif is_heatmap:
        if len(all_dimensions) > 0:
            chart['x_axis'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['y_axis'] = all_breakdowns[0]
        elif len(all_dimensions) > 1:
            chart['y_axis'] = all_dimensions[1]
    elif chart_type in _SINGULAR_DIM_TYPES:
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            if chart_type in ('metric', 'waffle'):
                chart['breakdown'] = merged[0]
            else:
                chart['dimension'] = merged[0]
        if chart_type == 'mosaic' and len(merged) > 1:
            chart['breakdown'] = merged[1]
    elif chart_type != 'gauge':
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            chart['breakdowns'] = merged


def _fill_required_defaults(
    chart: dict[str, Any],
    chart_type: str,
    panel_type: str,
    has_skipped_metrics: bool,
) -> None:
    """Fill in TODO placeholder defaults for incomplete panels so the YAML is still valid."""
    default_metric: dict[str, Any]
    default_dim: dict[str, Any]

    if panel_type == 'lens':
        if has_skipped_metrics:
            default_metric = {'aggregation': 'sum', 'field': 'TODO_unsupported_metric_field', 'label': 'TODO_unsupported_metric'}
        else:
            default_metric = {'aggregation': 'count'}
        default_dim = {'type': 'values', 'field': 'TODO_field'}
        if 'data_view' not in chart:
            chart['data_view'] = 'TODO_data_view'
    else:
        default_metric = {'field': 'TODO_metric_field'}
        default_dim = {'field': 'TODO_dimension_field'}

    is_xy = chart_type in _XY_CHART_TYPES
    is_partition = chart_type in _PARTITION_TYPES

    if chart_type == 'metric' and 'primary' not in chart:
        chart['primary'] = default_metric
    if is_xy and 'metrics' not in chart:
        chart['metrics'] = [default_metric]
    if is_partition:
        if chart_type != 'treemap' and 'metrics' not in chart:
            chart['metrics'] = [default_metric]
        if 'breakdowns' not in chart:
            chart['breakdowns'] = [default_dim]
    if chart_type == 'datatable' and 'metrics' not in chart and 'breakdowns' not in chart:
        chart['metrics'] = [default_metric]
    if chart_type == 'heatmap':
        if 'x_axis' not in chart:
            chart['x_axis'] = default_dim
        if 'metric' not in chart:
            chart['metric'] = default_metric
    if chart_type in _SINGULAR_METRIC_TYPES and 'metric' not in chart:
        chart['metric'] = default_metric
    if chart_type in _SINGULAR_DIM_TYPES:
        if chart_type == 'metric':
            pass  # breakdown is optional for metric
        elif chart_type == 'waffle':
            if 'breakdown' not in chart:
                chart['breakdown'] = default_dim
        elif 'dimension' not in chart:
            chart['dimension'] = default_dim


# ---------------------------------------------------------------------------
# Panel inference
# ---------------------------------------------------------------------------


def _infer_lens_chart(panel_dict: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Build (panel_type_key, chart_config) from a raw Lens/ES|QL panel dict.

    Returns the inferred panel type key ('lens' or 'esql') alongside the chart
    config dict, since a raw ``type='lens'`` panel may contain an ES|QL chart
    when its visualization state uses textBased datasource layers.
    """
    inferred = _build_inferred_lens_panel(panel_dict)
    chart: dict[str, Any] = {}
    vis_state = inferred.visualization_state

    # Resolve chart type
    chart_type: str | None = None
    if vis_state is not None:
        chart_type = _resolve_chart_type(vis_state)
        if chart_type is not None:
            chart['type'] = chart_type
            mode = _resolve_stacking_mode(vis_state, chart_type)
            if mode is not None:
                chart['mode'] = mode
            # Donut detection
            if chart_type == 'pie' and vis_state.shape == 'donut':
                chart.setdefault('appearance', {})['donut'] = 'medium'
    if chart_type is None:
        chart_type = 'metric'
        chart['type'] = chart_type

    # Extract legend and appearance from visualization state
    if vis_state is not None:
        vis_raw = vis_state.raw

        # Legend extraction
        if chart_type in _XY_CHART_TYPES:
            legend = _extract_xy_legend(vis_raw)
        elif chart_type in PARTITION_CHART_TYPES:
            legend = _extract_partition_legend(vis_raw)
        else:
            legend = None
        if legend is not None:
            chart['legend'] = legend

        # XY appearance extraction
        if chart_type in _XY_CHART_TYPES:
            _merge_appearance(chart, _extract_xy_appearance(vis_raw, chart_type))

        # Gauge appearance + titles_and_text
        elif chart_type == 'gauge':
            gauge_appearance, gauge_titles = _extract_gauge_settings(vis_raw)
            _merge_appearance(chart, gauge_appearance)
            if gauge_titles is not None:
                chart['titles_and_text'] = gauge_titles

        # Partition chart appearance (pie/treemap/waffle/mosaic)
        elif chart_type in PARTITION_CHART_TYPES:
            _merge_appearance(chart, _extract_partition_appearance(vis_raw, chart_type))

        # Datatable sorting / paging / appearance
        elif chart_type == 'datatable':
            dt_sorting, dt_paging, dt_appearance = _extract_datatable_options(vis_raw)
            if dt_sorting is not None:
                chart['sorting'] = dt_sorting
            if dt_paging is not None:
                chart['paging'] = dt_paging
            if dt_appearance is not None:
                chart['appearance'] = dt_appearance

    # Data view / query
    if inferred.panel_type == 'lens' and inferred.data_view_id is not None:
        chart['data_view'] = inferred.data_view_id

    esql_query: str | None = None
    if inferred.panel_type == 'esql':
        # Check top-level query first, then layer queries
        esql_query = inferred.esql_query
        if esql_query is None:
            for layer in inferred.esql_layers.values():
                esql_query = layer.query
                break
        chart['query'] = esql_query if esql_query is not None else 'TODO_esql_query'

    # Extract metrics/dimensions/breakdowns
    all_metrics: list[dict[str, Any]] = []
    all_dimensions: list[dict[str, Any]] = []
    all_breakdowns: list[dict[str, Any]] = []
    has_skipped_metrics = False

    if inferred.panel_type == 'esql':
        for layer_id, layer in inferred.esql_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b = _classify_esql_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
    else:
        for layer_id, layer in inferred.form_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b, skipped = _classify_form_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
            if skipped:
                has_skipped_metrics = True

    _assign_metrics_and_dimensions(chart, chart_type, all_metrics, all_dimensions, all_breakdowns)
    _fill_required_defaults(chart, chart_type, inferred.panel_type, has_skipped_metrics)

    try:
        _ = _lens_panel_adapter.validate_python(chart) if inferred.panel_type == 'lens' else _esql_panel_adapter.validate_python(chart)
    except ValidationError as exc:
        msg = f'infer_lens_chart produced invalid chart dict (type={chart_type}): {exc}'
        raise ValueError(msg) from exc

    return inferred.panel_type, chart
