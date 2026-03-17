"""Simple panel builders for non-Lens panel types.

Handles inference of markdown, search, image, links, and vega panels
from parsed Kibana panel structures into YAML-ready config dicts.
"""

from typing import Any

from .parse import (
    ParsedSimplePanel,
    as_dict,
)

__all__ = ['_SIMPLE_PANEL_BUILDERS']


def _infer_markdown_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer markdown panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    content = ec.get('markdown')
    if not isinstance(content, str):
        saved_vis = as_dict(ec.get('savedVis'))
        if saved_vis is not None:
            params = as_dict(saved_vis.get('params'))
            if params is not None:
                content = params.get('markdown')

    config['content'] = content if isinstance(content, str) else 'TODO(decompile): provide markdown content'

    saved_vis = as_dict(ec.get('savedVis'))
    if saved_vis is not None:
        params = as_dict(saved_vis.get('params'))
        if params is not None:
            font_size = params.get('fontSize')
            if isinstance(font_size, int):
                config['font_size'] = font_size
            links_in_new_tab = params.get('openLinksInNewTab')
            if isinstance(links_in_new_tab, bool):
                config['links_in_new_tab'] = links_in_new_tab

    return config


def _infer_search_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer search panel config from parsed simple panel."""
    panel = simple.raw
    saved_search_id = panel.get('savedSearchId')
    if isinstance(saved_search_id, str):
        return {'saved_search_id': saved_search_id}

    ec = as_dict(panel.get('embeddableConfig'))
    if ec is not None:
        ref_name = ec.get('savedSearchRefName')
        if isinstance(ref_name, str):
            resolved = ref_lookup.get(ref_name)
            if isinstance(resolved, str):
                return {'saved_search_id': resolved}

    return {'saved_search_id': 'TODO_saved_search_id'}


def _infer_image_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer image panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    image_config = as_dict(ec.get('imageConfig'))
    if image_config is not None:
        src = as_dict(image_config.get('src'))
        if src is not None:
            url = src.get('url')
            if isinstance(url, str):
                config['from_url'] = url
        sizing = as_dict(image_config.get('sizing'))
        if sizing is not None:
            fit = sizing.get('objectFit')
            if isinstance(fit, str) and fit in {'contain', 'cover', 'fill', 'none'}:
                config['fit'] = fit
        alt = image_config.get('altText')
        if isinstance(alt, str) and len(alt) > 0:
            config['description'] = alt
        bg = image_config.get('backgroundColor')
        if isinstance(bg, str) and len(bg) > 0:
            config['background_color'] = bg

    if 'from_url' not in config:
        config['from_url'] = 'TODO_image_url'
    return config


def _build_link_common(raw_link: dict[str, Any]) -> dict[str, Any]:
    """Extract common link fields (id, label) shared by external and dashboard links."""
    item: dict[str, Any] = {}
    link_id = raw_link.get('id')
    if isinstance(link_id, str):
        item['id'] = link_id
    label = raw_link.get('label')
    if isinstance(label, str):
        item['label'] = label
    return item


def _infer_links_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer links panel config from parsed simple panel."""
    attrs = simple.embeddable_attributes
    if not attrs:
        attrs = as_dict(simple.embeddable_config.get('attributes')) or {}

    config: dict[str, Any] = {}
    layout = attrs.get('layout')
    if isinstance(layout, str) and layout in {'horizontal', 'vertical'}:
        config['layout'] = layout

    items: list[dict[str, Any]] = []
    raw_links = attrs.get('links')
    if isinstance(raw_links, list):
        for raw_item in raw_links:  # pyright: ignore[reportUnknownVariableType]
            raw_link = as_dict(raw_item)  # pyright: ignore[reportUnknownArgumentType]
            if raw_link is None:
                continue
            options = as_dict(raw_link.get('options')) or {}
            link_type = raw_link.get('type')

            if link_type == 'externalLink':
                dest = raw_link.get('destination')
                if not isinstance(dest, str):
                    continue
                item = _build_link_common(raw_link)
                item['url'] = dest
                new_tab = options.get('openInNewTab')
                if isinstance(new_tab, bool):
                    item['new_tab'] = new_tab
                encode = options.get('encodeUrl')
                if isinstance(encode, bool):
                    item['encode'] = encode
                items.append(item)

            elif link_type == 'dashboardLink':
                dest_ref = raw_link.get('destinationRefName')
                if not isinstance(dest_ref, str):
                    continue
                item = _build_link_common(raw_link)
                dashboard_id = ref_lookup.get(dest_ref)
                item['dashboard'] = dashboard_id if isinstance(dashboard_id, str) else f'TODO_dashboard_id_for_{dest_ref}'
                new_tab = options.get('openInNewTab')
                if isinstance(new_tab, bool):
                    item['new_tab'] = new_tab
                with_time = options.get('useCurrentDateRange')
                if isinstance(with_time, bool):
                    item['with_time'] = with_time
                with_filters = options.get('useCurrentFilters')
                if isinstance(with_filters, bool):
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
