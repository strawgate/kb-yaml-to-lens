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
from .infer_simple import _SIMPLE_PANEL_BUILDERS  # pyright: ignore[reportPrivateUsage]
from .kbn_raw_models.dashboard.view import KbnDashboard
from .kbn_raw_models.filters.view import KbnFilter, KbnFilterMeta
from .kbn_raw_models.panels.view import KbnBasePanel
from .parse_shared import (
    as_dict,
    get_bool,
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
    return settings or None


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


def _infer_filter(f: KbnFilter) -> dict[str, Any] | None:
    """Infer a single filter config dict from a typed KbnFilter. Returns None for unrecognized types."""
    if not isinstance(f.meta, KbnFilterMeta):
        return None
    meta = f.meta
    key = meta.key
    if key is None:
        return None
    filter_type = meta.type
    result: dict[str, Any] = {}

    if filter_type == 'exists':
        result['exists'] = key
    elif filter_type == 'phrase':
        result['field'] = key
        params = meta.params if isinstance(meta.params, dict) else None
        if params is not None:
            query = get_scalar(params, 'query')
            if query is not None:
                result['equals'] = query
        else:
            value = get_scalar(meta.model_dump(), 'value')
            if value is not None:
                result['equals'] = value
    elif filter_type == 'phrases':
        result['field'] = key
        params_list = meta.params if isinstance(meta.params, list) else None
        if params_list is not None:
            result['in'] = list(params_list)
    elif filter_type == 'range':
        result['field'] = key
        params = meta.params if isinstance(meta.params, dict) else None
        if params is not None:
            for bound in ('gte', 'gt', 'lte', 'lt'):
                val = get_scalar(params, bound)
                if val is not None:
                    result[bound] = val
        elif f.range is not None:
            field_range = as_dict(f.range.get(key))
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = get_scalar(field_range, bound)
                    if val is not None:
                        result[bound] = val
    else:
        return None

    if meta.disabled is True:
        result['disabled'] = True
    if meta.alias is not None and len(meta.alias) > 0:
        result['alias'] = meta.alias

    _ = _filter_adapter.validate_python(result)
    return result


def _infer_filters(kbn: KbnDashboard) -> list[dict[str, Any]]:
    """Extract dashboard-level filters from the KbnDashboard model."""
    attrs = kbn.attributes
    ssj = attrs.kibanaSavedObjectMeta.searchSourceJSON if attrs and attrs.kibanaSavedObjectMeta else None
    filters = ssj.filter if ssj else None
    if not filters:
        return []
    result: list[dict[str, Any]] = []
    for f in filters:
        try:
            inferred = _infer_filter(f)
            if inferred is not None:
                result.append(inferred)
        except ValidationError as exc:
            key = f.meta.key if isinstance(f.meta, KbnFilterMeta) else 'unknown'
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


def _build_reference_lookup(kbn: KbnDashboard) -> dict[str, str]:
    """Build name -> id reference lookup from KbnDashboard.references."""
    return {ref.name: ref.id for ref in kbn.references if ref.name and ref.id}


def _infer_panel(panel: KbnBasePanel, ref_lookup: dict[str, str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Infer panel config from a typed KbnBasePanel (or concrete subtype).

    Returns (panel_type_key, chart_config_dict, panel_wrapper_dict).
    """
    wrapper: dict[str, Any] = {}

    # Panel index
    if panel.panelIndex is not None:
        wrapper['id'] = panel.panelIndex

    # Grid data
    gd = panel.gridData
    if gd is not None:
        if gd.w is not None or gd.h is not None:
            wrapper['size'] = {k: v for k, v in {'w': gd.w, 'h': gd.h}.items() if v is not None}
        if gd.x is not None or gd.y is not None:
            wrapper['position'] = {k: v for k, v in {'x': gd.x, 'y': gd.y}.items() if v is not None}

    # embeddableConfig is always a raw dict (or None) since KbnBasePanel.embeddableConfig: Any | None.
    embeddable_cfg_dict: dict[str, Any] = as_dict(panel.embeddableConfig) or {}

    # Title: panel-level first, then embeddableConfig
    title = panel.title or get_str(embeddable_cfg_dict, 'title') or ''
    wrapper['title'] = title

    # Hide title
    if get_bool(embeddable_cfg_dict, 'hidePanelTitles') is True:
        wrapper['hide_title'] = True

    # Description: embeddableConfig first, then panel-level
    description = get_str(embeddable_cfg_dict, 'description') or panel.description
    if description:
        wrapper['description'] = description

    panel_type = panel.type
    if panel_type is None:
        return 'markdown', {'content': 'TODO(decompile): missing panel type'}, wrapper

    # Check for unresolved panel reference (only for panel types where panelRefName
    # means an externally stored embeddable config, not for search where it IS the reference).
    panel_ref_name = panel.panelRefName
    has_embedded_attrs = as_dict(embeddable_cfg_dict.get('attributes')) is not None
    if panel_ref_name is not None and not has_embedded_attrs and panel_type != 'search':
        return 'markdown', {'content': f'TODO(decompile): unresolved panel reference: {panel_ref_name}'}, wrapper

    # Lens / ESQL panels (dispatch on type, not isinstance — a panel may have fallen
    # to KbnBasePanel catch-all if deeply nested validation failed, but the dict path works either way)
    if panel_type in {'lens', 'esql'}:
        panel_dict = panel.model_dump(by_alias=True, exclude_none=False)
        try:
            inferred_type, chart = _infer_lens_chart(panel_dict)
        except (ValueError, ValidationError) as exc:
            logger.warning('_infer_lens_chart validation failed for panel %s: %s', panel.panelIndex, exc)
            return 'markdown', {'content': f'TODO(decompile): panel validation failed: {exc}'}, wrapper
        return inferred_type, chart, wrapper

    # Simple panels — legacy 'visualization' type maps to 'markdown' in config
    config_type = 'markdown' if panel_type == 'visualization' else panel_type
    builder = _SIMPLE_PANEL_BUILDERS.get(config_type)
    if builder is not None:
        config = builder(panel, embeddable_cfg_dict, ref_lookup)
        return config_type, config, wrapper

    return 'markdown', {'content': f'TODO(decompile): unsupported panel type `{panel_type}`'}, wrapper


def infer_dashboard(kbn: KbnDashboard) -> Dashboard:
    """Infer a Dashboard config model from a KbnDashboard view model.

    Args:
        kbn: The validated KbnDashboard model.

    Returns:
        A ``kb_dashboard_core.dashboard.config.Dashboard`` instance.
    """
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

    reference_lookup = _build_reference_lookup(kbn)
    filters = _infer_filters(kbn)
    if filters:
        dashboard['filters'] = filters

    controls = _infer_controls(kbn, reference_lookup)
    if controls:
        dashboard['controls'] = controls

    # Panels
    panels: list[dict[str, Any]] = []
    panels_json = attrs.panelsJSON if attrs is not None else None
    if panels_json is not None:
        for panel_item in panels_json:
            panel_type, chart_config, panel_wrapper = _infer_panel(panel_item, reference_lookup)
            panel_wrapper[panel_type] = chart_config
            panels.append(panel_wrapper)

    dashboard['panels'] = panels
    return Dashboard.model_validate(dashboard)
