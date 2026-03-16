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

from .raw_models import (
    RawDashboard,
    RawDashboardAttributes,
    RawEmbeddableAttributes,
    RawEmbeddableConfig,
    RawGridData,
    RawPanel,
    RawReference,
    RawState,
)

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


def as_list(value: object) -> list[object] | None:
    """Safely cast a value to list if it is one, otherwise return None."""
    if isinstance(value, list):
        return cast('list[object]', value)
    return None


def get_dict(source: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Extract a dict-valued key from a dict source."""
    return as_dict(source.get(key))


def get_list(source: dict[str, Any], key: str) -> list[object] | None:
    """Extract a list-valued key from a dict source."""
    return as_list(source.get(key))


def get_str(source: dict[str, Any], key: str) -> str | None:
    """Extract a string-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, str) else None


def get_int(source: dict[str, Any], key: str) -> int | None:
    """Extract an int-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, int) else None


def get_bool(source: dict[str, Any], key: str) -> bool | None:
    """Extract a bool-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, bool) else None


def get_dict_path(source: dict[str, Any], *path: str) -> dict[str, Any] | None:
    """Walk nested dict keys and return the final dict, or None if any segment is missing."""
    current: dict[str, Any] = source
    for key in path:
        next_value = as_dict(current.get(key))
        if next_value is None:
            return None
        current = next_value
    return current


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


def _saved_visualization_panel_type(panel: RawPanel) -> str | None:
    embeddable_config = panel.embeddable_config
    if embeddable_config is None or embeddable_config.saved_vis is None:
        return None
    return embeddable_config.saved_vis.type


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

    explicit_input = get_dict(normalized, 'explicitInput') or {}
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


def _parse_grid_data(raw: RawGridData) -> ParsedGridData:
    return ParsedGridData(
        x=raw.x,
        y=raw.y,
        w=raw.w,
        h=raw.h,
        section_id=raw.section_id,
    )


def _parse_panel_title(panel: RawPanel) -> str:
    if panel.title is not None:
        return panel.title
    if panel.embeddable_config is not None and panel.embeddable_config.title is not None:
        return panel.embeddable_config.title
    if panel.embeddable_config is not None:
        embeddable_config = panel.embeddable_config.model_dump(exclude_none=True, by_alias=True)
        embedded_title = get_str(embeddable_config, 'title')
        if embedded_title is not None:
            return embedded_title
    return ''


def _parse_column(col_id: str, col: dict[str, Any]) -> ParsedColumn:
    op_type = get_str(col, 'operationType')
    data_type = get_str(col, 'dataType')
    parsed = ParsedColumn(
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


def _parse_esql_column(raw: dict[str, Any]) -> ParsedESQLColumn | None:
    col_id = get_str(raw, 'columnId')
    field_name = get_str(raw, 'fieldName')
    if col_id is None or field_name is None:
        return None
    parsed = ParsedESQLColumn(column_id=col_id, field_name=field_name)
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


def _parse_visualization_state(embeddable_attributes: RawEmbeddableAttributes, *, is_esql: bool) -> ParsedVisualizationState:
    state_raw = embeddable_attributes.state
    vis_type = embeddable_attributes.visualization_type
    parsed = ParsedVisualizationState(
        raw_type=vis_type,
    )
    if state_raw is None:
        return parsed

    visualization_model = state_raw.visualization
    if visualization_model is None:
        return parsed
    visualization = visualization_model.model_dump(exclude_none=True, by_alias=True)

    parsed.raw = visualization
    parsed.view_model = _parse_visualization_view_model(parsed.raw_type, visualization, is_esql=is_esql)
    parsed.preferred_series_type = visualization_model.preferred_series_type
    parsed.shape = visualization_model.shape

    # Multi-layer roles (XY charts, reference lines)
    vis_layers = visualization_model.layers
    if vis_layers is not None:
        for vis_layer in vis_layers:
            layer_id = vis_layer.layer_id
            if layer_id is None:
                continue
            vis_layer_dict = vis_layer.model_dump(exclude_none=True, by_alias=True)
            role = ParsedVisualizationLayerRole(layer_id=layer_id)
            metric_ids = vis_layer.accessors
            if metric_ids is not None:
                role.metric_ids = [v for v in metric_ids if isinstance(v, str)]
            x_accessor = vis_layer.x_accessor
            if x_accessor is not None:
                role.dimension_id = x_accessor
            split_accessor = vis_layer.split_accessor
            if split_accessor is not None:
                role.breakdown_id = split_accessor
            role.accessors = _collect_accessor_ids(vis_layer_dict, ('xAccessor', 'splitAccessor'))
            parsed.layer_roles[layer_id] = role

    # Single-layer roles (metric, gauge, pie, heatmap, etc.)
    single_layer_id = visualization_model.layer_id
    if single_layer_id is not None:
        role = parsed.layer_roles.setdefault(single_layer_id, ParsedVisualizationLayerRole(layer_id=single_layer_id))
        for value in (
            visualization_model.metric_accessor,
            visualization_model.secondary_accessor,
            visualization_model.accessor,
        ):
            if value is not None and value not in role.metric_ids:
                role.metric_ids.append(value)
        list_accessors = visualization_model.accessors
        if list_accessors is not None:
            for v in list_accessors:
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

    return parsed


def _parse_form_based_layers(state: dict[str, Any]) -> dict[str, ParsedFormLayer]:
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return {}
    form_based = get_dict(ds_states, 'formBased')
    if form_based is None:
        return {}
    layers_raw = get_dict(form_based, 'layers')
    if layers_raw is None:
        return {}

    layers: dict[str, ParsedFormLayer] = {}
    for layer_id, layer_value in layers_raw.items():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        parsed_layer = ParsedFormLayer(
            layer_id=layer_id,
            index_pattern_id=get_str(layer, 'indexPatternId'),
        )
        column_order = get_list(layer, 'columnOrder')
        if column_order is not None:
            parsed_layer.column_order = [c for c in column_order if isinstance(c, str)]

        columns_raw = get_dict(layer, 'columns')
        if columns_raw is not None:
            for col_id, col_value in columns_raw.items():  # pyright: ignore[reportAny]
                col = as_dict(col_value)  # pyright: ignore[reportAny]
                if col is not None:
                    parsed_layer.columns[col_id] = _parse_column(col_id, col)
        layers[layer_id] = parsed_layer
    return layers


def _parse_esql_layers(state: dict[str, Any]) -> dict[str, ParsedESQLLayer]:
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return {}
    text_based = get_dict(ds_states, 'textBased')
    if text_based is None:
        return {}
    layers_raw = get_dict(text_based, 'layers')
    if layers_raw is None:
        return {}

    # Fall back to top-level query if layer doesn't have its own
    top_esql = _extract_esql_query_from_state(state)

    layers: dict[str, ParsedESQLLayer] = {}
    for layer_id, layer_value in layers_raw.items():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query_obj = get_dict(layer, 'query')
        esql = get_str(query_obj, 'esql') if query_obj is not None else None
        if esql is None:
            esql = top_esql
        if esql is None:
            continue
        parsed_layer = ParsedESQLLayer(layer_id=layer_id, query=esql)
        time_field = get_str(layer, 'timeField')
        if time_field is not None:
            parsed_layer.time_field = time_field

        for col_list_key in ('columns', 'allColumns'):
            col_list = get_list(layer, col_list_key)
            if col_list is not None:
                for raw_col in col_list:
                    col = as_dict(raw_col)
                    if col is not None:
                        parsed = _parse_esql_column(col)
                        if parsed is not None:
                            existing_ids = {c.column_id for c in parsed_layer.columns}
                            if parsed.column_id not in existing_ids:
                                parsed_layer.columns.append(parsed)
        layers[layer_id] = parsed_layer
    return layers


def _has_text_based_query(state: dict[str, Any]) -> bool:
    top_query = get_dict(state, 'query')
    if top_query is not None and get_str(top_query, 'esql') is not None:
        return True
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return False
    text_based = get_dict(ds_states, 'textBased')
    if text_based is None:
        return False
    layers_raw = get_dict(text_based, 'layers')
    if layers_raw is None:
        return False
    for layer_value in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = get_dict(layer, 'query')
        if query is not None and get_str(query, 'esql') is not None:
            return True
    return False


def _extract_esql_query_from_state(state: dict[str, Any]) -> str | None:
    top_query = get_dict(state, 'query')
    if top_query is not None:
        esql = get_str(top_query, 'esql')
        if esql is not None:
            return esql
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return None
    text_based = get_dict(ds_states, 'textBased')
    if text_based is None:
        return None
    layers_raw = get_dict(text_based, 'layers')
    if layers_raw is None:
        return None
    for layer_value in layers_raw.values():  # pyright: ignore[reportAny]
        layer = as_dict(layer_value)  # pyright: ignore[reportAny]
        if layer is None:
            continue
        query = get_dict(layer, 'query')
        if query is not None:
            esql = get_str(query, 'esql')
            if esql is not None:
                return esql
    return None


def _extract_data_view_from_refs(refs: list[RawReference | object]) -> str | None:
    for ref in refs:
        if not isinstance(ref, RawReference):
            continue
        if ref.type == 'index-pattern' and ref.id is not None:
            return ref.id
    return None


def _parse_lens_panel(panel: RawPanel, raw_panel_type: str) -> ParsedLensPanel:
    embeddable_config_model = panel.embeddable_config or RawEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or RawEmbeddableAttributes()
    state_model = embeddable_attributes_model.state or RawState()
    state = state_model.model_dump(exclude_none=True, by_alias=True)
    is_esql = raw_panel_type == 'esql' or _has_text_based_query(state)
    panel_type = 'esql' if is_esql else 'lens'

    vis_state = _parse_visualization_state(embeddable_attributes_model, is_esql=is_esql)

    # Parse datasource layers
    form_layers = _parse_form_based_layers(state) if not is_esql else {}
    esql_layers = _parse_esql_layers(state) if is_esql else {}

    # Extract top-level ES|QL query
    esql_query = _extract_esql_query_from_state(state) if is_esql else None

    # Extract data view from references
    refs = embeddable_attributes_model.references
    if refs is None:
        refs = embeddable_config_model.references or []
    data_view = _extract_data_view_from_refs(refs)

    parsed_refs: list[ParsedReference] = []
    for ref in refs:
        if not isinstance(ref, RawReference):
            continue
        name = ref.name
        ref_type = ref.type
        ref_id = ref.id
        if name is not None and ref_type is not None and ref_id is not None:
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


def _parse_simple_panel_view(panel: RawPanel, panel_raw: dict[str, Any], panel_type: str) -> object | None:
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(panel_type)
    if model_cls is not None:
        return _validate_view_model(model_cls, panel_raw)
    if panel_type != 'visualization':
        return None
    saved_vis_type = _saved_visualization_panel_type(panel)
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(saved_vis_type or '')
    if model_cls is None:
        return None
    return _validate_view_model(model_cls, panel_raw)


def _parse_simple_panel(panel: RawPanel, panel_raw: dict[str, Any], panel_type: str) -> ParsedSimplePanel:
    embeddable_config_model = panel.embeddable_config or RawEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or RawEmbeddableAttributes()
    embeddable_config = embeddable_config_model.model_dump(exclude_none=True, by_alias=True)
    embeddable_attributes = embeddable_attributes_model.model_dump(exclude_none=True, by_alias=True)
    resolved_panel_type = _saved_visualization_panel_type(panel) if panel_type == 'visualization' else panel_type
    return ParsedSimplePanel(
        panel_type=resolved_panel_type or panel_type,
        raw=panel_raw,
        embeddable_config=embeddable_config,
        embeddable_attributes=embeddable_attributes,
        view_panel=_parse_simple_panel_view(panel, panel_raw, panel_type),
    )


def _parse_panel(panel: dict[str, Any]) -> ParsedPanel:
    raw_panel = RawPanel.model_validate(panel)
    parsed = ParsedPanel()

    panel_index = raw_panel.panel_index
    if panel_index is not None:
        parsed.panel_index = panel_index

    parsed.title = _parse_panel_title(raw_panel)

    grid_raw = raw_panel.grid_data
    if grid_raw is not None:
        parsed.grid = _parse_grid_data(grid_raw)

    panel_type = raw_panel.type
    if panel_type is None:
        parsed.error = 'missing panel type'
        return parsed

    if panel_type in {'lens', 'esql'}:
        try:
            parsed.lens = _parse_lens_panel(raw_panel, panel_type)
        except Exception as exc:
            logger.warning('Failed to parse lens panel %s: %s', parsed.panel_index, exc)
            parsed.error = f'parse error: {exc}'
    elif panel_type in {'markdown', 'search', 'links', 'image', 'vega', 'visualization', 'map'}:
        parsed.simple = _parse_simple_panel(raw_panel, panel, panel_type)
    else:
        parsed.simple = _parse_simple_panel(raw_panel, panel, panel_type)

    return parsed


# ---------------------------------------------------------------------------
# Dashboard-level parsing
# ---------------------------------------------------------------------------


def _parse_settings(attributes: dict[str, Any]) -> ParsedDashboardSettings | None:
    options = parse_json_field(attributes.get('optionsJSON'))
    if not isinstance(options, dict):
        return None
    return ParsedDashboardSettings(
        margins=get_bool(options, 'useMargins'),
        sync_colors=get_bool(options, 'syncColors'),
        sync_cursor=get_bool(options, 'syncCursor'),
        sync_tooltips=get_bool(options, 'syncTooltips'),
        hide_panel_titles=get_bool(options, 'hidePanelTitles'),
        view_options=cast('KbnDashboardOptions | None', _validate_view_model(KbnDashboardOptions, options)),
    )


def _parse_filters(attributes: dict[str, Any]) -> list[ParsedFilter]:
    meta_raw = get_dict(attributes, 'kibanaSavedObjectMeta')
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
        filter_meta = get_dict(raw, 'meta')
        if filter_meta is None:
            continue
        key = get_str(filter_meta, 'key')
        if key is None:
            continue
        result.append(
            ParsedFilter(
                raw=raw,
                meta=filter_meta,
                key=key,
                filter_type=get_str(filter_meta, 'type'),
                view_filter=cast('KbnFilter | None', _validate_view_model(KbnFilter, _normalize_filter_for_view(raw))),
            )
        )
    return result


def _parse_dashboard_query(attributes: dict[str, Any]) -> dict[str, str] | None:
    query_dict: dict[str, str] | None = None
    meta_raw = get_dict(attributes, 'kibanaSavedObjectMeta')
    if meta_raw is not None:
        search_source = parse_json_field(meta_raw.get('searchSourceJSON'))
        if isinstance(search_source, dict):
            raw_query = get_dict(search_source, 'query')
            if raw_query is not None:
                language = get_str(raw_query, 'language')
                query = get_str(raw_query, 'query')
                if query is not None:
                    if language == 'kuery':
                        query_dict = {'kql': query}
                    elif language == 'lucene':
                        query_dict = {'lucene': query}
    return query_dict


def _parse_controls(attributes: dict[str, Any], reference_lookup: dict[str, str]) -> list[ParsedControl]:
    control_group = get_dict(attributes, 'controlGroupInput')
    if control_group is None:
        return []
    panels_json = parse_json_field(control_group.get('panelsJSON'))
    if not isinstance(panels_json, dict):
        return []

    def _order(item: tuple[str, object]) -> int:
        panel = as_dict(item[1])
        if panel is None:
            return 0
        return get_int(panel, 'order') or 0

    result: list[ParsedControl] = []
    for panel_id, panel_value in sorted(panels_json.items(), key=_order):  # pyright: ignore[reportAny]
        panel = as_dict(panel_value)  # pyright: ignore[reportAny]
        if panel is None:
            continue
        explicit_input = get_dict(panel, 'explicitInput')
        ctrl = ParsedControl(raw=panel, control_type=get_str(panel, 'type'))
        if explicit_input is not None:
            fn = get_str(explicit_input, 'fieldName')
            if fn is not None:
                ctrl.field_name = fn
            title = get_str(explicit_input, 'title')
            if title is not None:
                ctrl.title = title
            dv = get_str(explicit_input, 'dataViewId')
            if dv is not None:
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
                    if resolved is not None:
                        ctrl.data_view_id = resolved
                    else:
                        attr_ref = get_str(attributes, ref_name)
                        if attr_ref is not None:
                            ctrl.data_view_id = attr_ref
        normalized_panel = _normalize_control_for_view(panel_id, panel)
        normalized_explicit = get_dict(normalized_panel, 'explicitInput')
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


def _extract_reference_lookup(references: list[RawReference | object] | None) -> dict[str, str]:
    lookup: dict[str, str] = {}
    if references is None:
        return lookup
    for ref in references:
        if not isinstance(ref, RawReference):
            continue
        name = ref.name
        target_id = ref.id
        if name is not None and target_id is not None:
            lookup[name] = target_id
    return lookup


def parse_dashboard(dashboard: dict[str, Any]) -> ParsedDashboard:
    """Parse a raw Kibana dashboard JSON dict into a typed intermediate structure."""
    raw_dashboard = RawDashboard.model_validate(dashboard)
    raw_attributes = raw_dashboard.attributes or RawDashboardAttributes()
    attributes = raw_attributes.model_dump(exclude_none=True, by_alias=True)
    reference_lookup = _extract_reference_lookup(raw_dashboard.references)

    parsed = ParsedDashboard(
        dashboard_id=raw_dashboard.id,
        title=raw_attributes.title if raw_attributes.title is not None else 'Untitled Dashboard',
        description=raw_attributes.description,
        time_from=raw_attributes.time_from,
        time_to=raw_attributes.time_to,
        settings=_parse_settings(attributes),
        query=_parse_dashboard_query(attributes),
        filters=_parse_filters(attributes),
        controls=_parse_controls(attributes, reference_lookup),
        reference_lookup=reference_lookup,
    )

    panels_json = parse_json_field(raw_attributes.panels_json)
    if isinstance(panels_json, list):
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is not None:
                parsed.panels.append(_parse_panel(panel))

    return parsed
