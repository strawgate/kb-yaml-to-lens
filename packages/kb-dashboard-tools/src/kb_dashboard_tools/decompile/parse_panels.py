"""Panel-focused parsing for decompiler parse phase."""

import logging
from collections.abc import Callable, Iterator
from typing import Any, cast

from .parse_models import (
    ParsedColumn,
    ParsedESQLColumn,
    ParsedESQLLayer,
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
    get_dict,
    get_list,
    get_str,
    validate_view_model,
    visualization_model_type,
)
from .raw_models import (
    RawEmbeddableAttributes,
    RawEmbeddableConfig,
    RawGridData,
    RawPanel,
    RawReference,
    RawState,
    RawVisualization,
)

logger = logging.getLogger(__name__)


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


def _iter_raw_references(references: list[RawReference | object] | None) -> Iterator[RawReference]:
    if references is None:
        return
    for ref in references:
        if isinstance(ref, RawReference):
            yield ref


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


def _parse_visualization_state(embeddable_attributes: RawEmbeddableAttributes, *, is_esql: bool) -> ParsedVisualizationState:
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


def _parse_multi_layer_roles(parsed: ParsedVisualizationState, visualization_model: RawVisualization) -> None:
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
    visualization_model: RawVisualization,
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


def _extract_data_view_from_refs(refs: list[RawReference | object]) -> str | None:
    for ref in _iter_raw_references(refs):
        if ref.type == 'index-pattern' and ref.id is not None:
            return ref.id
    return None


def _saved_visualization_panel_type(panel: RawPanel) -> str | None:
    embeddable_config = panel.embeddable_config
    if embeddable_config is None or embeddable_config.saved_vis is None:
        return None
    return embeddable_config.saved_vis.type


def _parse_lens_panel(panel: RawPanel, raw_panel_type: str) -> ParsedLensPanel:
    embeddable_config_model = panel.embeddable_config or RawEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or RawEmbeddableAttributes()
    state_model = embeddable_attributes_model.state or RawState()
    state = state_model.model_dump(exclude_none=True, by_alias=True)
    is_esql = raw_panel_type == 'esql' or _has_text_based_query(state)
    panel_type = 'esql' if is_esql else 'lens'

    vis_state = _parse_visualization_state(embeddable_attributes_model, is_esql=is_esql)
    form_layers = _parse_form_based_layers(state) if not is_esql else {}
    esql_layers = _parse_esql_layers(state) if is_esql else {}
    esql_query = _extract_esql_query_from_state(state) if is_esql else None

    refs = embeddable_attributes_model.references
    if refs is None:
        refs = embeddable_config_model.references or []
    data_view = _extract_data_view_from_refs(refs)

    parsed_refs = [
        ParsedReference(name=ref.name, ref_type=ref.type, ref_id=ref.id)
        for ref in _iter_raw_references(refs)
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


def _parse_simple_panel_view(panel: RawPanel, panel_raw: dict[str, Any], panel_type: str) -> SimplePanelViewModel | None:
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


def _parse_simple_panel(panel: RawPanel, panel_raw: dict[str, Any], panel_type: str) -> ParsedSimplePanel:
    embeddable_config_model = panel.embeddable_config or RawEmbeddableConfig()
    embeddable_attributes_model = embeddable_config_model.attributes or RawEmbeddableAttributes()
    resolved_panel_type = _saved_visualization_panel_type(panel) if panel_type == 'visualization' else panel_type
    return ParsedSimplePanel(
        panel_type=resolved_panel_type or panel_type,
        raw=panel_raw,
        embeddable_config=embeddable_config_model.model_dump(exclude_none=True, by_alias=True),
        embeddable_attributes=embeddable_attributes_model.model_dump(exclude_none=True, by_alias=True),
        view_panel=_parse_simple_panel_view(panel, panel_raw, panel_type),
    )


def _assign_lens_panel(parsed: ParsedPanel, raw_panel: RawPanel, _panel_raw: dict[str, Any], panel_type: str) -> None:
    try:
        parsed.lens = _parse_lens_panel(raw_panel, panel_type)
    except Exception as exc:
        logger.warning('Failed to parse lens panel %s: %s', parsed.panel_index, exc)
        parsed.error = f'parse error: {exc}'


def _assign_simple_panel(parsed: ParsedPanel, raw_panel: RawPanel, panel_raw: dict[str, Any], panel_type: str) -> None:
    parsed.simple = _parse_simple_panel(raw_panel, panel_raw, panel_type)


PanelParseHandler = Callable[[ParsedPanel, RawPanel, dict[str, Any], str], None]
PANEL_PARSE_HANDLERS: dict[str, PanelParseHandler] = {
    'lens': _assign_lens_panel,
    'esql': _assign_lens_panel,
}


def parse_panel(panel: dict[str, Any]) -> ParsedPanel:
    """Parse a panel JSON object into ParsedPanel."""
    raw_panel = RawPanel.model_validate(panel)
    parsed = ParsedPanel()

    if raw_panel.panel_index is not None:
        parsed.panel_index = raw_panel.panel_index
    parsed.title = _parse_panel_title(raw_panel)
    if raw_panel.grid_data is not None:
        parsed.grid = _parse_grid_data(raw_panel.grid_data)

    panel_type = raw_panel.type
    if panel_type is None:
        parsed.error = 'missing panel type'
        return parsed
    panel_ref_name = get_str(panel, 'panelRefName')
    embeddable_config = get_dict(panel, 'embeddableConfig') or {}
    if panel_ref_name is not None and get_dict(embeddable_config, 'attributes') is None:
        parsed.error = f'unresolved panel reference: {panel_ref_name}'
        return parsed

    handler = PANEL_PARSE_HANDLERS.get(panel_type, _assign_simple_panel)
    handler(parsed, raw_panel, panel, panel_type)
    return parsed
