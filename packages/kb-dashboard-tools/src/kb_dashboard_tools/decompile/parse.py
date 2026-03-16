"""Phase 1: Parse raw Kibana dashboard JSON into typed intermediate structures.

Handles stringified-vs-already-parsed JSON fields and provides graceful
fallback when panel parsing fails.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, cast

from kb_dashboard_core.controls.view import (
    KbnESQLControl,
    KbnOptionsListControl,
    KbnRangeSliderControl,
    KbnTimeSliderControl,
)
from kb_dashboard_core.dashboard.view import KbnDashboardOptions
from kb_dashboard_core.filters.view import KbnFilter
from kb_dashboard_core.panels.charts.datatable.view import KbnDatatableVisualizationState
from kb_dashboard_core.panels.charts.gauge.view import KbnGaugeVisualizationState
from kb_dashboard_core.panels.charts.heatmap.view import KbnHeatmapVisualizationState
from kb_dashboard_core.panels.charts.metric.view import KbnESQLMetricVisualizationState, KbnMetricVisualizationState
from kb_dashboard_core.panels.charts.mosaic.view import KbnMosaicVisualizationState
from kb_dashboard_core.panels.charts.pie.view import KbnPieVisualizationState
from kb_dashboard_core.panels.charts.tagcloud.view import KbnTagcloudVisualizationState
from kb_dashboard_core.panels.charts.waffle.view import KbnWaffleVisualizationState
from kb_dashboard_core.panels.charts.xy.view import KbnXYVisualizationState
from kb_dashboard_core.panels.images.view import KbnImagePanel
from kb_dashboard_core.panels.links.view import KbnLinksPanel
from kb_dashboard_core.panels.markdown.view import KbnMarkdownPanel
from kb_dashboard_core.panels.search.view import KbnSearchPanel
from kb_dashboard_core.panels.vega.view import KbnVegaPanel
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def parse_json_field(raw: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a field that may be a JSON string or already-parsed object."""
    if raw is None:
        return None
    if isinstance(raw, str):
        parsed: dict[str, Any] | list[Any] = json.loads(raw)  # pyright: ignore[reportAny]
        return parsed
    return raw


def as_dict(value: object) -> dict[str, Any] | None:
    """Safely cast a value to dict if it is one, otherwise return None."""
    if isinstance(value, dict):
        return value  # pyright: ignore[reportUnknownVariableType]
    return None


def _validate_view_model(model_cls: type[Any], data: object) -> object | None:
    """Best-effort validation into an existing Kbn* view model."""
    try:
        return model_cls.model_validate(  # pyright: ignore[reportAny]
            data,
            strict=False,
            extra='ignore',
        )
    except ValidationError:
        return None


VISUALIZATION_VIEW_MODEL_MAP: dict[str, type[Any]] = {
    'lnsXY': KbnXYVisualizationState,
    'lnsGauge': KbnGaugeVisualizationState,
    'lnsHeatmap': KbnHeatmapVisualizationState,
    'lnsDatatable': KbnDatatableVisualizationState,
    'lnsTagcloud': KbnTagcloudVisualizationState,
}

SIMPLE_PANEL_VIEW_MODEL_MAP: dict[str, type[Any]] = {
    'search': KbnSearchPanel,
    'links': KbnLinksPanel,
    'image': KbnImagePanel,
    'vega': KbnVegaPanel,
    'markdown': KbnMarkdownPanel,
}


def _visualization_model_type(visualization_type: str | None, visualization: dict[str, Any], *, is_esql: bool) -> type[Any] | None:
    if visualization_type == 'lnsMetric':
        return KbnESQLMetricVisualizationState if is_esql else KbnMetricVisualizationState
    if visualization_type == 'lnsPie':
        shape = visualization.get('shape')
        if shape == 'mosaic':
            return KbnMosaicVisualizationState
        if shape == 'waffle':
            return KbnWaffleVisualizationState
        return KbnPieVisualizationState
    return VISUALIZATION_VIEW_MODEL_MAP.get(visualization_type or '')


def _saved_visualization_panel_type(panel: dict[str, Any]) -> str | None:
    embeddable_config = as_dict(panel.get('embeddableConfig')) or {}
    saved_vis = as_dict(embeddable_config.get('savedVis')) or {}
    saved_vis_type = saved_vis.get('type')
    return saved_vis_type if isinstance(saved_vis_type, str) else None


def _normalize_filter_for_view(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw Kibana filter JSON into the field names used by KbnFilter."""
    normalized = dict(raw)
    state = cast('object', normalized.pop('$state', None))
    if 'state' not in normalized and isinstance(state, dict):
        normalized['state'] = state
    return normalized


def _normalize_control_for_view(panel_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Fill Kibana defaulted control fields so Kbn* view validation can succeed."""
    normalized = dict(raw)
    panel_type = normalized.get('type')
    normalized.setdefault('grow', False)
    normalized.setdefault('width', 'medium')

    explicit_input = as_dict(normalized.get('explicitInput')) or {}
    normalized_explicit = dict(explicit_input)
    normalized_explicit.setdefault('id', panel_id)

    if panel_type == 'optionsListControl':
        normalized_explicit.setdefault('searchTechnique', 'prefix')
        normalized_explicit.setdefault('selectedOptions', [])
        normalized_explicit.setdefault('singleSelect', False)
        normalized_explicit.setdefault('sort', {'by': '_count', 'direction': 'desc'})
        normalized_explicit.setdefault('runPastTimeout', False)
    elif panel_type == 'rangeSliderControl':
        _ = normalized_explicit.setdefault('step', None)
    elif panel_type == 'esqlControl':
        normalized_explicit.setdefault('selectedOptions', [])

    if normalized_explicit:
        normalized['explicitInput'] = normalized_explicit
    return normalized


# ---------------------------------------------------------------------------
# Parsed intermediate structures
# ---------------------------------------------------------------------------


@dataclass
class ParsedReference:
    """A resolved reference from the dashboard references array."""

    name: str
    ref_type: str
    ref_id: str


@dataclass
class ParsedGridData:
    """Parsed panel grid layout."""

    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None
    section_id: str | None = None


@dataclass
class ParsedColumn:
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
class ParsedESQLColumn:
    """A single parsed ES|QL column."""

    column_id: str
    field_name: str
    label: str | None = None
    custom_label: bool = False
    meta_type: str | None = None


@dataclass
class ParsedFormLayer:
    """A parsed form-based datasource layer."""

    layer_id: str
    columns: dict[str, ParsedColumn] = field(default_factory=dict)
    column_order: list[str] = field(default_factory=list)
    index_pattern_id: str | None = None


@dataclass
class ParsedESQLLayer:
    """A parsed ES|QL datasource layer."""

    layer_id: str
    query: str
    columns: list[ParsedESQLColumn] = field(default_factory=list)
    time_field: str = '@timestamp'


@dataclass
class ParsedVisualizationLayerRole:
    """Accessor roles for a single visualization layer."""

    layer_id: str
    metric_ids: list[str] = field(default_factory=list)
    dimension_id: str | None = None
    breakdown_id: str | None = None
    accessors: list[str] = field(default_factory=list)


@dataclass
class ParsedVisualizationState:
    """Parsed visualization state with resolved chart type."""

    raw_type: str | None = None
    preferred_series_type: str | None = None
    shape: str | None = None
    layer_roles: dict[str, ParsedVisualizationLayerRole] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    view_model: object | None = None


@dataclass
class ParsedLensPanel:
    """A fully parsed Lens/ES|QL panel ready for inference."""

    panel_type: str  # 'lens' or 'esql'
    visualization_type: str | None = None
    visualization_state: ParsedVisualizationState | None = None
    form_layers: dict[str, ParsedFormLayer] = field(default_factory=dict)
    esql_layers: dict[str, ParsedESQLLayer] = field(default_factory=dict)
    data_view_id: str | None = None
    esql_query: str | None = None
    references: list[ParsedReference] = field(default_factory=list)
    view_visualization: object | None = None


@dataclass
class ParsedSimplePanel:
    """A parsed non-chart panel (markdown, search, links, image, vega)."""

    panel_type: str
    raw: dict[str, Any] = field(default_factory=dict)
    embeddable_config: dict[str, Any] = field(default_factory=dict)
    embeddable_attributes: dict[str, Any] = field(default_factory=dict)
    view_panel: object | None = None


@dataclass
class ParsedPanel:
    """Wrapper around all parsed panel types."""

    panel_index: str | None = None
    title: str = ''
    grid: ParsedGridData | None = None
    hide_title: bool | None = None
    description: str | None = None

    lens: ParsedLensPanel | None = None
    simple: ParsedSimplePanel | None = None
    error: str | None = None


@dataclass
class ParsedDashboardSettings:
    """Parsed dashboard-level settings."""

    margins: bool | None = None
    sync_colors: bool | None = None
    sync_cursor: bool | None = None
    sync_tooltips: bool | None = None
    hide_panel_titles: bool | None = None
    view_options: KbnDashboardOptions | None = None


@dataclass
class ParsedFilter:
    """A parsed dashboard-level filter."""

    raw: dict[str, Any]
    meta: dict[str, Any]
    key: str
    filter_type: str | None = None
    view_filter: KbnFilter | None = None


@dataclass
class ParsedControl:
    """A parsed dashboard control."""

    raw: dict[str, Any]
    control_type: str | None = None
    field_name: str | None = None
    title: str | None = None
    data_view_id: str | None = None
    view_control: object | None = None


@dataclass
class ParsedDashboard:
    """Top-level parsed dashboard."""

    dashboard_id: str | None = None
    title: str = 'Untitled Dashboard'
    description: str | None = None
    time_from: str | None = None
    time_to: str | None = None
    settings: ParsedDashboardSettings | None = None
    query: dict[str, str] | None = None
    filters: list[ParsedFilter] = field(default_factory=list)
    controls: list[ParsedControl] = field(default_factory=list)
    panels: list[ParsedPanel] = field(default_factory=list)
    reference_lookup: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_grid_data(raw: dict[str, Any]) -> ParsedGridData:
    grid = ParsedGridData()
    x = raw.get('x')
    y = raw.get('y')
    w = raw.get('w')
    h = raw.get('h')
    if isinstance(x, int):
        grid.x = x
    if isinstance(y, int):
        grid.y = y
    if isinstance(w, int):
        grid.w = w
    if isinstance(h, int):
        grid.h = h
    section_id = raw.get('sectionId')
    if isinstance(section_id, str):
        grid.section_id = section_id
    return grid


def _parse_panel_title(panel: dict[str, Any]) -> str:
    direct_title = panel.get('title')
    if isinstance(direct_title, str):
        return direct_title
    embeddable_config = as_dict(panel.get('embeddableConfig'))
    if embeddable_config is not None:
        embedded_title = embeddable_config.get('title')
        if isinstance(embedded_title, str):
            return embedded_title
    return ''


def _parse_column(col_id: str, col: dict[str, Any]) -> ParsedColumn:
    op_type = col.get('operationType')
    parsed = ParsedColumn(
        column_id=col_id,
        operation_type=op_type if isinstance(op_type, str) else 'unknown',
        is_bucketed=bool(col.get('isBucketed')),
        data_type=col.get('dataType') if isinstance(col.get('dataType'), str) else None,
    )
    source_field = col.get('sourceField')
    if isinstance(source_field, str):
        parsed.source_field = source_field
    label = col.get('label')
    if isinstance(label, str):
        parsed.label = label
    parsed.custom_label = bool(col.get('customLabel'))
    params = as_dict(col.get('params'))
    if params is not None:
        parsed.params = params

    col_filter = as_dict(col.get('filter'))
    if col_filter is not None:
        q = col_filter.get('query')
        lang = col_filter.get('language')
        if isinstance(q, str):
            parsed.filter_query = q
            parsed.filter_language = lang if isinstance(lang, str) else None
    return parsed


def _parse_esql_column(raw: dict[str, Any]) -> ParsedESQLColumn | None:
    col_id = raw.get('columnId')
    field_name = raw.get('fieldName')
    if not isinstance(col_id, str) or not isinstance(field_name, str):
        return None
    parsed = ParsedESQLColumn(column_id=col_id, field_name=field_name)
    label = raw.get('label')
    if isinstance(label, str):
        parsed.label = label
    parsed.custom_label = bool(raw.get('customLabel'))
    meta = as_dict(raw.get('meta'))
    if meta is not None:
        mt = meta.get('type')
        if isinstance(mt, str):
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
        value = source.get(key)
        if isinstance(value, str):
            ids.append(value)
    list_accessors = source.get('accessors')
    if isinstance(list_accessors, list):
        ids.extend([a for a in list_accessors if isinstance(a, str)])  # pyright: ignore[reportUnknownVariableType]
    return _dedupe_ids(ids)


def _parse_visualization_view_model(
    visualization_type: str | None,
    visualization: dict[str, Any],
    *,
    is_esql: bool,
) -> object | None:
    model_cls = _visualization_model_type(visualization_type, visualization, is_esql=is_esql)
    if model_cls is None:
        return None
    return _validate_view_model(model_cls, visualization)


def _parse_visualization_state(embeddable_attributes: dict[str, Any], *, is_esql: bool) -> ParsedVisualizationState:
    state_raw = as_dict(embeddable_attributes.get('state'))
    vis_type = embeddable_attributes.get('visualizationType')
    parsed = ParsedVisualizationState(
        raw_type=vis_type if isinstance(vis_type, str) else None,
    )
    if state_raw is None:
        return parsed

    visualization = as_dict(state_raw.get('visualization'))
    if visualization is None:
        return parsed

    parsed.raw = visualization
    parsed.view_model = _parse_visualization_view_model(parsed.raw_type, visualization, is_esql=is_esql)
    parsed.preferred_series_type = (
        visualization.get('preferredSeriesType') if isinstance(visualization.get('preferredSeriesType'), str) else None
    )
    parsed.shape = visualization.get('shape') if isinstance(visualization.get('shape'), str) else None

    # Multi-layer roles (XY charts, reference lines)
    vis_layers = visualization.get('layers')
    if isinstance(vis_layers, list):
        for vis_layer_item in vis_layers:  # pyright: ignore[reportUnknownVariableType]
            vis_layer = as_dict(vis_layer_item)  # pyright: ignore[reportUnknownArgumentType]
            if vis_layer is None:
                continue
            layer_id = vis_layer.get('layerId')
            if not isinstance(layer_id, str):
                continue
            role = ParsedVisualizationLayerRole(layer_id=layer_id)
            metric_ids = vis_layer.get('accessors')
            if isinstance(metric_ids, list):
                role.metric_ids = [v for v in metric_ids if isinstance(v, str)]  # pyright: ignore[reportUnknownVariableType]
            x_accessor = vis_layer.get('xAccessor')
            if isinstance(x_accessor, str):
                role.dimension_id = x_accessor
            split_accessor = vis_layer.get('splitAccessor')
            if isinstance(split_accessor, str):
                role.breakdown_id = split_accessor
            role.accessors = _collect_accessor_ids(vis_layer, ('xAccessor', 'splitAccessor'))
            parsed.layer_roles[layer_id] = role

    # Single-layer roles (metric, gauge, pie, heatmap, etc.)
    single_layer_id = visualization.get('layerId')
    if isinstance(single_layer_id, str):
        role = parsed.layer_roles.setdefault(single_layer_id, ParsedVisualizationLayerRole(layer_id=single_layer_id))
        for key in ('metricAccessor', 'secondaryAccessor', 'accessor'):
            value = visualization.get(key)
            if isinstance(value, str) and value not in role.metric_ids:
                role.metric_ids.append(value)
        list_accessors = visualization.get('accessors')
        if isinstance(list_accessors, list):
            for v in list_accessors:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(v, str) and v not in role.metric_ids:
                    role.metric_ids.append(v)
        x_accessor = visualization.get('xAccessor')
        if isinstance(x_accessor, str):
            role.dimension_id = x_accessor
        split_accessor = visualization.get('splitAccessor')
        if isinstance(split_accessor, str):
            role.breakdown_id = split_accessor
        if not role.accessors:
            role.accessors = _collect_accessor_ids(
                visualization,
                ('xAccessor', 'metricAccessor', 'splitAccessor', 'secondaryAccessor', 'accessor'),
            )

    return parsed


def _parse_form_based_layers(state: dict[str, Any]) -> dict[str, ParsedFormLayer]:
    ds_states = as_dict(state.get('datasourceStates'))
    if ds_states is None:
        return {}
    form_based = as_dict(ds_states.get('formBased'))
    if form_based is None:
        return {}
    layers_raw = as_dict(form_based.get('layers'))
    if layers_raw is None:
        return {}

    layers: dict[str, ParsedFormLayer] = {}
    for layer_id, layer_value in layers_raw.items():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        parsed_layer = ParsedFormLayer(
            layer_id=layer_id,
            index_pattern_id=layer.get('indexPatternId') if isinstance(layer.get('indexPatternId'), str) else None,
        )
        column_order = layer.get('columnOrder')
        if isinstance(column_order, list):
            parsed_layer.column_order = [c for c in column_order if isinstance(c, str)]  # pyright: ignore[reportUnknownVariableType]

        columns_raw = as_dict(layer.get('columns'))
        if columns_raw is not None:
            for col_id, col_value in columns_raw.items():  # pyright: ignore[reportAny]
                col = as_dict(col_value)  # pyright: ignore[reportAny]
                if col is not None:
                    parsed_layer.columns[col_id] = _parse_column(col_id, col)
        layers[layer_id] = parsed_layer
    return layers


def _parse_esql_layers(state: dict[str, Any]) -> dict[str, ParsedESQLLayer]:
    ds_states = as_dict(state.get('datasourceStates'))
    if ds_states is None:
        return {}
    text_based = as_dict(ds_states.get('textBased'))
    if text_based is None:
        return {}
    layers_raw = as_dict(text_based.get('layers'))
    if layers_raw is None:
        return {}

    # Fall back to top-level query if layer doesn't have its own
    top_esql = _extract_esql_query_from_state(state)

    layers: dict[str, ParsedESQLLayer] = {}
    for layer_id, layer_value in layers_raw.items():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query_obj = as_dict(layer.get('query'))
        esql = query_obj.get('esql') if query_obj is not None else None
        if not isinstance(esql, str):
            esql = top_esql
        if not isinstance(esql, str):
            continue
        parsed_layer = ParsedESQLLayer(layer_id=layer_id, query=esql)
        time_field = layer.get('timeField')
        if isinstance(time_field, str):
            parsed_layer.time_field = time_field

        for col_list_key in ('columns', 'allColumns'):
            col_list = layer.get(col_list_key)
            if isinstance(col_list, list):
                for raw_col in col_list:  # pyright: ignore[reportUnknownVariableType]
                    col = as_dict(raw_col)  # pyright: ignore[reportUnknownArgumentType]
                    if col is not None:
                        parsed = _parse_esql_column(col)
                        if parsed is not None:
                            existing_ids = {c.column_id for c in parsed_layer.columns}
                            if parsed.column_id not in existing_ids:
                                parsed_layer.columns.append(parsed)
        layers[layer_id] = parsed_layer
    return layers


def _has_text_based_query(state: dict[str, Any]) -> bool:
    top_query = as_dict(state.get('query'))
    if top_query is not None and isinstance(top_query.get('esql'), str):
        return True
    ds_states = as_dict(state.get('datasourceStates'))
    if ds_states is None:
        return False
    text_based = as_dict(ds_states.get('textBased'))
    if text_based is None:
        return False
    layers_raw = as_dict(text_based.get('layers'))
    if layers_raw is None:
        return False
    for layer_value in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = as_dict(layer.get('query'))
        if query is not None and isinstance(query.get('esql'), str):
            return True
    return False


def _extract_esql_query_from_state(state: dict[str, Any]) -> str | None:
    top_query = as_dict(state.get('query'))
    if top_query is not None:
        esql = top_query.get('esql')
        if isinstance(esql, str):
            return esql
    ds_states = as_dict(state.get('datasourceStates'))
    if ds_states is None:
        return None
    text_based = as_dict(ds_states.get('textBased'))
    if text_based is None:
        return None
    layers_raw = as_dict(text_based.get('layers'))
    if layers_raw is None:
        return None
    for layer_value in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = as_dict(layer.get('query'))
        if query is not None:
            esql = query.get('esql')
            if isinstance(esql, str):
                return esql
    return None


def _extract_data_view_from_refs(refs: list[object]) -> str | None:
    for ref_item in refs:
        ref = as_dict(ref_item)
        if ref is None:
            continue
        if ref.get('type') == 'index-pattern' and isinstance(ref.get('id'), str):
            return ref['id']  # pyright: ignore[reportAny]
    return None


def _parse_lens_panel(panel: dict[str, Any], raw_panel_type: str) -> ParsedLensPanel:
    embeddable_config = as_dict(panel.get('embeddableConfig')) or {}
    embeddable_attributes = as_dict(embeddable_config.get('attributes')) or {}

    state = as_dict(embeddable_attributes.get('state')) or {}
    is_esql = raw_panel_type == 'esql' or _has_text_based_query(state)
    panel_type = 'esql' if is_esql else 'lens'

    vis_state = _parse_visualization_state(embeddable_attributes, is_esql=is_esql)

    # Parse datasource layers
    form_layers = _parse_form_based_layers(state) if not is_esql else {}
    esql_layers = _parse_esql_layers(state) if is_esql else {}

    # Extract top-level ES|QL query
    esql_query = _extract_esql_query_from_state(state) if is_esql else None

    # Extract data view from references
    refs_raw = embeddable_attributes.get('references')
    if not isinstance(refs_raw, list):
        refs_raw = embeddable_config.get('references')
    refs = cast('list[object]', refs_raw) if isinstance(refs_raw, list) else []
    data_view = _extract_data_view_from_refs(refs)

    parsed_refs: list[ParsedReference] = []
    for ref_item in refs:
        ref = as_dict(ref_item)
        if ref is None:
            continue
        name = ref.get('name')
        ref_type = ref.get('type')
        ref_id = ref.get('id')
        if isinstance(name, str) and isinstance(ref_type, str) and isinstance(ref_id, str):
            parsed_refs.append(ParsedReference(name=name, ref_type=ref_type, ref_id=ref_id))

    return ParsedLensPanel(
        panel_type=panel_type,
        visualization_type=vis_state.raw_type,
        visualization_state=vis_state,
        form_layers=form_layers,
        esql_layers=esql_layers,
        data_view_id=data_view,
        esql_query=esql_query,
        references=parsed_refs,
        view_visualization=vis_state.view_model,
    )


def _parse_simple_panel_view(panel: dict[str, Any], panel_type: str) -> object | None:
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(panel_type)
    if model_cls is not None:
        return _validate_view_model(model_cls, panel)
    if panel_type != 'visualization':
        return None
    saved_vis_type = _saved_visualization_panel_type(panel)
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(saved_vis_type or '')
    if model_cls is None:
        return None
    return _validate_view_model(model_cls, panel)


def _parse_simple_panel(panel: dict[str, Any], panel_type: str) -> ParsedSimplePanel:
    embeddable_config = as_dict(panel.get('embeddableConfig')) or {}
    embeddable_attributes = as_dict(embeddable_config.get('attributes')) or {}
    resolved_panel_type = _saved_visualization_panel_type(panel) if panel_type == 'visualization' else panel_type
    return ParsedSimplePanel(
        panel_type=resolved_panel_type or panel_type,
        raw=panel,
        embeddable_config=embeddable_config,
        embeddable_attributes=embeddable_attributes,
        view_panel=_parse_simple_panel_view(panel, panel_type),
    )


def _parse_panel(panel: dict[str, Any]) -> ParsedPanel:
    parsed = ParsedPanel()

    panel_index = panel.get('panelIndex')
    if isinstance(panel_index, str):
        parsed.panel_index = panel_index

    parsed.title = _parse_panel_title(panel)

    grid_raw = as_dict(panel.get('gridData'))
    if grid_raw is not None:
        parsed.grid = _parse_grid_data(grid_raw)

    panel_type = panel.get('type')
    if not isinstance(panel_type, str):
        parsed.error = 'missing panel type'
        return parsed

    if panel_type in {'lens', 'esql'}:
        try:
            parsed.lens = _parse_lens_panel(panel, panel_type)
        except Exception as exc:
            logger.warning('Failed to parse lens panel %s: %s', parsed.panel_index, exc)
            parsed.error = f'parse error: {exc}'
    elif panel_type in {'markdown', 'search', 'links', 'image', 'vega', 'visualization', 'map'}:
        parsed.simple = _parse_simple_panel(panel, panel_type)
    else:
        parsed.simple = _parse_simple_panel(panel, panel_type)

    return parsed


# ---------------------------------------------------------------------------
# Dashboard-level parsing
# ---------------------------------------------------------------------------


def _parse_settings(attributes: dict[str, Any]) -> ParsedDashboardSettings | None:
    options = parse_json_field(attributes.get('optionsJSON'))
    if not isinstance(options, dict):
        return None
    return ParsedDashboardSettings(
        margins=options.get('useMargins') if isinstance(options.get('useMargins'), bool) else None,
        sync_colors=options.get('syncColors') if isinstance(options.get('syncColors'), bool) else None,
        sync_cursor=options.get('syncCursor') if isinstance(options.get('syncCursor'), bool) else None,
        sync_tooltips=options.get('syncTooltips') if isinstance(options.get('syncTooltips'), bool) else None,
        hide_panel_titles=options.get('hidePanelTitles') if isinstance(options.get('hidePanelTitles'), bool) else None,
        view_options=cast('KbnDashboardOptions | None', _validate_view_model(KbnDashboardOptions, options)),
    )


def _parse_filters(attributes: dict[str, Any]) -> list[ParsedFilter]:
    meta_raw = as_dict(attributes.get('kibanaSavedObjectMeta'))
    if meta_raw is None:
        return []
    search_source = parse_json_field(meta_raw.get('searchSourceJSON'))
    if not isinstance(search_source, dict):
        return []
    raw_filters = search_source.get('filter')
    if not isinstance(raw_filters, list):
        return []

    result: list[ParsedFilter] = []
    for filter_item in raw_filters:  # pyright: ignore[reportUnknownVariableType]
        raw = as_dict(filter_item)  # pyright: ignore[reportUnknownArgumentType]
        if raw is None:
            continue
        filter_meta = as_dict(raw.get('meta'))
        if filter_meta is None:
            continue
        key = filter_meta.get('key')
        if not isinstance(key, str):
            continue
        result.append(
            ParsedFilter(
                raw=raw,
                meta=filter_meta,
                key=key,
                filter_type=filter_meta.get('type') if isinstance(filter_meta.get('type'), str) else None,
                view_filter=cast('KbnFilter | None', _validate_view_model(KbnFilter, _normalize_filter_for_view(raw))),
            )
        )
    return result


def _parse_dashboard_query(attributes: dict[str, Any]) -> dict[str, str] | None:
    query_dict: dict[str, str] | None = None
    meta_raw = as_dict(attributes.get('kibanaSavedObjectMeta'))
    if meta_raw is not None:
        search_source = parse_json_field(meta_raw.get('searchSourceJSON'))
        if isinstance(search_source, dict):
            raw_query = as_dict(search_source.get('query'))
            if raw_query is not None:
                language = raw_query.get('language')
                query = raw_query.get('query')
                if isinstance(query, str):
                    if language == 'kuery':
                        query_dict = {'kql': query}
                    elif language == 'lucene':
                        query_dict = {'lucene': query}
    return query_dict


def _parse_controls(attributes: dict[str, Any], reference_lookup: dict[str, str]) -> list[ParsedControl]:
    control_group = as_dict(attributes.get('controlGroupInput'))
    if control_group is None:
        return []
    panels_json = parse_json_field(control_group.get('panelsJSON'))
    if not isinstance(panels_json, dict):
        return []

    def _order(item: tuple[str, object]) -> int:
        panel = as_dict(item[1])
        if panel is None:
            return 0
        order = panel.get('order', 0)  # pyright: ignore[reportAny]
        return order if isinstance(order, int) else 0

    result: list[ParsedControl] = []
    for panel_id, panel_value in sorted(panels_json.items(), key=_order):  # pyright: ignore[reportAny]
        panel = as_dict(panel_value)  # pyright: ignore[reportAny]
        if panel is None:
            continue
        explicit_input = as_dict(panel.get('explicitInput'))
        ctrl = ParsedControl(raw=panel, control_type=panel.get('type') if isinstance(panel.get('type'), str) else None)
        if explicit_input is not None:
            fn = explicit_input.get('fieldName')
            if isinstance(fn, str):
                ctrl.field_name = fn
            title = explicit_input.get('title')
            if isinstance(title, str):
                ctrl.title = title
            dv = explicit_input.get('dataViewId')
            if isinstance(dv, str):
                ctrl.data_view_id = dv
            else:
                ref_suffix = {
                    'optionsListControl': 'optionsListDataView',
                    'rangeSliderControl': 'rangeSliderDataView',
                    'timeSliderControl': 'timeSliderDataView',
                    'esqlControl': 'esqlControlDataView',
                }.get(ctrl.control_type or '')
                if ref_suffix is not None:
                    ref_name = f'controlGroup_{panel_id}:{ref_suffix}'
                    resolved = reference_lookup.get(ref_name)
                    if isinstance(resolved, str):
                        ctrl.data_view_id = resolved
                    else:
                        attr_ref = attributes.get(ref_name)
                        if isinstance(attr_ref, str):
                            ctrl.data_view_id = attr_ref
        normalized_panel = _normalize_control_for_view(panel_id, panel)
        normalized_explicit = as_dict(normalized_panel.get('explicitInput'))
        if normalized_explicit is not None and ctrl.data_view_id is not None and 'dataViewId' not in normalized_explicit:
            normalized_explicit = dict(normalized_explicit)
            normalized_explicit['dataViewId'] = ctrl.data_view_id
            normalized_panel['explicitInput'] = normalized_explicit
        if ctrl.control_type == 'optionsListControl':
            ctrl.view_control = _validate_view_model(KbnOptionsListControl, normalized_panel)
        elif ctrl.control_type == 'rangeSliderControl':
            ctrl.view_control = _validate_view_model(KbnRangeSliderControl, normalized_panel)
        elif ctrl.control_type == 'timeSliderControl':
            ctrl.view_control = _validate_view_model(KbnTimeSliderControl, normalized_panel)
        elif ctrl.control_type == 'esqlControl':
            ctrl.view_control = _validate_view_model(KbnESQLControl, normalized_panel)
        result.append(ctrl)
    return result


def _extract_reference_lookup(dashboard: dict[str, Any]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    references = dashboard.get('references')
    if not isinstance(references, list):
        return lookup
    for ref_item in references:  # pyright: ignore[reportUnknownVariableType]
        ref = as_dict(ref_item)  # pyright: ignore[reportUnknownArgumentType]
        if ref is None:
            continue
        name = ref.get('name')
        target_id = ref.get('id')
        if isinstance(name, str) and isinstance(target_id, str):
            lookup[name] = target_id
    return lookup


def parse_dashboard(dashboard: dict[str, Any]) -> ParsedDashboard:
    """Parse a raw Kibana dashboard JSON dict into a typed intermediate structure."""
    attributes = as_dict(dashboard.get('attributes')) or {}
    reference_lookup = _extract_reference_lookup(dashboard)

    title = attributes.get('title')
    description = attributes.get('description')

    parsed = ParsedDashboard(
        dashboard_id=dashboard.get('id') if isinstance(dashboard.get('id'), str) else None,
        title=title if isinstance(title, str) else 'Untitled Dashboard',
        description=description if isinstance(description, str) else None,
        time_from=attributes.get('timeFrom') if isinstance(attributes.get('timeFrom'), str) else None,
        time_to=attributes.get('timeTo') if isinstance(attributes.get('timeTo'), str) else None,
        settings=_parse_settings(attributes),
        query=_parse_dashboard_query(attributes),
        filters=_parse_filters(attributes),
        controls=_parse_controls(attributes, reference_lookup),
        reference_lookup=reference_lookup,
    )

    panels_json = parse_json_field(attributes.get('panelsJSON'))
    if isinstance(panels_json, list):
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is not None:
                parsed.panels.append(_parse_panel(panel))

    return parsed
