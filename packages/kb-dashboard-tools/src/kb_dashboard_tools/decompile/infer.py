"""Phase 2: Infer Dashboard config objects from a KbnDashboard view model.

Maps parsed Kibana/Kbn view data to actual kb-dashboard-core config models,
producing dicts that can be validated into ``Dashboard`` instances.

Chart-specific logic is delegated to sub-modules:
- ``infer_lens``: Lens / ES|QL chart inference
- ``infer_simple``: Simple panel builders (markdown, search, image, links, vega)
"""

import logging
from typing import Any

from kb_dashboard_core.controls.config import ControlTypes
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.filters.config import FilterTypes
from pydantic import TypeAdapter, ValidationError

from .infer_lens import _infer_lens_chart  # pyright: ignore[reportPrivateUsage]
from .infer_simple import _SIMPLE_PANEL_BUILDERS, _resolve_simple_panel_type  # pyright: ignore[reportPrivateUsage]
from .kbn_raw_models.dashboard.view import KbnDashboard
from .kbn_raw_models.panels.view import KbnBasePanel
from .parse_shared import (
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_scalar,
    get_str,
)
from .tables import (
    CONTROL_TYPE_MAP,
)

logger = logging.getLogger(__name__)

_filter_adapter: TypeAdapter[FilterTypes] = TypeAdapter(FilterTypes)
_control_adapter: TypeAdapter[ControlTypes] = TypeAdapter(ControlTypes)

# ---------------------------------------------------------------------------
# Dashboard-level inference helpers
# ---------------------------------------------------------------------------


def _infer_settings(kbn: KbnDashboard) -> dict[str, Any] | None:
    """Infer dashboard-level settings (margins, sync options, panel titles)."""
    attrs = kbn.attributes
    if attrs is None:
        return None
    opts = attrs.optionsJSON
    if opts is None:
        return None
    settings: dict[str, Any] = {}
    sync: dict[str, Any] = {}
    if opts.useMargins is not None:
        settings['margins'] = opts.useMargins
    if opts.syncColors is not None:
        sync['colors'] = opts.syncColors
    if opts.syncCursor is not None:
        sync['cursor'] = opts.syncCursor
    if opts.syncTooltips is not None:
        sync['tooltips'] = opts.syncTooltips
    if sync:
        settings['sync'] = sync
    if opts.hidePanelTitles is not None:
        settings['titles'] = not opts.hidePanelTitles
    return settings if settings else None


def _infer_time_range(kbn: KbnDashboard) -> dict[str, str] | None:
    """Infer dashboard time range from timeFrom/timeTo attributes."""
    attrs = kbn.attributes
    if attrs is None:
        return None
    time_from = attrs.timeFrom
    time_to = attrs.timeTo
    if time_from is None and time_to is None:
        return None
    tr: dict[str, str] = {}
    if time_from is not None:
        tr['from'] = time_from
    if time_to is not None:
        tr['to'] = time_to
    return tr


def _infer_query(kbn: KbnDashboard) -> dict[str, str] | None:
    """Infer dashboard query from kibanaSavedObjectMeta."""
    attrs = kbn.attributes
    meta = attrs.kibanaSavedObjectMeta if attrs is not None else None
    search_source = meta.searchSourceJSON if meta is not None else None
    q = search_source.query if search_source is not None else None
    query_str = q.query if q is not None else None
    language = q.language if q is not None else None
    if query_str is None:
        return None
    if language == 'kuery':
        return {'kql': query_str}
    if language == 'lucene':
        return {'lucene': query_str}
    return None


def _build_reference_lookup(kbn: KbnDashboard, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Build a name→id lookup from the dashboard references list.

    ``extra`` is merged in first so KbnDashboard refs (which are validated and
    complete) take precedence over the raw fallback.
    """
    lookup: dict[str, str] = dict(extra) if extra else {}
    for ref in kbn.references:
        lookup[ref.name] = ref.id
    return lookup


# ---------------------------------------------------------------------------
# Filter inference
# ---------------------------------------------------------------------------


def _infer_filter_from_raw(raw_filter: dict[str, Any]) -> dict[str, Any] | None:
    """Infer a single filter config dict from a raw filter dict. Returns None for unrecognized types."""
    meta = get_dict(raw_filter, 'meta')
    if meta is None:
        return None

    filter_type = get_str(meta, 'type')
    key = get_str(meta, 'key')
    if key is None:
        return None

    f: dict[str, Any] = {}

    if filter_type == 'exists':
        f['exists'] = key
    elif filter_type == 'phrase':
        f['field'] = key
        params = get_dict(meta, 'params')
        if params is not None:
            query = get_scalar(params, 'query')
            if query is not None:
                f['equals'] = query
        else:
            value = get_scalar(meta, 'value')
            if value is not None:
                f['equals'] = value
    elif filter_type == 'phrases':
        f['field'] = key
        params_raw = meta.get('params')
        if isinstance(params_raw, list):
            f['in'] = [p for p in params_raw if isinstance(p, (str, int, float, bool))]  # pyright: ignore[reportUnknownVariableType]
    elif filter_type == 'range':
        f['field'] = key
        # Range bounds are stored in a top-level 'range' key on the raw filter dict
        range_params = get_dict(raw_filter, 'range')
        if range_params is not None:
            field_range = get_dict(range_params, key)
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = get_scalar(field_range, bound)
                    if val is not None:
                        f[bound] = val
    else:
        return None

    # Apply metadata
    disabled = get_bool(meta, 'disabled')
    if disabled is not None and disabled:
        f['disabled'] = True
    alias = get_str(meta, 'alias')
    if alias is not None and len(alias) > 0:
        f['alias'] = alias

    _ = _filter_adapter.validate_python(f)
    return f


# ---------------------------------------------------------------------------
# Control inference
# ---------------------------------------------------------------------------


def _resolve_control_data_view(
    control_type: str | None,
    panel_id: str,
    explicit_input: dict[str, Any],
    reference_lookup: dict[str, str],
) -> str | None:
    """Resolve data view ID for a control panel."""
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
    return reference_lookup.get(ref_name)


def _infer_control_from_dict(
    panel_id: str,
    panel_dict: dict[str, Any],
    reference_lookup: dict[str, str],
) -> dict[str, Any]:
    """Infer a single control config dict from a raw control panel dict."""
    ctrl: dict[str, Any] = {}
    control_type = get_str(panel_dict, 'type')
    if control_type is not None:
        ctrl['type'] = CONTROL_TYPE_MAP.get(control_type, f'TODO_control_type_{control_type}')
    else:
        ctrl['type'] = 'TODO_control_type_unknown'

    explicit_input = get_dict(panel_dict, 'explicitInput') or {}
    field_name = get_str(explicit_input, 'fieldName')
    title = get_str(explicit_input, 'title')
    data_view_id = _resolve_control_data_view(control_type, panel_id, explicit_input, reference_lookup)

    if field_name is not None:
        ctrl['field'] = field_name
    if title is not None:
        ctrl['label'] = title

    resolved_type = ctrl.get('type')
    if resolved_type in {'options', 'range'}:
        ctrl['data_view'] = data_view_id if data_view_id is not None else 'TODO_data_view'
    elif data_view_id is not None:
        ctrl['data_view'] = data_view_id

    _ = _control_adapter.validate_python(ctrl)
    return ctrl


# ---------------------------------------------------------------------------
# Panel inference
# ---------------------------------------------------------------------------


def _parse_panel_title(panel_dict: dict[str, Any]) -> str:
    """Extract panel title from a raw panel dict."""
    title = get_str(panel_dict, 'title')
    if title is not None:
        return title
    ec = get_dict(panel_dict, 'embeddableConfig') or {}
    ec_title = get_str(ec, 'title')
    if ec_title is not None:
        return ec_title
    return ''


def _infer_panel(panel_dict: dict[str, Any], ref_lookup: dict[str, str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Infer panel config. Returns (panel_type_key, chart_config_dict, panel_wrapper_dict).

    The panel_wrapper_dict contains id, title, size, position.
    The chart_config_dict is nested under the panel_type_key.
    """
    kbn_panel = KbnBasePanel.model_validate(panel_dict)
    wrapper: dict[str, Any] = {}

    if kbn_panel.panelIndex is not None:
        wrapper['id'] = kbn_panel.panelIndex
    wrapper['title'] = _parse_panel_title(panel_dict)

    ec = get_dict(panel_dict, 'embeddableConfig') or {}
    hide_panel_titles = get_bool(ec, 'hidePanelTitles')
    if hide_panel_titles is True:
        wrapper['hide_title'] = True
    panel_description = get_str(ec, 'description')
    if panel_description is None:
        panel_description = get_str(panel_dict, 'description')
    if panel_description is not None and len(panel_description) > 0:
        wrapper['description'] = panel_description

    grid = kbn_panel.gridData
    if grid is not None:
        if grid.w is not None or grid.h is not None:
            size: dict[str, int] = {}
            if grid.w is not None:
                size['w'] = grid.w
            if grid.h is not None:
                size['h'] = grid.h
            wrapper['size'] = size
        if grid.x is not None or grid.y is not None:
            pos: dict[str, int] = {}
            if grid.x is not None:
                pos['x'] = grid.x
            if grid.y is not None:
                pos['y'] = grid.y
            wrapper['position'] = pos

    panel_type = get_str(panel_dict, 'type')

    # Check for unresolved panel reference
    panel_ref_name = get_str(panel_dict, 'panelRefName')
    if panel_ref_name is not None and get_dict(ec, 'attributes') is None:
        return 'markdown', {'content': f'TODO(decompile): unresolved panel reference: {panel_ref_name}'}, wrapper

    if panel_type is None:
        return 'markdown', {'content': 'TODO(decompile): missing panel type'}, wrapper

    # Lens/ESQL panel
    if panel_type in ('lens', 'esql'):
        try:
            inferred_type, chart = _infer_lens_chart(panel_dict)
        except (ValueError, ValidationError) as exc:
            logger.warning('_infer_lens_chart validation failed for panel %s: %s', wrapper.get('id'), exc)
            return 'markdown', {'content': f'TODO(decompile): panel validation failed: {exc}'}, wrapper
        return inferred_type, chart, wrapper

    # Simple panels
    resolved_type = _resolve_simple_panel_type(panel_dict)
    builder = _SIMPLE_PANEL_BUILDERS.get(resolved_type)
    if builder is not None:
        config = builder(panel_dict, ref_lookup)  # pyright: ignore[reportAny]
        return resolved_type, config, wrapper

    # Unsupported type
    return 'markdown', {'content': f'TODO(decompile): unsupported panel type `{panel_type}`'}, wrapper


# ---------------------------------------------------------------------------
# Controls iteration
# ---------------------------------------------------------------------------


def _iter_controls(kbn: KbnDashboard) -> list[tuple[str, dict[str, Any]]]:
    """Yield (panel_id, panel_dict) tuples for controls, sorted by order."""
    attrs = kbn.attributes
    if attrs is None:
        return []
    control_group = attrs.controlGroupInput
    if control_group is None:
        return []
    panels_json = control_group.panelsJSON
    if panels_json is None:
        return []

    def _order(item: tuple[str, object]) -> int:
        panel = as_dict(item[1]) if not isinstance(item[1], dict) else item[1]  # pyright: ignore[reportUnknownVariableType]
        return (get_int(panel, 'order') or 0) if panel is not None else 0  # pyright: ignore[reportUnknownArgumentType]

    result: list[tuple[str, dict[str, Any]]] = []
    for panel_id, panel_value in sorted(panels_json.root.items(), key=_order):
        panel = panel_value.model_dump(exclude_none=True) if hasattr(panel_value, 'model_dump') else as_dict(panel_value)
        if panel is not None:
            result.append((panel_id, panel))
    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def infer_dashboard(
    kbn: KbnDashboard,
    raw_reference_lookup: dict[str, str] | None = None,
    raw_filters: list[dict[str, Any]] | None = None,
) -> tuple[Dashboard, list[dict[str, Any]]]:
    """Infer a Dashboard config model from a KbnDashboard view model.

    Args:
        kbn: Validated KbnDashboard view model.
        raw_reference_lookup: Optional pre-built reference lookup extracted from the raw
            dict before validation (handles partial/non-standard references).
        raw_filters: Optional raw filter dicts extracted from the raw dict. Used instead
            of KbnFilter objects because KbnFilter drops the top-level 'range' key.

    Returns:
        Tuple of (dashboard_model, raw_panels) where dashboard_model is an
        actual ``kb_dashboard_core.dashboard.config.Dashboard`` instance and
        raw_panels are the original panel dicts for TODO comment generation.
    """
    attrs = kbn.attributes
    title = attrs.title if attrs is not None and attrs.title is not None else 'Untitled Dashboard'

    dashboard: dict[str, Any] = {
        'name': title,
    }
    if kbn.id is not None:
        dashboard['id'] = kbn.id
    description = attrs.description if attrs is not None else None
    if description is not None:
        dashboard['description'] = description

    settings = _infer_settings(kbn)
    if settings is not None:
        dashboard['settings'] = settings

    time_range = _infer_time_range(kbn)
    if time_range is not None:
        dashboard['time_range'] = time_range

    query = _infer_query(kbn)
    if query is not None:
        dashboard['query'] = query

    # Filters — prefer raw_filters (which preserve all top-level keys like 'range')
    # over the KbnFilter objects that drop unknown fields
    filters_list: list[dict[str, Any]] = []
    filter_source: list[dict[str, Any]] = []
    if raw_filters is not None:
        filter_source = raw_filters
    elif attrs is not None and attrs.kibanaSavedObjectMeta is not None:
        meta_obj = attrs.kibanaSavedObjectMeta
        search_source = meta_obj.searchSourceJSON
        if search_source is not None and search_source.filter is not None:
            for kbn_filter in search_source.filter:
                fd = kbn_filter.model_dump(exclude_none=True, by_alias=True)
                filter_source.append(fd)
    for raw_f in filter_source:
        try:
            result = _infer_filter_from_raw(raw_f)
            if result is not None:
                filters_list.append(result)
        except ValidationError as exc:
            meta_f = get_dict(raw_f, 'meta') or {}
            key = get_str(meta_f, 'key') or '?'
            logger.warning('_infer_filter produced invalid filter dict (key=%s): %s', key, exc)
    if filters_list:
        dashboard['filters'] = filters_list

    # Controls
    reference_lookup = _build_reference_lookup(kbn, raw_reference_lookup)
    controls_list: list[dict[str, Any]] = []
    for panel_id, panel_dict in _iter_controls(kbn):
        try:
            controls_list.append(_infer_control_from_dict(panel_id, panel_dict, reference_lookup))
        except ValidationError as exc:
            control_type = get_str(panel_dict, 'type')
            logger.warning('_infer_control produced invalid control dict (type=%s): %s', control_type, exc)
    if controls_list:
        dashboard['controls'] = controls_list

    # Panels
    raw_panels: list[dict[str, Any]] = []
    panels: list[dict[str, Any]] = []
    panels_json = attrs.panelsJSON if attrs is not None else None
    if panels_json is not None:
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is None:
                continue
            raw_panels.append(panel)
            panel_type_key, chart_config, panel_wrapper = _infer_panel(panel, reference_lookup)
            panel_wrapper[panel_type_key] = chart_config
            panels.append(panel_wrapper)

    dashboard['panels'] = panels
    return Dashboard.model_validate(dashboard), raw_panels
