"""Dashboard parsing via KbnDashboard.model_validate — replaces parse_dashboard and parse_panels."""

import logging
from collections.abc import Callable, Iterator
from typing import Any, cast

from kb_dashboard_core.controls.view import (
    KbnESQLControl,
    KbnOptionsListControl,
    KbnRangeSliderControl,
    KbnTimeSliderControl,
)
from kb_dashboard_core.dashboard.view import KbnDashboardOptions
from kb_dashboard_core.filters.view import KbnFilter

from .kbn_raw_models.models import (
    KbnDashboard,
    KbnDashboardAttributes,
    KbnEmbeddableAttributes,
    KbnEmbeddableConfig,
    KbnPanel,
    KbnReference,
    KbnVisualization,
)
from .parse_models import (
    ParsedColumn,
    ParsedControl,
    ParsedDashboard,
    ParsedDashboardSettings,
    ParsedESQLColumn,
    ParsedESQLLayer,
    ParsedFilter,
    ParsedFormLayer,
    ParsedGridData,
    ParsedLensPanel,
    ParsedPanel,
    ParsedReference,
    ParsedSimplePanel,
    ParsedVisualizationLayerRole,
    ParsedVisualizationState,
    SimplePanelViewModel,
    VisualizationViewModel,
)
from .parse_shared import (
    SIMPLE_PANEL_VIEW_MODEL_MAP,
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_list,
    get_str,
    parse_json_field,
    validate_view_model,
    visualization_model_type,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reference helpers
# ---------------------------------------------------------------------------


def _build_reference_lookup(references: list[KbnReference | object] | None) -> dict[str, str]:
    lookup: dict[str, str] = {}
    if references is None:
        return lookup
    for ref in references:
        if isinstance(ref, KbnReference) and ref.name is not None and ref.id is not None:
            lookup[ref.name] = ref.id
    return lookup


def _iter_typed_references(references: list[KbnReference | object] | None) -> Iterator[KbnReference]:
    if references is None:
        return
    for ref in references:
        if isinstance(ref, KbnReference):
            yield ref


# ---------------------------------------------------------------------------
# Dashboard-level settings
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
        view_options=cast('KbnDashboardOptions | None', validate_view_model(KbnDashboardOptions, options)),
    )


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def _normalize_filter_for_view(raw: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(raw)
    state = cast('object', normalized.pop('$state', None))
    if 'state' not in normalized and isinstance(state, dict):
        normalized['state'] = state
    return normalized


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
        key = get_str(filter_meta, 'key') if filter_meta is not None else None
        if filter_meta is None or key is None:
            continue
        result.append(
            ParsedFilter(
                raw=raw,
                meta=filter_meta,
                key=key,
                filter_type=get_str(filter_meta, 'type'),
                view_filter=cast('KbnFilter | None', validate_view_model(KbnFilter, _normalize_filter_for_view(raw))),
            )
        )
    return result


# ---------------------------------------------------------------------------
# Dashboard query
# ---------------------------------------------------------------------------


def _parse_dashboard_query(attributes: dict[str, Any]) -> dict[str, str] | None:
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
                        return {'kql': query}
                    if language == 'lucene':
                        return {'lucene': query}
    return None


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def _normalize_control_for_view(panel_id: str, raw: dict[str, Any]) -> dict[str, Any]:
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
    elif panel_type in ('rangeSliderControl', 'timeSlider'):
        _ = normalized_explicit.setdefault('step', None)
    elif panel_type == 'esqlControl':
        normalized_explicit.setdefault('selectedOptions', [])

    if normalized_explicit:
        normalized['explicitInput'] = normalized_explicit
    return normalized


def _parse_controls(
    attributes: dict[str, Any],
    reference_lookup: dict[str, str],
) -> list[ParsedControl]:
    control_group = get_dict(attributes, 'controlGroupInput')
    if control_group is None:
        return []
    panels_json = parse_json_field(control_group.get('panelsJSON'))
    if not isinstance(panels_json, dict):
        return []

    def _order(item: tuple[str, object]) -> int:
        panel = as_dict(item[1])
        return (get_int(panel, 'order') or 0) if panel is not None else 0

    def _resolve_control_data_view(control_type: str | None, panel_id: str, explicit_input: dict[str, Any]) -> str | None:
        direct = get_str(explicit_input, 'dataViewId')
        if direct is not None:
            return direct
        ref_suffix = {
            'optionsListControl': 'optionsListDataView',
            'rangeSliderControl': 'rangeSliderDataView',
            'timeSliderControl': 'timeSliderDataView',
            'esqlControl': 'esqlControlDataView',
        }.get(control_type or '')
        if ref_suffix is None:
            return None
        ref_name = f'controlGroup_{panel_id}:{ref_suffix}'
        return reference_lookup.get(ref_name) or get_str(attributes, ref_name)

    result: list[ParsedControl] = []
    for panel_id, panel_value in sorted(panels_json.items(), key=_order):  # pyright: ignore[reportAny]
        panel = as_dict(panel_value)  # pyright: ignore[reportAny]
        if panel is None:
            continue
        explicit_input = get_dict(panel, 'explicitInput')
        ctrl = ParsedControl(raw=panel, control_type=get_str(panel, 'type'))
        if explicit_input is not None:
            ctrl.field_name = get_str(explicit_input, 'fieldName')
            ctrl.title = get_str(explicit_input, 'title')
            ctrl.data_view_id = _resolve_control_data_view(ctrl.control_type, panel_id, explicit_input)

        normalized_panel = _normalize_control_for_view(panel_id, panel)
        normalized_explicit = get_dict(normalized_panel, 'explicitInput')
        if normalized_explicit is not None and ctrl.data_view_id is not None and 'dataViewId' not in normalized_explicit:
            normalized_explicit = dict(normalized_explicit)
            normalized_explicit['dataViewId'] = ctrl.data_view_id
            normalized_panel['explicitInput'] = normalized_explicit

        if ctrl.control_type == 'optionsListControl':
            ctrl.view_control = cast('KbnOptionsListControl | None', validate_view_model(KbnOptionsListControl, normalized_panel))
        elif ctrl.control_type == 'rangeSliderControl':
            ctrl.view_control = cast('KbnRangeSliderControl | None', validate_view_model(KbnRangeSliderControl, normalized_panel))
        elif ctrl.control_type in ('timeSliderControl', 'timeSlider'):
            ctrl.view_control = cast('KbnTimeSliderControl | None', validate_view_model(KbnTimeSliderControl, normalized_panel))
        elif ctrl.control_type == 'esqlControl':
            ctrl.view_control = cast('KbnESQLControl | None', validate_view_model(KbnESQLControl, normalized_panel))
        result.append(ctrl)
    return result


# ---------------------------------------------------------------------------
# Panel parsing helpers (ported from parse_panels.py)
# ---------------------------------------------------------------------------


def _parse_grid_data(raw: dict[str, Any]) -> ParsedGridData:
    return ParsedGridData(
        x=get_int(raw, 'x'),
        y=get_int(raw, 'y'),
        w=get_int(raw, 'w'),
        h=get_int(raw, 'h'),
        section_id=get_str(raw, 'sectionId'),
    )


def _parse_panel_title(panel: KbnPanel) -> str:
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


def _iter_named_dict_entries(source: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    for key, value in source.items():  # pyright: ignore[reportAny]
        item = as_dict(value)  # pyright: ignore[reportAny]
        if item is not None:
            yield key, item


def _get_datasource_layers(state: dict[str, Any], datasource_key: str) -> dict[str, Any] | None:
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return None
    datasource = get_dict(ds_states, datasource_key)
    if datasource is None:
        return None
    return get_dict(datasource, 'layers')


def _parse_visualization_view_model(
    visualization_type: str | None,
    visualization: dict[str, Any],
    *,
    is_esql: bool,
) -> VisualizationViewModel | None:
    model_cls = visualization_model_type(visualization_type, visualization, is_esql=is_esql)
    if model_cls is None:
        return None
    return cast('VisualizationViewModel | None', validate_view_model(model_cls, visualization))


def _parse_multi_layer_roles(parsed: ParsedVisualizationState, visualization_model: KbnVisualization) -> None:
    vis_layers = visualization_model.layers
    if vis_layers is None:
        return
    for vis_layer in vis_layers:
        layer_id = vis_layer.layer_id
        if layer_id is None:
            continue
        vis_layer_dict = vis_layer.model_dump(exclude_none=True, by_alias=True)
        role = ParsedVisualizationLayerRole(layer_id=layer_id)
        metric_ids = vis_layer.accessors
        if metric_ids is not None:
            role.metric_ids = [v for v in metric_ids if isinstance(v, str)]
        if vis_layer.x_accessor is not None:
            role.dimension_id = vis_layer.x_accessor
        if vis_layer.split_accessor is not None:
            role.breakdown_id = vis_layer.split_accessor
        role.accessors = _dedupe_ids(
            [
                *_collect_accessor_ids(vis_layer_dict, ('xAccessor', 'splitAccessor')),
                *role.metric_ids,
            ]
        )
        parsed.layer_roles[layer_id] = role


def _parse_single_layer_roles(
    parsed: ParsedVisualizationState,
    visualization_model: KbnVisualization,
    visualization: dict[str, Any],
) -> None:
    single_layer_id = visualization_model.layer_id
    if single_layer_id is None:
        return
    role = parsed.layer_roles.setdefault(single_layer_id, ParsedVisualizationLayerRole(layer_id=single_layer_id))
    for value in (visualization_model.metric_accessor, visualization_model.secondary_accessor, visualization_model.accessor):
        if value is not None and value not in role.metric_ids:
            role.metric_ids.append(value)
    if visualization_model.accessors is not None:
        for v in visualization_model.accessors:
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


def _parse_visualization_state(embeddable_attributes: KbnEmbeddableAttributes, *, is_esql: bool) -> ParsedVisualizationState:
    state_raw = embeddable_attributes.state
    vis_type = embeddable_attributes.visualization_type
    parsed = ParsedVisualizationState(raw_type=vis_type)
    if state_raw is None or state_raw.visualization is None:
        return parsed

    visualization_model = state_raw.visualization
    visualization = visualization_model.model_dump(exclude_none=True, by_alias=True)
    parsed.raw = visualization
    parsed.view_model = _parse_visualization_view_model(parsed.raw_type, visualization, is_esql=is_esql)
    parsed.preferred_series_type = visualization_model.preferred_series_type
    parsed.shape = visualization_model.shape

    _parse_multi_layer_roles(parsed, visualization_model)
    _parse_single_layer_roles(parsed, visualization_model, visualization)

    return parsed


def _parse_form_based_layers(state: dict[str, Any]) -> dict[str, ParsedFormLayer]:
    layers_raw = _get_datasource_layers(state, 'formBased')
    if layers_raw is None:
        return {}

    layers: dict[str, ParsedFormLayer] = {}
    for layer_id, layer in _iter_named_dict_entries(layers_raw):
        parsed_layer = ParsedFormLayer(layer_id=layer_id, index_pattern_id=get_str(layer, 'indexPatternId'))
        column_order = get_list(layer, 'columnOrder')
        if column_order is not None:
            parsed_layer.column_order = [c for c in column_order if isinstance(c, str)]
        for col_id, col in _iter_named_dict_entries(get_dict(layer, 'columns') or {}):
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
    for _, layer in _iter_named_dict_entries(layers_raw):
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
    for _, layer in _iter_named_dict_entries(layers_raw):
        query = get_dict(layer, 'query')
        if query is not None and get_str(query, 'esql') is not None:
            return True
    return False


def _parse_esql_layers(state: dict[str, Any]) -> dict[str, ParsedESQLLayer]:
    layers_raw = _get_datasource_layers(state, 'textBased')
    if layers_raw is None:
        return {}

    top_esql = _extract_esql_query_from_state(state)
    layers: dict[str, ParsedESQLLayer] = {}
    for layer_id, layer in _iter_named_dict_entries(layers_raw):
        query_obj = get_dict(layer, 'query')
        esql = get_str(query_obj, 'esql') if query_obj is not None else top_esql
        if esql is None:
            continue
        parsed_layer = ParsedESQLLayer(layer_id=layer_id, query=esql)
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


def _extract_data_view_from_refs(refs: list[KbnReference | object]) -> str | None:
    for ref in _iter_typed_references(refs):
        if ref.type == 'index-pattern' and ref.id is not None:
            return ref.id
    return None


def _saved_visualization_panel_type(panel: KbnPanel) -> str | None:
    embeddable_config = panel.embeddable_config
    if embeddable_config is None or embeddable_config.saved_vis is None:
        return None
    return embeddable_config.saved_vis.type


def _parse_lens_panel(panel: KbnPanel, raw_panel_type: str) -> ParsedLensPanel:
    embeddable_config_model = panel.embeddable_config or KbnEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or KbnEmbeddableAttributes()
    state_model = embeddable_attributes_model.state
    state_dict: dict[str, Any] = {}
    if state_model is not None:
        state_dict = state_model.model_dump(exclude_none=True, by_alias=True)
    is_esql = raw_panel_type == 'esql' or _has_text_based_query(state_dict)
    panel_type = 'esql' if is_esql else 'lens'

    vis_state = _parse_visualization_state(embeddable_attributes_model, is_esql=is_esql)
    form_layers = _parse_form_based_layers(state_dict) if not is_esql else {}
    esql_layers = _parse_esql_layers(state_dict) if is_esql else {}
    esql_query = _extract_esql_query_from_state(state_dict) if is_esql else None

    refs = embeddable_attributes_model.references
    if refs is None:
        refs = embeddable_config_model.references or []
    data_view = _extract_data_view_from_refs(refs)

    parsed_refs = [
        ParsedReference(name=ref.name, ref_type=ref.type, ref_id=ref.id)
        for ref in _iter_typed_references(refs)
        if ref.name is not None and ref.type is not None and ref.id is not None
    ]

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


def _parse_simple_panel_view(panel: KbnPanel, panel_raw: dict[str, Any], panel_type: str) -> SimplePanelViewModel | None:
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(panel_type)
    if model_cls is not None:
        return cast('SimplePanelViewModel | None', validate_view_model(model_cls, panel_raw))
    if panel_type != 'visualization':
        return None
    saved_vis_type = _saved_visualization_panel_type(panel)
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(saved_vis_type or '')
    if model_cls is None:
        return None
    return cast('SimplePanelViewModel | None', validate_view_model(model_cls, panel_raw))


def _parse_simple_panel(panel: KbnPanel, panel_raw: dict[str, Any], panel_type: str) -> ParsedSimplePanel:
    embeddable_config_model = panel.embeddable_config or KbnEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or KbnEmbeddableAttributes()
    resolved_panel_type = _saved_visualization_panel_type(panel) if panel_type == 'visualization' else panel_type
    return ParsedSimplePanel(
        panel_type=resolved_panel_type or panel_type,
        raw=panel_raw,
        embeddable_config=embeddable_config_model.model_dump(exclude_none=True, by_alias=True),
        embeddable_attributes=embeddable_attributes_model.model_dump(exclude_none=True, by_alias=True),
        view_panel=_parse_simple_panel_view(panel, panel_raw, panel_type),
    )


def _assign_lens_panel(parsed: ParsedPanel, kbn_panel: KbnPanel, _panel_raw: dict[str, Any], panel_type: str) -> None:
    try:
        parsed.lens = _parse_lens_panel(kbn_panel, panel_type)
    except Exception as exc:
        logger.warning('Failed to parse lens panel %s: %s', parsed.panel_index, exc)
        parsed.error = f'parse error: {exc}'


def _assign_simple_panel(parsed: ParsedPanel, kbn_panel: KbnPanel, panel_raw: dict[str, Any], panel_type: str) -> None:
    parsed.simple = _parse_simple_panel(kbn_panel, panel_raw, panel_type)


PanelParseHandler = Callable[[ParsedPanel, KbnPanel, dict[str, Any], str], None]
PANEL_PARSE_HANDLERS: dict[str, PanelParseHandler] = {
    'lens': _assign_lens_panel,
    'esql': _assign_lens_panel,
}


def _parse_panel(panel_raw: dict[str, Any]) -> ParsedPanel:
    kbn_panel = KbnPanel.model_validate(panel_raw)
    parsed = ParsedPanel()

    if kbn_panel.panel_index is not None:
        parsed.panel_index = kbn_panel.panel_index
    parsed.title = _parse_panel_title(kbn_panel)
    if kbn_panel.grid_data is not None:
        grid_dict = kbn_panel.grid_data.model_dump(by_alias=True)
        parsed.grid = _parse_grid_data(grid_dict)

    embeddable_cfg = get_dict(panel_raw, 'embeddableConfig') or {}
    hide_panel_titles = get_bool(embeddable_cfg, 'hidePanelTitles')
    if hide_panel_titles is True:
        parsed.hide_title = True
    panel_description = get_str(embeddable_cfg, 'description')
    if panel_description is None:
        panel_description = get_str(panel_raw, 'description')
    if panel_description is not None and len(panel_description) > 0:
        parsed.description = panel_description

    panel_type = kbn_panel.type
    if panel_type is None:
        parsed.error = 'missing panel type'
        return parsed
    panel_ref_name = get_str(panel_raw, 'panelRefName')
    embeddable_config = get_dict(panel_raw, 'embeddableConfig') or {}
    if panel_ref_name is not None and get_dict(embeddable_config, 'attributes') is None:
        parsed.error = f'unresolved panel reference: {panel_ref_name}'
        return parsed

    handler = PANEL_PARSE_HANDLERS.get(panel_type, _assign_simple_panel)
    handler(parsed, kbn_panel, panel_raw, panel_type)
    return parsed


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def parse_dashboard(raw: dict[str, Any]) -> ParsedDashboard:
    """Parse a raw Kibana dashboard JSON dict into a typed intermediate structure."""
    kbn = KbnDashboard.model_validate(raw)
    kbn_attributes = kbn.attributes or KbnDashboardAttributes()
    attributes = kbn_attributes.model_dump(exclude_none=True, by_alias=True)
    reference_lookup = _build_reference_lookup(kbn.references)

    parsed = ParsedDashboard(
        dashboard_id=kbn.id,
        title=kbn_attributes.title if kbn_attributes.title is not None else 'Untitled Dashboard',
        description=kbn_attributes.description,
        time_from=kbn_attributes.time_from,
        time_to=kbn_attributes.time_to,
        settings=_parse_settings(attributes),
        query=_parse_dashboard_query(attributes),
        filters=_parse_filters(attributes),
        controls=_parse_controls(attributes, reference_lookup),
        reference_lookup=reference_lookup,
    )

    panels_json = parse_json_field(kbn_attributes.panels_json)
    if isinstance(panels_json, list):
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is not None:
                parsed.panels.append(_parse_panel(panel))

    return parsed
