"""Decompile a Kibana dashboard JSON object into a YAML dashboard stub."""

import json
from typing import Any, cast

from ruamel.yaml.comments import CommentedMap, CommentedSeq

_LENS_VISUALIZATION_TYPES = {
    'metric': 'metric',
    'gauge': 'gauge',
    'pie': 'pie',
    'bar': 'bar',
    'line': 'line',
    'area': 'area',
    'heatmap': 'heatmap',
    'datatable': 'table',
    'tagcloud': 'tagcloud',
    'mosaic': 'mosaic',
    'waffle': 'waffle',
    'lnsmetric': 'metric',
    'lnsgauge': 'gauge',
    'lnspie': 'pie',
    'lnsheatmap': 'heatmap',
    'lnsdatatable': 'table',
    'lnstagcloud': 'tagcloud',
    'lnsmosaic': 'mosaic',
    'lnswaffle': 'waffle',
    'lnsxy': None,  # resolved via preferredSeriesType
}

_XY_SERIES_TYPES: dict[str, str] = {
    'line': 'line',
    'bar': 'bar',
    'bar_stacked': 'bar',
    'bar_horizontal': 'bar',
    'bar_horizontal_stacked': 'bar',
    'bar_percentage_stacked': 'bar',
    'bar_horizontal_percentage_stacked': 'bar',
    'area': 'area',
    'area_stacked': 'area',
    'area_percentage_stacked': 'area',
}

_PIE_SHAPES: dict[str, str] = {
    'pie': 'pie',
    'donut': 'donut',
    'treemap': 'treemap',
}

_OPERATION_TYPE_MAP: dict[str, str] = {
    'count': 'count',
    'sum': 'sum',
    'avg': 'average',
    'average': 'average',
    'min': 'min',
    'max': 'max',
    'median': 'median',
    'unique_count': 'unique_count',
    'last_value': 'last_value',
    'percentile': 'percentile',
}

_SKIP_OPERATION_TYPES = {'formula', 'differences', 'math', 'cumulative_sum', 'counter_rate', 'moving_average'}


def _as_dict(value: object) -> dict[str, Any] | None:
    """Narrow an unknown value to a typed dict, or return None."""
    if isinstance(value, dict):
        return cast('dict[str, Any]', value)
    return None


def _parse_json_field(field: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a JSON field that may be a string, dict, list, or None."""
    if field is None:
        return None
    if isinstance(field, str):
        parsed: dict[str, Any] | list[Any] = json.loads(field)  # pyright: ignore[reportAny]
        return parsed
    return field


def _to_int(value: object) -> int | None:
    """Convert an unknown value to int only when it is already an integer."""
    if isinstance(value, int):
        return value
    return None


def _normalize_lens_type(value: object) -> str | None:
    """Normalize Lens visualization type values from Kibana."""
    if not isinstance(value, str):
        return None
    return _LENS_VISUALIZATION_TYPES.get(value.lower())


def _resolve_xy_type(embeddable_attributes: dict[str, Any]) -> str | None:
    """Resolve XY chart sub-type from preferredSeriesType in visualization state."""
    state = _as_dict(embeddable_attributes.get('state'))
    if state is None:
        return 'line'

    visualization = _as_dict(state.get('visualization'))
    if visualization is None:
        return 'line'

    preferred = visualization.get('preferredSeriesType')
    if isinstance(preferred, str):
        resolved = _XY_SERIES_TYPES.get(preferred)
        if resolved is not None:
            return resolved

    return 'line'


def _resolve_pie_shape(embeddable_attributes: dict[str, Any]) -> str:
    """Resolve pie chart shape from visualization state."""
    state = _as_dict(embeddable_attributes.get('state'))
    if state is None:
        return 'pie'

    visualization = _as_dict(state.get('visualization'))
    if visualization is None:
        return 'pie'

    shape = visualization.get('shape')
    if isinstance(shape, str):
        resolved = _PIE_SHAPES.get(shape)
        if resolved is not None:
            return resolved

    return 'pie'


def _extract_panel_title(panel: dict[str, Any]) -> str:
    """Extract panel title from panel-level or embeddable config."""
    direct_title = panel.get('title')
    if isinstance(direct_title, str):
        return direct_title

    embeddable_config = _as_dict(panel.get('embeddableConfig'))
    if embeddable_config is not None:
        embedded_title = embeddable_config.get('title')
        if isinstance(embedded_title, str):
            return embedded_title

    return ''


def _extract_embeddable_attributes(panel: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract embeddable config and nested attributes dictionaries."""
    embeddable_config = _as_dict(panel.get('embeddableConfig'))
    if embeddable_config is None:
        return {}, {}

    embeddable_attributes: dict[str, Any] = {}
    attributes = _as_dict(embeddable_config.get('attributes'))
    if attributes is not None:
        embeddable_attributes = attributes
    return embeddable_config, embeddable_attributes


def _extract_data_view_from_references(panel: dict[str, Any]) -> str | None:
    """Extract data view ID from panel references."""
    embeddable_config, embeddable_attributes = _extract_embeddable_attributes(panel)

    references = embeddable_attributes.get('references')
    if not isinstance(references, list):
        references = embeddable_config.get('references')
    if not isinstance(references, list):
        return None

    for ref_item in references:  # pyright: ignore[reportUnknownVariableType]
        ref = _as_dict(ref_item)  # pyright: ignore[reportUnknownArgumentType]
        if ref is None:
            continue
        ref_type = ref.get('type')
        ref_id = ref.get('id')
        if ref_type == 'index-pattern' and isinstance(ref_id, str):
            return ref_id

    return None


def _build_bucketed_column(col: dict[str, Any], op_type: str) -> tuple[str, CommentedMap] | None:
    """Build a dimension or breakdown stub from a bucketed column.

    Returns a tuple of (category, stub) where category is 'dimension' or 'breakdown',
    or None if the column type is unrecognized.
    """
    if op_type == 'date_histogram':
        dim = CommentedMap()
        dim['type'] = 'date_histogram'
        source_field = col.get('sourceField')
        if isinstance(source_field, str):
            dim['field'] = source_field
        params = _as_dict(col.get('params'))
        if params is not None:
            interval = params.get('interval')
            if isinstance(interval, str) and interval != 'auto':
                dim['minimum_interval'] = interval
        return 'dimension', dim

    if op_type == 'terms':
        bd = CommentedMap()
        bd['type'] = 'values'
        source_field = col.get('sourceField')
        if isinstance(source_field, str):
            bd['field'] = source_field
        params = _as_dict(col.get('params'))
        if params is not None:
            size = params.get('size')
            if isinstance(size, int):
                bd['size'] = size
        return 'breakdown', bd

    if op_type == 'filters':
        bd = CommentedMap()
        bd['type'] = 'filters'
        return 'breakdown', bd

    return None


def _build_metric_column(col: dict[str, Any], op_type: str) -> tuple[CommentedMap | None, str | None]:
    """Build a metric stub from a non-bucketed column.

    Returns a tuple of (metric_stub, skipped_op_type). Exactly one will be non-None.
    """
    if op_type in _SKIP_OPERATION_TYPES:
        return None, op_type

    aggregation = _OPERATION_TYPE_MAP.get(op_type)
    if aggregation is None:
        return None, op_type

    metric = CommentedMap()
    metric['aggregation'] = aggregation

    source_field = col.get('sourceField')
    if isinstance(source_field, str) and source_field != 'Records':
        metric['field'] = source_field

    label = col.get('label')
    if isinstance(label, str) and len(label) > 0:
        metric['label'] = label

    return metric, None


def _get_form_based_layers(embeddable_attributes: dict[str, Any]) -> dict[str, Any] | None:
    """Navigate to formBased layers dict, returning None if any level is missing."""
    state = _as_dict(embeddable_attributes.get('state'))
    if state is None:
        return None
    datasource_states = _as_dict(state.get('datasourceStates'))
    if datasource_states is None:
        return None
    form_based = _as_dict(datasource_states.get('formBased'))
    if form_based is None:
        return None
    return _as_dict(form_based.get('layers'))


def _classify_column(
    col: dict[str, Any],
    metrics: list[CommentedMap],
    dimensions: list[CommentedMap],
    breakdowns: list[CommentedMap],
    skipped: list[str],
) -> None:
    """Classify a single form-based column into metrics, dimensions, breakdowns, or skipped."""
    op_type = col.get('operationType')
    if not isinstance(op_type, str):
        return

    is_bucketed = col.get('isBucketed')
    if isinstance(is_bucketed, bool) and is_bucketed:
        result = _build_bucketed_column(col, op_type)
        if result is not None:
            category, stub = result
            if category == 'dimension':
                dimensions.append(stub)
            else:
                breakdowns.append(stub)
    else:
        metric, skipped_op = _build_metric_column(col, op_type)
        if metric is not None:
            metrics.append(metric)
        elif skipped_op is not None:
            skipped.append(skipped_op)


def _extract_form_based_columns(
    embeddable_attributes: dict[str, Any],
) -> tuple[list[CommentedMap], list[CommentedMap], list[CommentedMap], list[str]]:
    """Extract metrics, dimensions, and breakdowns from form-based datasource layers.

    Returns a tuple of (metrics, dimensions, breakdowns, skipped_operation_types).
    """
    metrics: list[CommentedMap] = []
    dimensions: list[CommentedMap] = []
    breakdowns: list[CommentedMap] = []
    skipped: list[str] = []

    layers = _get_form_based_layers(embeddable_attributes)
    if layers is None:
        return metrics, dimensions, breakdowns, skipped

    for layer_value in layers.values():  # pyright: ignore[reportAny]
        layer = _as_dict(layer_value)  # pyright: ignore[reportUnknownArgumentType]
        if layer is None:
            continue

        columns = _as_dict(layer.get('columns'))
        if columns is None:
            continue

        for col_value in columns.values():  # pyright: ignore[reportAny]
            col = _as_dict(col_value)  # pyright: ignore[reportUnknownArgumentType]
            if col is None:
                continue
            _classify_column(col, metrics, dimensions, breakdowns, skipped)

    return metrics, dimensions, breakdowns, skipped


def _extract_esql_query(embeddable_attributes: dict[str, Any]) -> str | None:
    """Extract ES|QL query string from textBased datasource layers."""
    state = _as_dict(embeddable_attributes.get('state'))
    if state is None:
        return None

    datasource_states = _as_dict(state.get('datasourceStates'))
    if datasource_states is None:
        return None

    text_based = _as_dict(datasource_states.get('textBased'))
    if text_based is None:
        return None

    layers = _as_dict(text_based.get('layers'))
    if layers is None:
        return None

    for layer_value in layers.values():  # pyright: ignore[reportAny]
        layer = _as_dict(layer_value)  # pyright: ignore[reportUnknownArgumentType]
        if layer is None:
            continue
        query = _as_dict(layer.get('query'))
        if query is None:
            continue
        esql = query.get('esql')
        if isinstance(esql, str):
            return esql

    return None


def _build_markdown_stub(panel: dict[str, Any], _reference_lookup: dict[str, str]) -> CommentedMap:
    """Build markdown panel stub."""
    embeddable_config, _ = _extract_embeddable_attributes(panel)
    markdown = CommentedMap()

    markdown_content = embeddable_config.get('markdown')
    if not isinstance(markdown_content, str):
        saved_vis = _as_dict(embeddable_config.get('savedVis'))
        if saved_vis is not None:
            params = _as_dict(saved_vis.get('params'))
            if params is not None:
                markdown_content = params.get('markdown')

    if isinstance(markdown_content, str):
        markdown['content'] = markdown_content
    else:
        markdown['content'] = 'TODO(decompile): provide markdown content'

    saved_vis = _as_dict(embeddable_config.get('savedVis'))
    if saved_vis is not None:
        params = _as_dict(saved_vis.get('params'))
        if params is not None:
            font_size = _to_int(params.get('fontSize'))
            if font_size is not None:
                markdown['font_size'] = font_size
            links_in_new_tab = params.get('openLinksInNewTab')
            if isinstance(links_in_new_tab, bool):
                markdown['links_in_new_tab'] = links_in_new_tab

    return markdown


def _build_search_stub(panel: dict[str, Any], reference_lookup: dict[str, str]) -> CommentedMap:
    """Build search panel stub."""
    search = CommentedMap()

    saved_search_id = panel.get('savedSearchId')
    if isinstance(saved_search_id, str):
        search['saved_search_id'] = saved_search_id
        return search

    embeddable_config = _as_dict(panel.get('embeddableConfig'))
    if embeddable_config is not None:
        saved_search_ref_name = embeddable_config.get('savedSearchRefName')
        if isinstance(saved_search_ref_name, str):
            resolved_saved_search_id = reference_lookup.get(saved_search_ref_name)
            if isinstance(resolved_saved_search_id, str):
                search['saved_search_id'] = resolved_saved_search_id
                return search

    search['saved_search_id'] = 'TODO_saved_search_id'
    return search


def _extract_links_attributes(panel: dict[str, Any]) -> dict[str, Any]:
    """Extract links panel attributes from embeddable config."""
    embeddable_config, embeddable_attributes = _extract_embeddable_attributes(panel)
    if len(embeddable_attributes) == 0:
        attributes = _as_dict(embeddable_config.get('attributes'))
        if attributes is not None:
            embeddable_attributes = attributes
    return embeddable_attributes


def _build_link_common_fields(raw_link: dict[str, Any]) -> CommentedMap:
    """Build common link fields shared by dashboard and external links."""
    link_item = CommentedMap()
    link_id = raw_link.get('id')
    if isinstance(link_id, str):
        link_item['id'] = link_id

    label = raw_link.get('label')
    if isinstance(label, str):
        link_item['label'] = label
    return link_item


def _build_external_link_item(raw_link: dict[str, Any], options: dict[str, Any]) -> CommentedMap | None:
    """Build a decompiled external link item."""
    destination = raw_link.get('destination')
    if not isinstance(destination, str):
        return None

    link_item = _build_link_common_fields(raw_link)
    link_item['url'] = destination

    new_tab = options.get('openInNewTab')
    if isinstance(new_tab, bool):
        link_item['new_tab'] = new_tab

    encode = options.get('encodeUrl')
    if isinstance(encode, bool):
        link_item['encode'] = encode
    return link_item


def _build_dashboard_link_item(raw_link: dict[str, Any], options: dict[str, Any], reference_lookup: dict[str, str]) -> CommentedMap | None:
    """Build a decompiled dashboard link item."""
    destination_ref_name = raw_link.get('destinationRefName')
    if not isinstance(destination_ref_name, str):
        return None

    link_item = _build_link_common_fields(raw_link)
    dashboard_id = reference_lookup.get(destination_ref_name)
    if isinstance(dashboard_id, str):
        link_item['dashboard'] = dashboard_id
    else:
        link_item['dashboard'] = f'TODO_dashboard_id_for_{destination_ref_name}'

    new_tab = options.get('openInNewTab')
    if isinstance(new_tab, bool):
        link_item['new_tab'] = new_tab

    with_time = options.get('useCurrentDateRange')
    if isinstance(with_time, bool):
        link_item['with_time'] = with_time

    with_filters = options.get('useCurrentFilters')
    if isinstance(with_filters, bool):
        link_item['with_filters'] = with_filters
    return link_item


def _build_links_stub(panel: dict[str, Any], reference_lookup: dict[str, str]) -> CommentedMap:
    """Build links panel stub."""
    links = CommentedMap()
    embeddable_attributes = _extract_links_attributes(panel)

    layout = embeddable_attributes.get('layout')
    if isinstance(layout, str) and layout in {'horizontal', 'vertical'}:
        links['layout'] = layout

    links['items'] = CommentedSeq()

    raw_links = embeddable_attributes.get('links')
    if not isinstance(raw_links, list):
        return links

    for raw_link_item in raw_links:  # pyright: ignore[reportUnknownVariableType]
        raw_link = _as_dict(raw_link_item)  # pyright: ignore[reportUnknownArgumentType]
        if raw_link is None:
            continue

        options = _as_dict(raw_link.get('options'))
        if options is None:
            options = {}

        link_type = raw_link.get('type')
        if link_type == 'externalLink':
            link_item = _build_external_link_item(raw_link, options)
        elif link_type == 'dashboardLink':
            link_item = _build_dashboard_link_item(raw_link, options, reference_lookup)
        else:
            link_item = None

        if link_item is not None:
            links['items'].append(link_item)  # pyright: ignore[reportUnknownMemberType]

    return links


def _build_image_stub(panel: dict[str, Any]) -> CommentedMap:
    """Build image panel stub."""
    image = CommentedMap()
    embeddable_config = _as_dict(panel.get('embeddableConfig'))
    if embeddable_config is None:
        embeddable_config = {}

    image_config = _as_dict(embeddable_config.get('imageConfig'))
    if image_config is not None:
        src = _as_dict(image_config.get('src'))
        if src is not None:
            url = src.get('url')
            if isinstance(url, str):
                image['from_url'] = url

        sizing = _as_dict(image_config.get('sizing'))
        if sizing is not None:
            object_fit = sizing.get('objectFit')
            if isinstance(object_fit, str) and object_fit in {'contain', 'cover', 'fill', 'none'}:
                image['fit'] = object_fit

        description = image_config.get('altText')
        if isinstance(description, str) and len(description) > 0:
            image['description'] = description

        background_color = image_config.get('backgroundColor')
        if isinstance(background_color, str) and len(background_color) > 0:
            image['background_color'] = background_color

    if 'from_url' not in image:
        image['from_url'] = 'TODO_image_url'

    return image


def _build_vega_stub() -> CommentedMap:
    """Build vega panel stub."""
    vega = CommentedMap()
    vega['spec'] = CommentedMap()
    return vega


def _build_links_stub_from_panel(panel: dict[str, Any], reference_lookup: dict[str, str]) -> CommentedMap:
    """Adapter for simple builder dispatch."""
    return _build_links_stub(panel, reference_lookup)


def _build_image_stub_from_panel(panel: dict[str, Any], _reference_lookup: dict[str, str]) -> CommentedMap:
    """Adapter for simple builder dispatch."""
    return _build_image_stub(panel)


def _build_vega_stub_from_panel(_panel: dict[str, Any], _reference_lookup: dict[str, str]) -> CommentedMap:
    """Adapter for simple builder dispatch."""
    return _build_vega_stub()


_BuilderFn = Any  # Callable[[dict[str, Any], dict[str, str]], CommentedMap]


def _resolve_chart_type(vis_type_raw: object, embeddable_attributes: dict[str, Any]) -> str | None:
    """Resolve the final chart type from visualization type and state."""
    visualization_type = _normalize_lens_type(vis_type_raw)

    if isinstance(vis_type_raw, str) and vis_type_raw.lower() == 'lnsxy':
        return _resolve_xy_type(embeddable_attributes)

    if isinstance(vis_type_raw, str) and vis_type_raw.lower() in {'lnspie', 'pie'}:
        shape = _resolve_pie_shape(embeddable_attributes)
        if shape != 'pie':
            return shape

    return visualization_type


def _list_to_seq(items: list[CommentedMap]) -> CommentedSeq:
    """Convert a list of CommentedMaps to a CommentedSeq."""
    seq = CommentedSeq()
    for item in items:
        seq.append(item)  # pyright: ignore[reportUnknownMemberType]
    return seq


def _build_lens_like_stub(panel: dict[str, Any]) -> CommentedMap:  # noqa: PLR0912
    """Build lens/esql panel stub with chart type, data view, metrics, and dimensions."""
    _, embeddable_attributes = _extract_embeddable_attributes(panel)
    chart = CommentedMap()

    visualization_type = _resolve_chart_type(embeddable_attributes.get('visualizationType'), embeddable_attributes)
    if visualization_type is not None:
        chart['type'] = visualization_type

    data_view = _extract_data_view_from_references(panel)
    if data_view is not None:
        chart['data_view'] = data_view

    esql_query = _extract_esql_query(embeddable_attributes)
    if esql_query is not None:
        chart['query'] = esql_query

    metrics, dimensions, breakdowns, _skipped = _extract_form_based_columns(embeddable_attributes)

    is_xy = visualization_type in {'line', 'bar', 'area'}
    is_metric = visualization_type == 'metric'

    if is_metric:
        # Metric charts use primary/secondary, not metrics list
        if len(metrics) > 0:
            chart['primary'] = metrics[0]
        if len(metrics) > 1:
            chart['secondary'] = metrics[1]
    elif len(metrics) > 0:
        chart['metrics'] = _list_to_seq(metrics)

    if is_xy:
        # XY charts use singular dimension/breakdown, not lists
        if len(dimensions) > 0:
            chart['dimension'] = dimensions[0]
        if len(breakdowns) > 0:
            chart['breakdown'] = breakdowns[0]
    else:
        # Pie, table, etc. use plural dimensions
        if len(dimensions) > 0:
            chart['dimensions'] = _list_to_seq(dimensions)
        if len(breakdowns) > 0:
            chart['breakdown'] = _list_to_seq(breakdowns)

    return chart


def _panel_type_stub(panel: dict[str, Any], reference_lookup: dict[str, str]) -> tuple[str, CommentedMap]:
    """Build a minimal YAML panel type stub from a Kibana panel object."""
    panel_type = panel.get('type')
    simple_builders: dict[str, tuple[str, _BuilderFn]] = {
        'markdown': ('markdown', _build_markdown_stub),
        'search': ('search', _build_search_stub),
        'links': ('links', _build_links_stub_from_panel),
        'image': ('image', _build_image_stub_from_panel),
        'vega': ('vega', _build_vega_stub_from_panel),
    }

    if isinstance(panel_type, str) and panel_type in simple_builders:
        yaml_type, builder = simple_builders[panel_type]  # pyright: ignore[reportAny]
        result: CommentedMap = builder(panel, reference_lookup)  # pyright: ignore[reportAny]
        return yaml_type, result

    if panel_type in {'lens', 'esql'}:
        return str(panel_type), _build_lens_like_stub(panel)

    markdown = CommentedMap()
    markdown['content'] = f'TODO(decompile): unsupported panel type `{panel_type}`'
    return 'markdown', markdown


def _serialize_panel_comment(panel: dict[str, Any], panel_type: str) -> str:
    """Create TODO comment text for non-trivial panel config migration."""
    raw_panel_json = json.dumps(panel, indent=2, sort_keys=True)
    return f'TODO(decompile): complete `{panel_type}` panel config from original Kibana panel JSON.\nOriginal panel JSON:\n{raw_panel_json}'


def _build_panel_stub(panel: dict[str, Any], reference_lookup: dict[str, str]) -> tuple[CommentedMap, str]:
    """Build a single panel YAML stub and TODO comment from Kibana panel JSON."""
    panel_yaml = CommentedMap()

    panel_id = panel.get('panelIndex')
    if isinstance(panel_id, str):
        panel_yaml['id'] = panel_id

    panel_yaml['title'] = _extract_panel_title(panel)

    grid_data = _as_dict(panel.get('gridData'))
    if grid_data is not None:
        width = _to_int(grid_data.get('w'))
        height = _to_int(grid_data.get('h'))
        if width is not None or height is not None:
            size = CommentedMap()
            if width is not None:
                size['w'] = width
            if height is not None:
                size['h'] = height
            if hasattr(size, 'fa'):
                size.fa.set_flow_style()  # pyright: ignore[reportUnknownMemberType]
            panel_yaml['size'] = size

        x_pos = _to_int(grid_data.get('x'))
        y_pos = _to_int(grid_data.get('y'))
        if x_pos is not None or y_pos is not None:
            position = CommentedMap()
            if x_pos is not None:
                position['x'] = x_pos
            if y_pos is not None:
                position['y'] = y_pos
            if hasattr(position, 'fa'):
                position.fa.set_flow_style()  # pyright: ignore[reportUnknownMemberType]
            panel_yaml['position'] = position

    panel_type, panel_config = _panel_type_stub(panel, reference_lookup)
    panel_yaml[panel_type] = panel_config
    panel_comment = _serialize_panel_comment(panel, panel_type)
    return panel_yaml, panel_comment


def _extract_reference_lookup(dashboard: dict[str, Any]) -> dict[str, str]:
    """Extract dashboard references as a name->id lookup map."""
    reference_lookup: dict[str, str] = {}
    references = dashboard.get('references')
    if not isinstance(references, list):
        return reference_lookup

    for ref_item in references:  # pyright: ignore[reportUnknownVariableType]
        reference = _as_dict(ref_item)  # pyright: ignore[reportUnknownArgumentType]
        if reference is None:
            continue
        name = reference.get('name')
        target_id = reference.get('id')
        if isinstance(name, str) and isinstance(target_id, str):
            reference_lookup[name] = target_id

    return reference_lookup


def _extract_settings(attributes: dict[str, Any]) -> CommentedMap | None:
    """Extract trivially reversible dashboard settings from optionsJSON."""
    options = _parse_json_field(attributes.get('optionsJSON'))
    if not isinstance(options, dict):
        return None

    settings = CommentedMap()
    sync = CommentedMap()

    margins = options.get('useMargins')
    if isinstance(margins, bool):
        settings['margins'] = margins

    sync_colors = options.get('syncColors')
    if isinstance(sync_colors, bool):
        sync['colors'] = sync_colors

    sync_cursor = options.get('syncCursor')
    if isinstance(sync_cursor, bool):
        sync['cursor'] = sync_cursor

    sync_tooltips = options.get('syncTooltips')
    if isinstance(sync_tooltips, bool):
        sync['tooltips'] = sync_tooltips

    if len(sync) > 0:
        settings['sync'] = sync

    hide_panel_titles = options.get('hidePanelTitles')
    if isinstance(hide_panel_titles, bool):
        settings['titles'] = not hide_panel_titles

    if len(settings) == 0:
        return None
    return settings


def _extract_time_range(attributes: dict[str, Any]) -> CommentedMap | None:
    """Extract dashboard time range from simple dashboard attributes."""
    from_time = attributes.get('timeFrom')
    to_time = attributes.get('timeTo')

    if not isinstance(from_time, str) and not isinstance(to_time, str):
        return None

    time_range = CommentedMap()
    if isinstance(from_time, str):
        time_range['from'] = from_time
    if isinstance(to_time, str):
        time_range['to'] = to_time
    return time_range


_CONTROL_TYPE_MAP: dict[str, str] = {
    'optionsListControl': 'options',
    'rangeSliderControl': 'range',
    'timesliderControl': 'time',
}


def _build_control_stub(panel: dict[str, Any]) -> CommentedMap:
    """Build a single control stub from a controlGroupInput panel."""
    control = CommentedMap()
    panel_type = panel.get('type')
    if isinstance(panel_type, str):
        control['type'] = _CONTROL_TYPE_MAP.get(panel_type, f'TODO_control_type_{panel_type}')
    else:
        control['type'] = 'TODO_control_type_unknown'

    explicit_input = _as_dict(panel.get('explicitInput'))
    if explicit_input is not None:
        field_name = explicit_input.get('fieldName')
        if isinstance(field_name, str):
            control['field'] = field_name

        title = explicit_input.get('title')
        if isinstance(title, str):
            control['label'] = title

        data_view_id = explicit_input.get('dataViewId')
        if isinstance(data_view_id, str):
            control['data_view'] = data_view_id

    return control


def _extract_controls(attributes: dict[str, Any]) -> CommentedSeq | None:
    """Extract controls from controlGroupInput.panelsJSON."""
    control_group = _as_dict(attributes.get('controlGroupInput'))
    if control_group is None:
        return None

    panels_json = _parse_json_field(control_group.get('panelsJSON'))
    if not isinstance(panels_json, dict):
        return None

    controls = CommentedSeq()

    def _control_order(item: tuple[str, object]) -> int:
        """Extract order field for sorting controls."""
        panel = _as_dict(item[1])
        if panel is None:
            return 0
        order = panel.get('order', 0)
        return order if isinstance(order, int) else 0

    sorted_panels = sorted(
        panels_json.items(),  # pyright: ignore[reportUnknownMemberType]
        key=_control_order,
    )

    for _panel_id, panel_value in sorted_panels:  # pyright: ignore[reportUnknownVariableType]
        panel = _as_dict(panel_value)  # pyright: ignore[reportUnknownArgumentType]
        if panel is None:
            continue
        controls.append(_build_control_stub(panel))  # pyright: ignore[reportUnknownMemberType]

    if len(controls) == 0:
        return None
    return controls


def _build_phrase_filter(filter_meta: dict[str, Any], filter_key: str) -> CommentedMap:
    """Build a phrase filter stub."""
    f = CommentedMap()
    f['field'] = filter_key
    params = filter_meta.get('params')
    if isinstance(params, dict):
        query = params.get('query')  # pyright: ignore[reportUnknownMemberType]
        if isinstance(query, str):
            f['equals'] = query
        elif query is not None:
            f['equals'] = str(query)  # pyright: ignore[reportUnknownArgumentType]
    else:
        value = filter_meta.get('value')
        if isinstance(value, str):
            f['equals'] = value
    return f


def _build_phrases_filter(filter_meta: dict[str, Any], filter_key: str) -> CommentedMap:
    """Build a phrases (in) filter stub."""
    f = CommentedMap()
    f['field'] = filter_key
    params = filter_meta.get('params')
    if isinstance(params, list):
        in_list = CommentedSeq()
        for p in params:  # pyright: ignore[reportUnknownVariableType]
            if isinstance(p, str):
                in_list.append(p)  # pyright: ignore[reportUnknownMemberType]
            elif p is not None:  # pyright: ignore[reportUnknownArgumentType]
                in_list.append(str(p))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        f['in'] = in_list
    return f


def _build_range_filter(raw_filter: dict[str, Any], filter_key: str) -> CommentedMap:
    """Build a range filter stub."""
    f = CommentedMap()
    f['field'] = filter_key
    range_params = _as_dict(raw_filter.get('range'))
    if range_params is not None:
        field_range = _as_dict(range_params.get(filter_key))
        if field_range is not None:
            for bound in ('gte', 'gt', 'lte', 'lt'):
                val = field_range.get(bound)
                if val is not None:
                    f[bound] = str(val)
    return f


def _apply_filter_metadata(f: CommentedMap, filter_meta: dict[str, Any]) -> None:
    """Apply disabled and alias metadata to a filter stub."""
    disabled = filter_meta.get('disabled')
    if isinstance(disabled, bool) and disabled:
        f['disabled'] = True

    alias = filter_meta.get('alias')
    if isinstance(alias, str) and len(alias) > 0:
        f['alias'] = alias


def _build_single_filter(raw_filter: dict[str, Any], filter_meta: dict[str, Any], filter_key: str) -> CommentedMap:
    """Build a single filter stub based on filter type."""
    filter_type = filter_meta.get('type')

    if filter_type == 'phrase':
        f = _build_phrase_filter(filter_meta, filter_key)
    elif filter_type == 'phrases':
        f = _build_phrases_filter(filter_meta, filter_key)
    elif filter_type == 'range':
        f = _build_range_filter(raw_filter, filter_key)
    else:
        f = CommentedMap()
        f['field'] = filter_key

    _apply_filter_metadata(f, filter_meta)
    return f


def _extract_filters(attributes: dict[str, Any]) -> CommentedSeq | None:
    """Extract dashboard-level filters from kibanaSavedObjectMeta.searchSourceJSON."""
    meta = _as_dict(attributes.get('kibanaSavedObjectMeta'))
    if meta is None:
        return None

    search_source = _parse_json_field(meta.get('searchSourceJSON'))
    if not isinstance(search_source, dict):
        return None

    raw_filters = search_source.get('filter')
    if not isinstance(raw_filters, list):
        return None

    filters = CommentedSeq()
    for filter_item in raw_filters:  # pyright: ignore[reportUnknownVariableType]
        raw_filter = _as_dict(filter_item)  # pyright: ignore[reportUnknownArgumentType]
        if raw_filter is None:
            continue

        filter_meta = _as_dict(raw_filter.get('meta'))
        if filter_meta is None:
            continue

        filter_key = filter_meta.get('key')
        if not isinstance(filter_key, str):
            continue

        if filter_meta.get('type') == 'exists':
            f_exists = CommentedMap()
            f_exists['exists'] = filter_key
            _apply_filter_metadata(f_exists, filter_meta)
            filters.append(f_exists)  # pyright: ignore[reportUnknownMemberType]
            continue

        filters.append(_build_single_filter(raw_filter, filter_meta, filter_key))  # pyright: ignore[reportUnknownMemberType]

    if len(filters) == 0:
        return None
    return filters


def decompile_dashboard(dashboard: dict[str, Any]) -> CommentedMap:
    """Convert a Kibana dashboard object into a YAML stub document."""
    attributes = _as_dict(dashboard.get('attributes'))
    if attributes is None:
        attributes = {}

    document = CommentedMap()
    dashboards = CommentedSeq()
    document['dashboards'] = dashboards

    dashboard_yaml = CommentedMap()
    dashboards.append(dashboard_yaml)  # pyright: ignore[reportUnknownMemberType]

    title = attributes.get('title')
    if isinstance(title, str):
        dashboard_yaml['name'] = title
    else:
        dashboard_yaml['name'] = 'Untitled Dashboard'

    dashboard_id = dashboard.get('id')
    if isinstance(dashboard_id, str):
        dashboard_yaml['id'] = dashboard_id

    description = attributes.get('description')
    if isinstance(description, str):
        dashboard_yaml['description'] = description

    settings = _extract_settings(attributes)
    if settings is not None:
        dashboard_yaml['settings'] = settings

    time_range = _extract_time_range(attributes)
    if time_range is not None:
        dashboard_yaml['time_range'] = time_range

    filters = _extract_filters(attributes)
    if filters is not None:
        dashboard_yaml['filters'] = filters

    controls = _extract_controls(attributes)
    if controls is not None:
        dashboard_yaml['controls'] = controls

    panels = CommentedSeq()
    reference_lookup = _extract_reference_lookup(dashboard)
    panels_json = _parse_json_field(attributes.get('panelsJSON'))
    if isinstance(panels_json, list):
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = _as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is None:
                continue
            panel_stub, panel_comment = _build_panel_stub(panel, reference_lookup)
            panels.append(panel_stub)  # pyright: ignore[reportUnknownMemberType]
            panel_index = len(panels) - 1
            panels.yaml_set_comment_before_after_key(panel_index, before=panel_comment)  # pyright: ignore[reportUnknownMemberType]
    dashboard_yaml['panels'] = panels

    return document
