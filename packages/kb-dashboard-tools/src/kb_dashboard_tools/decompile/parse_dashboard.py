"""Dashboard-level parsing orchestration for decompiler parse phase."""

from typing import Any, cast

from kb_dashboard_core.controls.view import (
    KbnESQLControl,
    KbnOptionsListControl,
    KbnRangeSliderControl,
    KbnTimeSliderControl,
)
from kb_dashboard_core.dashboard.view import KbnDashboardOptions
from kb_dashboard_core.filters.view import KbnFilter

from .parse_models import (
    ParsedControl,
    ParsedDashboard,
    ParsedDashboardSettings,
    ParsedFilter,
)
from .parse_panels import parse_panel
from .parse_shared import (
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_str,
    parse_json_field,
    validate_view_model,
)
from .raw_models import RawDashboard, RawDashboardAttributes, RawReference


def _normalize_filter_for_view(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw Kibana filter JSON into the field names used by KbnFilter."""
    normalized = dict(raw)
    state = cast('object', normalized.pop('$state', None))
    if 'state' not in normalized and isinstance(state, dict):
        normalized['state'] = state
    return normalized


def _normalize_control_for_view(panel_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Fill Kibana defaulted control fields so Kbn* view validation can succeed."""
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


def _iter_raw_references(references: list[RawReference | object] | None) -> dict[str, str]:
    lookup: dict[str, str] = {}
    if references is None:
        return lookup
    for ref in references:
        if isinstance(ref, RawReference) and ref.name is not None and ref.id is not None:
            lookup[ref.name] = ref.id
    return lookup


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


def _parse_dashboard_query(attributes: dict[str, Any]) -> dict[str, str] | None:
    query_dict: dict[str, str] | None = None
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
                        query_dict = {'kql': query}
                    elif language == 'lucene':
                        query_dict = {'lucene': query}
    return query_dict


def _parse_controls(attributes: dict[str, Any], reference_lookup: dict[str, str]) -> list[ParsedControl]:
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


def parse_dashboard(dashboard: dict[str, Any]) -> ParsedDashboard:
    """Parse a raw Kibana dashboard JSON dict into a typed intermediate structure."""
    raw_dashboard = RawDashboard.model_validate(dashboard)
    raw_attributes = raw_dashboard.attributes or RawDashboardAttributes()
    attributes = raw_attributes.model_dump(exclude_none=True, by_alias=True)
    reference_lookup = _iter_raw_references(raw_dashboard.references)

    parsed = ParsedDashboard(
        dashboard_id=raw_dashboard.id,
        title=raw_attributes.title if raw_attributes.title is not None else 'Untitled Dashboard',
        description=raw_attributes.description,
        time_from=raw_attributes.time_from,
        time_to=raw_attributes.time_to,
        settings=_parse_settings(attributes),
        query=_parse_dashboard_query(attributes),
        filters=_parse_filters(attributes),
        controls=_parse_controls(attributes, reference_lookup),
        reference_lookup=reference_lookup,
    )

    panels_json = parse_json_field(raw_attributes.panels_json)
    if isinstance(panels_json, list):
        for panel_item in panels_json:  # pyright: ignore[reportAny]
            panel = as_dict(panel_item)  # pyright: ignore[reportAny]
            if panel is not None:
                parsed.panels.append(parse_panel(panel))

    return parsed
