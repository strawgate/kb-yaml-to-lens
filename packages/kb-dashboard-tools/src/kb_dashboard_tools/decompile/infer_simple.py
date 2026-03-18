"""Simple panel builders for non-Lens panel types.

Handles inference of markdown, search, image, links, and vega panels
from parsed Kibana panel structures into YAML-ready config dicts.
"""

from typing import Any

from .parse import (
    ParsedSimplePanel,
)
from .parse_shared import (
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_list,
    get_nested,
    get_str,
)

__all__ = ['_SIMPLE_PANEL_BUILDERS']


def _infer_markdown_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer markdown panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    content = get_str(ec, 'markdown')
    if content is None:
        params = get_nested(ec, 'savedVis', 'params')
        if params is not None:
            content = get_str(params, 'markdown')

    config['content'] = content if content is not None else 'TODO(decompile): provide markdown content'

    params = get_nested(ec, 'savedVis', 'params')
    if params is not None:
        font_size = get_int(params, 'fontSize')
        if font_size is not None:
            config['font_size'] = font_size
        links_in_new_tab = get_bool(params, 'openLinksInNewTab')
        if links_in_new_tab is not None:
            config['links_in_new_tab'] = links_in_new_tab

    return config


def _infer_search_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer search panel config from parsed simple panel."""
    panel = simple.raw
    saved_search_id = get_str(panel, 'savedSearchId')
    if saved_search_id is not None:
        return {'saved_search_id': saved_search_id}

    ec = get_dict(panel, 'embeddableConfig')
    if ec is not None:
        ref_name = get_str(ec, 'savedSearchRefName')
        if ref_name is not None:
            resolved = get_str(ref_lookup, ref_name)
            if resolved is not None:
                return {'saved_search_id': resolved}

    return {'saved_search_id': 'TODO_saved_search_id'}


def _infer_image_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer image panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    image_config = get_dict(ec, 'imageConfig')
    if image_config is not None:
        src = get_dict(image_config, 'src')
        if src is not None:
            url = get_str(src, 'url')
            if url is not None:
                config['from_url'] = url
        sizing = get_dict(image_config, 'sizing')
        if sizing is not None:
            fit = get_str(sizing, 'objectFit')
            if fit is not None and fit in {'contain', 'cover', 'fill', 'none'}:
                config['fit'] = fit
        alt = get_str(image_config, 'altText')
        if alt is not None and len(alt) > 0:
            config['description'] = alt
        bg = get_str(image_config, 'backgroundColor')
        if bg is not None and len(bg) > 0:
            config['background_color'] = bg

    if 'from_url' not in config:
        config['from_url'] = 'TODO_image_url'
    return config


def _build_link_common(raw_link: dict[str, Any]) -> dict[str, Any]:
    """Extract common link fields (id, label) shared by external and dashboard links."""
    item: dict[str, Any] = {}
    link_id = get_str(raw_link, 'id')
    if link_id is not None:
        item['id'] = link_id
    label = get_str(raw_link, 'label')
    if label is not None:
        item['label'] = label
    return item


def _infer_links_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer links panel config from parsed simple panel."""
    attrs = simple.embeddable_attributes
    if not attrs:
        attrs = get_dict(simple.embeddable_config, 'attributes') or {}

    config: dict[str, Any] = {}
    layout = get_str(attrs, 'layout')
    if layout is not None and layout in {'horizontal', 'vertical'}:
        config['layout'] = layout

    items: list[dict[str, Any]] = []
    raw_links = get_list(attrs, 'links')
    if raw_links is not None:
        for raw_item in raw_links:
            raw_link = as_dict(raw_item)
            if raw_link is None:
                continue
            options = get_dict(raw_link, 'options') or {}
            link_type = get_str(raw_link, 'type')

            if link_type == 'externalLink':
                dest = get_str(raw_link, 'destination')
                if dest is None:
                    continue
                item = _build_link_common(raw_link)
                item['url'] = dest
                new_tab = get_bool(options, 'openInNewTab')
                if new_tab is not None:
                    item['new_tab'] = new_tab
                encode = get_bool(options, 'encodeUrl')
                if encode is not None:
                    item['encode'] = encode
                items.append(item)

            elif link_type == 'dashboardLink':
                dest_ref = get_str(raw_link, 'destinationRefName')
                if dest_ref is None:
                    continue
                item = _build_link_common(raw_link)
                dashboard_id = get_str(ref_lookup, dest_ref)
                item['dashboard'] = dashboard_id if dashboard_id is not None else f'TODO_dashboard_id_for_{dest_ref}'
                new_tab = get_bool(options, 'openInNewTab')
                if new_tab is not None:
                    item['new_tab'] = new_tab
                with_time = get_bool(options, 'useCurrentDateRange')
                if with_time is not None:
                    item['with_time'] = with_time
                with_filters = get_bool(options, 'useCurrentFilters')
                if with_filters is not None:
                    item['with_filters'] = with_filters
                items.append(item)

    config['items'] = items
    return config


def _infer_vega_panel(_simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer vega panel config (stub -- spec must be provided manually)."""
    return {'spec': {}}


type _SimplePanelBuilder = Any  # Callable[[ParsedSimplePanel, dict[str, str]], dict[str, Any]]

_SIMPLE_PANEL_BUILDERS: dict[str, _SimplePanelBuilder] = {
    'markdown': _infer_markdown_panel,
    'search': _infer_search_panel,
    'links': _infer_links_panel,
    'image': _infer_image_panel,
    'vega': _infer_vega_panel,
}
