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
    'datatable': 'datatable',
    'tagcloud': 'tagcloud',
    'mosaic': 'mosaic',
    'waffle': 'waffle',
    'lnsmetric': 'metric',
    'lnsgauge': 'gauge',
    'lnspie': 'pie',
    'lnsheatmap': 'heatmap',
    'lnsdatatable': 'datatable',
    'lnstagcloud': 'tagcloud',
    'lnsmosaic': 'mosaic',
    'lnswaffle': 'waffle',
}


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


def _build_lens_like_stub(panel: dict[str, Any]) -> CommentedMap:
    """Build lens/esql panel stub with optional chart type."""
    _, embeddable_attributes = _extract_embeddable_attributes(panel)
    chart = CommentedMap()
    visualization_type = _normalize_lens_type(embeddable_attributes.get('visualizationType'))
    if visualization_type is not None:
        chart['type'] = visualization_type
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
