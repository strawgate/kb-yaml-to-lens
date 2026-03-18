"""Phase 2: Infer Dashboard config objects from KbnDashboard view model.

Maps parsed Kibana/Kbn view data to actual kb-dashboard-core config models,
producing dicts that can be validated into ``Dashboard`` instances.

Chart-specific logic is delegated to sub-modules:
- ``infer_lens``: Lens / ES|QL chart inference
- ``infer_simple``: Simple panel builders (markdown, search, image, links, vega)
"""

# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import logging
from typing import Any

from kb_dashboard_core.controls.config import ControlTypes
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.filters.config import FilterTypes
from pydantic import TypeAdapter, ValidationError

from .infer_lens import _infer_lens_chart  # pyright: ignore[reportPrivateUsage]
from .infer_simple import _SIMPLE_PANEL_BUILDERS, SimplePanel  # pyright: ignore[reportPrivateUsage]
from .kbn_raw_models.dashboard.view import KbnDashboard
from .parse_shared import (
    as_dict,
    get_bool,
    get_list,
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
# Dashboard-level inference
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
    """Infer dashboard time range from timeFrom/timeTo."""
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
    """Extract the dashboard-level KQL/Lucene query."""
    attrs = kbn.attributes
    meta = attrs.kibanaSavedObjectMeta if attrs is not None else None
    ssj = meta.searchSourceJSON if meta is not None else None
    query_obj = ssj.query if ssj is not None else None
    if query_obj is None:
        return None
    query = query_obj.query
    if query is None:
        return None
    if query_obj.language == 'lucene':
        return {'lucene': query}
    return {'kql': query}


def _infer_filter(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Infer a single filter config dict from a raw filter dict. Returns None for unrecognized types."""
    f: dict[str, Any] = {}
    filter_meta = as_dict(raw.get('meta'))
    if filter_meta is None:
        return None
    key = get_str(filter_meta, 'key')
    if key is None:
        return None
    filter_type = get_str(filter_meta, 'type')

    if filter_type == 'exists':
        f['exists'] = key
    elif filter_type == 'phrase':
        f['field'] = key
        params = as_dict(filter_meta.get('params'))
        if params is not None:
            query = get_scalar(params, 'query')
            if query is not None:
                f['equals'] = query
        else:
            value = get_scalar(filter_meta, 'value')
            if value is not None:
                f['equals'] = value
    elif filter_type == 'phrases':
        f['field'] = key
        params_list = get_list(filter_meta, 'params')
        if params_list is not None:
            f['in'] = [p for p in params_list if isinstance(p, (str, int, float, bool))]
    elif filter_type == 'range':
        f['field'] = key
        range_params = as_dict(raw.get('range'))
        if range_params is not None:
            field_range = as_dict(range_params.get(key))
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = get_scalar(field_range, bound)
                    if val is not None:
                        f[bound] = val
    else:
        # Unrecognized filter type — skip
        return None

    # Apply metadata
    disabled = get_bool(filter_meta, 'disabled')
    if disabled is not None and disabled:
        f['disabled'] = True
    alias = get_str(filter_meta, 'alias')
    if alias is not None and len(alias) > 0:
        f['alias'] = alias

    _ = _filter_adapter.validate_python(f)
    return f


def _infer_filters(raw_dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract dashboard-level filters from the raw dashboard dict.

    Works with raw filter dicts to preserve fields (like 'range') that
    are not modeled in KbnFilter.
    """
    from .parse_shared import parse_json_field

    raw_attrs = as_dict(raw_dashboard.get('attributes'))
    if raw_attrs is None:
        return []
    raw_meta = as_dict(raw_attrs.get('kibanaSavedObjectMeta'))
    if raw_meta is None:
        return []
    search_source_raw = parse_json_field(raw_meta.get('searchSourceJSON'))
    if not isinstance(search_source_raw, dict):
        return []
    raw_filters = search_source_raw.get('filter')
    if not isinstance(raw_filters, list):
        return []

    result: list[dict[str, Any]] = []
    for filter_item in raw_filters:
        raw = as_dict(filter_item)
        if raw is None:
            continue
        try:
            result_filter = _infer_filter(raw)
            if result_filter is not None:
                result.append(result_filter)
        except ValidationError as exc:
            filter_meta = as_dict(raw.get('meta')) or {}
            key = get_str(filter_meta, 'key') or 'unknown'
            logger.warning('_infer_filter produced invalid filter dict (key=%s): %s', key, exc)
    return result


def _infer_control(panel_id: str, raw: dict[str, Any], reference_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer a single control config dict from a raw control panel dict."""
    ctrl: dict[str, Any] = {}
    control_type = get_str(raw, 'type')
    if control_type is not None:
        ctrl['type'] = CONTROL_TYPE_MAP.get(control_type, f'TODO_control_type_{control_type}')
    else:
        ctrl['type'] = 'TODO_control_type_unknown'

    explicit_input = as_dict(raw.get('explicitInput'))
    field_name: str | None = None
    title: str | None = None
    data_view_id: str | None = None

    if explicit_input is not None:
        field_name = get_str(explicit_input, 'fieldName')
        title = get_str(explicit_input, 'title')
        data_view_id = get_str(explicit_input, 'dataViewId')
        if data_view_id is None:
            ref_suffix = {
                'optionsListControl': 'optionsListDataView',
                'rangeSliderControl': 'rangeSliderDataView',
                'timeSliderControl': 'timeSliderDataView',
                'timeSlider': 'timeSliderDataView',
                'esqlControl': 'esqlControlDataView',
            }.get(control_type or '')
            if ref_suffix is not None:
                ref_name = f'controlGroup_{panel_id}:{ref_suffix}'
                data_view_id = reference_lookup.get(ref_name)

    if field_name is not None:
        ctrl['field'] = field_name
    if title is not None:
        ctrl['label'] = title

    # data_view is required for options and range controls
    resolved_type = ctrl.get('type')
    if resolved_type in {'options', 'range'}:
        ctrl['data_view'] = data_view_id if data_view_id is not None else 'TODO_data_view'
    elif data_view_id is not None:
        ctrl['data_view'] = data_view_id

    _ = _control_adapter.validate_python(ctrl)
    return ctrl


def _infer_controls(kbn: KbnDashboard, reference_lookup: dict[str, str]) -> list[dict[str, Any]]:
    """Extract dashboard controls from KbnDashboard."""
    attrs = kbn.attributes
    if attrs is None:
        return []
    cgi = attrs.controlGroupInput
    if cgi is None:
        return []
    panels_json = cgi.panelsJSON
    if panels_json is None:
        return []

    # panels_json is KbnControlPanelsJson (RootDict[KbnControlTypes])
    raw_panels = panels_json.root  # dict[str, KbnControlTypes]

    def _order(item: tuple[str, Any]) -> int:
        panel = item[1]
        order = getattr(panel, 'order', None)
        return order if isinstance(order, int) else 0

    result: list[dict[str, Any]] = []
    for panel_id, panel in sorted(raw_panels.items(), key=_order):
        # Dump to raw dict for processing
        panel_raw = panel.model_dump(by_alias=True, exclude_none=True)
        try:
            result.append(_infer_control(panel_id, panel_raw, reference_lookup))
        except ValidationError as exc:
            logger.warning('_infer_control produced invalid control dict (type=%s): %s', getattr(panel, 'type', None), exc)
    return result


def _build_reference_lookup(raw_dashboard: dict[str, Any]) -> dict[str, str]:
    """Build name -> id reference lookup from the raw dashboard references list.

    Uses the raw dict rather than KbnDashboard.references to handle
    non-dict items and references with missing fields gracefully.
    """
    refs = raw_dashboard.get('references')
    if not isinstance(refs, list):
        return {}
    lookup: dict[str, str] = {}
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        name = ref.get('name')
        ref_id = ref.get('id')
        if name is not None and ref_id is not None:
            lookup[str(name)] = str(ref_id)
    return lookup


def _infer_panel(panel_dict: dict[str, Any], ref_lookup: dict[str, str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Infer panel config from a raw panel dict.

    Returns (panel_type_key, chart_config_dict, panel_wrapper_dict).
    """
    wrapper: dict[str, Any] = {}

    # Panel index
    panel_index = get_str(panel_dict, 'panelIndex')
    if panel_index is not None:
        wrapper['id'] = panel_index

    # Title
    title = get_str(panel_dict, 'title') or ''
    embeddable_cfg = as_dict(panel_dict.get('embeddableConfig')) or {}
    if not title:
        title = get_str(embeddable_cfg, 'title') or ''
    wrapper['title'] = title

    # Hide title / description
    hide_panel_titles = get_bool(embeddable_cfg, 'hidePanelTitles')
    if hide_panel_titles is True:
        wrapper['hide_title'] = True

    panel_description = get_str(embeddable_cfg, 'description')
    if panel_description is None:
        panel_description = get_str(panel_dict, 'description')
    if panel_description is not None and len(panel_description) > 0:
        wrapper['description'] = panel_description

    # Grid data
    grid_data = as_dict(panel_dict.get('gridData'))
    if grid_data is not None:
        w = grid_data.get('w')
        h = grid_data.get('h')
        x = grid_data.get('x')
        y = grid_data.get('y')
        if isinstance(w, int) or isinstance(h, int):
            size: dict[str, int] = {}
            if isinstance(w, int):
                size['w'] = w
            if isinstance(h, int):
                size['h'] = h
            wrapper['size'] = size
        if isinstance(x, int) or isinstance(y, int):
            pos: dict[str, int] = {}
            if isinstance(x, int):
                pos['x'] = x
            if isinstance(y, int):
                pos['y'] = y
            wrapper['position'] = pos

    panel_type = get_str(panel_dict, 'type')
    if panel_type is None:
        return 'markdown', {'content': 'TODO(decompile): missing panel type'}, wrapper

    # Check for unresolved panel reference
    panel_ref_name = get_str(panel_dict, 'panelRefName')
    if panel_ref_name is not None and as_dict(embeddable_cfg.get('attributes')) is None:
        return 'markdown', {'content': f'TODO(decompile): unresolved panel reference: {panel_ref_name}'}, wrapper

    # Lens / ESQL panels
    if panel_type in {'lens', 'esql'}:
        try:
            inferred_type, chart = _infer_lens_chart(panel_dict)
        except (ValueError, ValidationError) as exc:
            logger.warning('_infer_lens_chart validation failed for panel %s: %s', panel_index, exc)
            return 'markdown', {'content': f'TODO(decompile): panel validation failed: {exc}'}, wrapper
        return inferred_type, chart, wrapper

    # Simple panels
    from .parse_shared import SIMPLE_PANEL_VIEW_MODEL_MAP, validate_view_model

    # Resolve saved vis type for 'visualization' panels
    saved_vis_type: str | None = None
    saved_vis = as_dict(embeddable_cfg.get('savedVis'))
    if saved_vis is not None:
        saved_vis_type = get_str(saved_vis, 'type')

    resolved_panel_type = saved_vis_type if panel_type == 'visualization' and saved_vis_type else panel_type

    # Build view model
    model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(panel_type)
    if model_cls is None and panel_type == 'visualization' and saved_vis_type is not None:
        model_cls = SIMPLE_PANEL_VIEW_MODEL_MAP.get(saved_vis_type)
    view_panel = validate_view_model(model_cls, panel_dict) if model_cls is not None else None

    embeddable_attrs = as_dict(embeddable_cfg.get('attributes')) or {}
    simple = SimplePanel(
        panel_type=resolved_panel_type,
        raw=panel_dict,
        embeddable_config=embeddable_cfg,
        embeddable_attributes=embeddable_attrs,
        view_panel=view_panel,
    )

    builder = _SIMPLE_PANEL_BUILDERS.get(resolved_panel_type)
    if builder is not None:
        config = builder(simple, ref_lookup)
        return resolved_panel_type, config, wrapper

    # Unsupported type
    return 'markdown', {'content': f'TODO(decompile): unsupported panel type `{panel_type}`'}, wrapper


def infer_dashboard(kbn: KbnDashboard, raw_dashboard: dict[str, Any] | None = None) -> tuple[Dashboard, list[dict[str, Any]]]:
    """Infer a Dashboard config model from a KbnDashboard view model.

    Args:
        kbn: The validated KbnDashboard model.
        raw_dashboard: The original raw dashboard dict (used for raw filter/reference extraction).

    Returns:
        Tuple of (dashboard_model, panel_originals) where dashboard_model is an
        actual ``kb_dashboard_core.dashboard.config.Dashboard`` instance.
    """
    if raw_dashboard is None:
        raw_dashboard = {}
    attrs = kbn.attributes

    dashboard: dict[str, Any] = {
        'name': (attrs.title if attrs is not None and attrs.title is not None else '') or 'Untitled Dashboard',
    }
    if kbn.id is not None:
        dashboard['id'] = kbn.id
    if attrs is not None and attrs.description is not None:
        dashboard['description'] = attrs.description

    settings = _infer_settings(kbn)
    if settings is not None:
        dashboard['settings'] = settings

    time_range = _infer_time_range(kbn)
    if time_range is not None:
        dashboard['time_range'] = time_range

    query = _infer_query(kbn)
    if query is not None:
        dashboard['query'] = query

    # Use raw dict for references to handle non-dict items and missing fields
    reference_lookup = _build_reference_lookup(raw_dashboard)

    # Use raw dict for filters to preserve fields (like 'range') not in KbnFilter
    filters = _infer_filters(raw_dashboard)
    if filters:
        dashboard['filters'] = filters

    controls = _infer_controls(kbn, reference_lookup)
    if controls:
        dashboard['controls'] = controls

    # Panels
    panels: list[dict[str, Any]] = []
    panels_json = attrs.panelsJSON if attrs is not None else None
    if isinstance(panels_json, list):
        for panel_item in panels_json:
            panel_dict = as_dict(panel_item)
            if panel_dict is None:
                continue
            panel_type, chart_config, panel_wrapper = _infer_panel(panel_dict, reference_lookup)
            panel_wrapper[panel_type] = chart_config
            panels.append(panel_wrapper)

    dashboard['panels'] = panels
    return Dashboard.model_validate(dashboard), []
