"""Phase 2: Infer Dashboard config objects from parsed intermediate structures.

Maps parsed Kibana/Kbn view data to actual kb-dashboard-core config models,
producing dicts that can be validated into ``Dashboard`` instances.

Chart-specific logic is delegated to sub-modules:
- ``infer_lens``: Lens / ES|QL chart inference
- ``infer_simple``: Simple panel builders (markdown, search, image, links, vega)
"""

import logging
from typing import Any

from kb_dashboard_core.dashboard.config import Dashboard

from .infer_lens import _infer_lens_chart  # pyright: ignore[reportPrivateUsage]
from .infer_simple import _SIMPLE_PANEL_BUILDERS  # pyright: ignore[reportPrivateUsage]
from .parse import (
    ParsedControl,
    ParsedDashboard,
    ParsedFilter,
    ParsedPanel,
)
from .parse_shared import (
    get_bool,
    get_dict,
    get_list,
    get_str,
)
from .tables import (
    CONTROL_TYPE_MAP,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dashboard-level inference
# ---------------------------------------------------------------------------


def _infer_settings(parsed: ParsedDashboard) -> dict[str, Any] | None:
    """Infer dashboard-level settings (margins, sync options, panel titles)."""
    s = parsed.settings
    if s is None:
        return None
    settings: dict[str, Any] = {}
    sync: dict[str, Any] = {}
    if s.margins is not None:
        settings['margins'] = s.margins
    if s.sync_colors is not None:
        sync['colors'] = s.sync_colors
    if s.sync_cursor is not None:
        sync['cursor'] = s.sync_cursor
    if s.sync_tooltips is not None:
        sync['tooltips'] = s.sync_tooltips
    if sync:
        settings['sync'] = sync
    if s.hide_panel_titles is not None:
        settings['titles'] = not s.hide_panel_titles
    return settings if settings else None


def _infer_time_range(parsed: ParsedDashboard) -> dict[str, str] | None:
    """Infer dashboard time range from parsed from/to values."""
    if parsed.time_from is None and parsed.time_to is None:
        return None
    tr: dict[str, str] = {}
    if parsed.time_from is not None:
        tr['from'] = parsed.time_from
    if parsed.time_to is not None:
        tr['to'] = parsed.time_to
    return tr


def _infer_filter(pf: ParsedFilter) -> dict[str, Any] | None:
    """Infer a single filter config dict. Returns None for unrecognized filter types."""
    f: dict[str, Any] = {}
    if pf.filter_type == 'exists':
        f['exists'] = pf.key
    elif pf.filter_type == 'phrase':
        f['field'] = pf.key
        params = get_dict(pf.meta, 'params')
        if params is not None:
            query = params.get('query')
            if isinstance(query, (str, int, float, bool)):
                f['equals'] = query
        else:
            value = pf.meta.get('value')
            if isinstance(value, (str, int, float, bool)):
                f['equals'] = value
    elif pf.filter_type == 'phrases':
        f['field'] = pf.key
        params = get_list(pf.meta, 'params')
        if params is not None:
            f['in'] = [p for p in params if isinstance(p, (str, int, float, bool))]
    elif pf.filter_type == 'range':
        f['field'] = pf.key
        range_params = get_dict(pf.raw, 'range')
        if range_params is not None:
            field_range = get_dict(range_params, pf.key)
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = field_range.get(bound)
                    if isinstance(val, (str, int, float, bool)):
                        f[bound] = val
    else:
        # Unrecognized filter type — skip rather than emit an unvalidatable shape
        return None

    # Apply metadata
    disabled = get_bool(pf.meta, 'disabled')
    if disabled is not None and disabled:
        f['disabled'] = True
    alias = get_str(pf.meta, 'alias')
    if alias is not None and len(alias) > 0:
        f['alias'] = alias

    return f


def _infer_control(pc: ParsedControl) -> dict[str, Any]:
    """Infer a single control config dict."""
    ctrl: dict[str, Any] = {}
    if pc.control_type is not None:
        ctrl['type'] = CONTROL_TYPE_MAP.get(pc.control_type, f'TODO_control_type_{pc.control_type}')
    else:
        ctrl['type'] = 'TODO_control_type_unknown'
    if pc.field_name is not None:
        ctrl['field'] = pc.field_name
    if pc.title is not None:
        ctrl['label'] = pc.title
    # data_view is required for options and range controls
    resolved_type = ctrl.get('type')
    if resolved_type in {'options', 'range'}:
        ctrl['data_view'] = pc.data_view_id if pc.data_view_id is not None else 'TODO_data_view'
    elif pc.data_view_id is not None:
        ctrl['data_view'] = pc.data_view_id
    return ctrl


def _infer_panel(panel: ParsedPanel, ref_lookup: dict[str, str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Infer panel config. Returns (panel_type_key, chart_config_dict, panel_wrapper_dict).

    The panel_wrapper_dict contains id, title, size, position.
    The chart_config_dict is nested under the panel_type_key.
    """
    wrapper: dict[str, Any] = {}
    if panel.panel_index is not None:
        wrapper['id'] = panel.panel_index
    wrapper['title'] = panel.title
    if panel.hide_title is True:
        wrapper['hide_title'] = True
    if panel.description is not None and len(panel.description) > 0:
        wrapper['description'] = panel.description

    if panel.grid is not None:
        g = panel.grid
        if g.w is not None or g.h is not None:
            size: dict[str, int] = {}
            if g.w is not None:
                size['w'] = g.w
            if g.h is not None:
                size['h'] = g.h
            wrapper['size'] = size
        if g.x is not None or g.y is not None:
            pos: dict[str, int] = {}
            if g.x is not None:
                pos['x'] = g.x
            if g.y is not None:
                pos['y'] = g.y
            wrapper['position'] = pos

    # Error fallback
    if panel.error is not None:
        return 'markdown', {'content': f'TODO(decompile): {panel.error}'}, wrapper

    # Lens/ESQL panel
    if panel.lens is not None:
        chart = _infer_lens_chart(panel.lens)
        return panel.lens.panel_type, chart, wrapper

    # Simple panels
    if panel.simple is not None:
        builder = _SIMPLE_PANEL_BUILDERS.get(panel.simple.panel_type)
        if builder is not None:
            config = builder(panel.simple, ref_lookup)  # pyright: ignore[reportAny]
            return panel.simple.panel_type, config, wrapper
        # Unsupported type
        return 'markdown', {'content': f'TODO(decompile): unsupported panel type `{panel.simple.panel_type}`'}, wrapper

    return 'markdown', {'content': 'TODO(decompile): empty panel'}, wrapper


def infer_dashboard(parsed: ParsedDashboard) -> tuple[Dashboard, list[dict[str, Any]]]:
    """Infer a Dashboard config model from parsed dashboard data.

    Returns:
        Tuple of (dashboard_model, panel_originals) where dashboard_model is an
        actual ``kb_dashboard_core.dashboard.config.Dashboard`` instance.
    """
    dashboard: dict[str, Any] = {
        'name': parsed.title,
    }
    if parsed.dashboard_id is not None:
        dashboard['id'] = parsed.dashboard_id
    if parsed.description is not None:
        dashboard['description'] = parsed.description

    settings = _infer_settings(parsed)
    if settings is not None:
        dashboard['settings'] = settings

    time_range = _infer_time_range(parsed)
    if time_range is not None:
        dashboard['time_range'] = time_range

    if parsed.filters:
        inferred_filters = [_infer_filter(f) for f in parsed.filters]
        valid_filters = [f for f in inferred_filters if f is not None]
        if valid_filters:
            dashboard['filters'] = valid_filters

    if parsed.controls:
        dashboard['controls'] = [_infer_control(c) for c in parsed.controls]

    if parsed.query is not None:
        dashboard['query'] = parsed.query

    panels: list[dict[str, Any]] = []
    for panel in parsed.panels:
        panel_type, chart_config, wrapper = _infer_panel(panel, parsed.reference_lookup)
        wrapper[panel_type] = chart_config
        panels.append(wrapper)

    dashboard['panels'] = panels
    return Dashboard.model_validate(dashboard), []
