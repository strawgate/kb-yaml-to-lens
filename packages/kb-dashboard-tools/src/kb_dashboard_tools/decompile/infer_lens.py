"""Lens and ES|QL chart inference.

Builds chart config dicts from Kibana Lens and ES|QL visualization panels —
resolving chart types, extracting metrics/dimensions/breakdowns, legend
settings, axis configuration, and appearance options.
"""

# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import logging
import re
from typing import Any

from kb_dashboard_core.panels.charts.config import ESQLPanelConfig, LensPanelConfig
from pydantic import TypeAdapter, ValidationError

from .parse_shared import (
    as_dict,
    get_bool,
    get_dict,
    get_int,
    get_list,
    get_nested,
    get_number,
    get_str,
)
from .tables import (
    KIBANA_AXIS_EXTENT_MODE_TO_YAML,
    KIBANA_CURVE_TYPE_TO_YAML,
    KIBANA_DEFAULT_FILL_OPACITY,
    KIBANA_END_VALUE_TO_YAML,
    KIBANA_FITTING_FUNCTION_TO_YAML,
    KIBANA_GAUGE_DEFAULT_SHAPE,
    KIBANA_GAUGE_SHAPE_TO_YAML,
    KIBANA_LEGEND_SIZE_TO_YAML,
    KIBANA_PARTITION_NUMBER_DISPLAY_TO_YAML,
    KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML,
    KIBANA_PIE_NUMBER_DISPLAY_TO_YAML,
    LENS_VISUALIZATION_TYPES,
    OPERATION_TYPE_MAP,
    PARTITION_CHART_TYPES,
    PIE_SHAPES,
    SKIP_OPERATION_TYPES,
    XY_SERIES_TYPES,
    XY_STACKING_MODES,
)

__all__ = ['_infer_lens_chart']

logger = logging.getLogger(__name__)

_lens_panel_adapter: TypeAdapter[LensPanelConfig] = TypeAdapter(LensPanelConfig)
_esql_panel_adapter: TypeAdapter[ESQLPanelConfig] = TypeAdapter(ESQLPanelConfig)

# Chart-type classification sets (reused across functions)
_XY_CHART_TYPES = frozenset({'line', 'bar', 'area'})
_SINGULAR_METRIC_TYPES = frozenset({'gauge', 'tagcloud', 'waffle', 'mosaic', 'treemap'})
_SINGULAR_DIM_TYPES = frozenset({'metric', 'tagcloud', 'waffle', 'mosaic'})
_PARTITION_TYPES = frozenset({'pie', 'treemap'})
_PLURAL_METRIC_TYPES = frozenset({'pie', 'datatable', 'line', 'bar', 'area'})

# Sentinel field name Kibana uses for record-count metrics
_RECORDS_FIELD = 'Records'


def _merge_appearance(chart: dict[str, Any], new_appearance: dict[str, Any] | None) -> None:
    """Merge appearance settings into chart, updating existing if present."""
    if new_appearance is None:
        return
    existing = as_dict(chart.get('appearance'))
    if existing is not None:
        existing.update(new_appearance)
    else:
        chart['appearance'] = new_appearance


# ---------------------------------------------------------------------------
# Visualization state helpers (still operate on raw dicts from visualization: Any)
# ---------------------------------------------------------------------------


def _resolve_vis_type(vis_raw: dict[str, Any], raw_vis_type: str | None) -> str | None:
    """Map Kibana visualization type + series preferences to a YAML chart type."""
    if raw_vis_type is None:
        return None
    normalized = LENS_VISUALIZATION_TYPES.get(raw_vis_type.lower())
    if raw_vis_type.lower() in {'lnsxy', 'xy'}:
        pst = get_str(vis_raw, 'preferredSeriesType')
        if pst is not None:
            return XY_SERIES_TYPES.get(pst, 'line')
        return 'line'
    if raw_vis_type.lower() in {'lnspie', 'pie'}:
        shape = get_str(vis_raw, 'shape')
        if shape is not None:
            resolved = PIE_SHAPES.get(shape)
            if resolved is not None and resolved != 'pie':
                return resolved
    return normalized


def _resolve_stacking_mode(vis_raw: dict[str, Any], chart_type: str | None) -> str | None:
    """Determine stacking mode (stacked/percentage) for bar and area charts."""
    if chart_type not in {'bar', 'area'}:
        return None
    pst = get_str(vis_raw, 'preferredSeriesType')
    if pst is None:
        return None
    return XY_STACKING_MODES.get(pst)


# ---------------------------------------------------------------------------
# Layer roles — extracted from raw visualization dict
# ---------------------------------------------------------------------------


def _parse_layer_roles_from_vis(vis_raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract layer roles from the raw visualization dict.

    Returns a mapping of layer_id -> {metric_ids, dimension_id, breakdown_id, accessors}.
    """
    roles: dict[str, dict[str, Any]] = {}

    def _dedupe(ids: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for i in ids:
            if i not in seen:
                result.append(i)
                seen.add(i)
        return result

    # Multi-layer: vis has a "layers" list
    vis_layers = get_list(vis_raw, 'layers')
    if vis_layers is not None:
        for raw_layer in vis_layers:
            layer = as_dict(raw_layer)
            if layer is None:
                continue
            layer_id = get_str(layer, 'layerId')
            if layer_id is None:
                continue
            metric_ids: list[str] = []
            raw_accessors = get_list(layer, 'accessors')
            if raw_accessors is not None:
                metric_ids = [a for a in raw_accessors if isinstance(a, str)]
            x_accessor = get_str(layer, 'xAccessor')
            split_accessor = get_str(layer, 'splitAccessor')
            accessors_combined: list[str] = []
            if x_accessor is not None:
                accessors_combined.append(x_accessor)
            if split_accessor is not None:
                accessors_combined.append(split_accessor)
            accessors_combined.extend(metric_ids)
            roles[layer_id] = {
                'metric_ids': metric_ids,
                'dimension_id': x_accessor,
                'breakdown_id': split_accessor,
                'accessors': _dedupe(accessors_combined),
            }

    # Single-layer: vis has a "layerId" directly
    single_layer_id = get_str(vis_raw, 'layerId')
    if single_layer_id is not None:
        role = roles.setdefault(single_layer_id, {'metric_ids': [], 'dimension_id': None, 'breakdown_id': None, 'accessors': []})
        # Metric accessors
        for key in ('metricAccessor', 'secondaryAccessor', 'accessor'):
            val = get_str(vis_raw, key)
            if val is not None and val not in role['metric_ids']:
                role['metric_ids'].append(val)
        raw_accessors2 = get_list(vis_raw, 'accessors')
        if raw_accessors2 is not None:
            for v in raw_accessors2:
                if isinstance(v, str) and v not in role['metric_ids']:
                    role['metric_ids'].append(v)
        # Dimension / breakdown
        x_acc = get_str(vis_raw, 'xAccessor')
        if x_acc is not None:
            role['dimension_id'] = x_acc
        split_acc = get_str(vis_raw, 'splitAccessor')
        if split_acc is not None:
            role['breakdown_id'] = split_acc
        # Build accessors list if empty
        if not role['accessors']:
            ids: list[str] = []
            for key in ('xAccessor', 'metricAccessor', 'splitAccessor', 'secondaryAccessor', 'accessor'):
                val = get_str(vis_raw, key)
                if val is not None:
                    ids.append(val)
            raw_accessors3 = get_list(vis_raw, 'accessors')
            if raw_accessors3 is not None:
                ids.extend([a for a in raw_accessors3 if isinstance(a, str)])
            role['accessors'] = _dedupe(ids)

    return roles


# ---------------------------------------------------------------------------
# Metric / dimension / breakdown extraction (form-based)
# ---------------------------------------------------------------------------


def _extract_metric_filter(col_raw: dict[str, Any]) -> dict[str, str] | None:
    """Extract the metric-level KQL/Lucene filter from a raw column dict, if present."""
    col_filter = get_dict(col_raw, 'filter')
    if col_filter is None:
        return None
    query = get_str(col_filter, 'query')
    if not query:
        return None
    language = get_str(col_filter, 'language')
    if language == 'lucene':
        return {'lucene': query}
    return {'kql': query}


def _extract_metric_format(col_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract number/byte/percent format configuration from a raw column dict."""
    params = get_dict(col_raw, 'params')
    if params is None:
        return None
    format_config = get_dict(params, 'format')
    if format_config is None:
        return None
    format_type = get_str(format_config, 'id')
    if format_type is None or format_type not in {'number', 'bytes', 'bits', 'percent', 'duration', 'custom'}:
        return None
    fmt: dict[str, Any] = {'type': format_type}
    fmt_params = get_dict(format_config, 'params')
    if fmt_params is None:
        if format_type == 'custom':
            return None
        return fmt
    decimals = get_int(fmt_params, 'decimals')
    if decimals is not None:
        fmt['decimals'] = decimals
    suffix = get_str(fmt_params, 'suffix')
    if suffix is not None:
        fmt['suffix'] = suffix
    compact = get_bool(fmt_params, 'compact')
    if compact is not None:
        fmt['compact'] = compact
    pattern = get_str(fmt_params, 'pattern')
    if pattern is not None:
        fmt['pattern'] = pattern
    # custom format requires a pattern; fall back to number if none is present
    if format_type == 'custom' and 'pattern' not in fmt:
        fmt['type'] = 'number'
    return fmt


def _build_metric_dict(col_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Build a metric config dict from a raw column dict. Returns None if skipped."""
    operation_type = get_str(col_raw, 'operationType')
    if operation_type is None:
        return None
    if operation_type in SKIP_OPERATION_TYPES:
        return None

    # Formula metrics bypass the normal aggregation mapping
    if operation_type == 'formula':
        params = get_dict(col_raw, 'params')
        formula_str = get_str(params, 'formula') if params is not None else None
        if formula_str is None:
            return None
        label = get_str(col_raw, 'label')
        metric: dict[str, Any] = {'formula': formula_str}
        if label is not None and len(label) > 0:
            metric['label'] = label
        fmt = _extract_metric_format(col_raw)
        if fmt is not None:
            metric['format'] = fmt
        return metric

    aggregation = OPERATION_TYPE_MAP.get(operation_type)
    if aggregation is None:
        return None

    label = get_str(col_raw, 'label')
    source_field = get_str(col_raw, 'sourceField')

    metric = {'aggregation': aggregation}
    if source_field is not None and source_field != _RECORDS_FIELD:
        metric['field'] = source_field
    if label is not None and len(label) > 0:
        metric['label'] = label

    params = get_dict(col_raw, 'params')
    if operation_type == 'percentile':
        percentile_val = get_number(params, 'percentile') if params is not None else None
        if percentile_val is not None:
            metric['percentile'] = int(percentile_val)
    elif operation_type == 'percentile_rank':
        rank_val = get_number(params, 'value') if params is not None else None
        if rank_val is not None:
            metric['rank'] = rank_val

    filt = _extract_metric_filter(col_raw)
    if filt is not None:
        metric['filter'] = filt
    fmt = _extract_metric_format(col_raw)
    if fmt is not None:
        metric['format'] = fmt
    return metric


def _build_dimension_dict(
    col_raw: dict[str, Any],
    col_id: str = '',
    layer_role: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]] | None:
    """Build a dimension or breakdown dict from a raw column dict. Returns (category, dict) or None."""
    operation_type = get_str(col_raw, 'operationType')
    source_field = get_str(col_raw, 'sourceField')

    if operation_type == 'date_histogram':
        dim: dict[str, Any] = {'type': 'date_histogram'}
        if source_field is not None:
            dim['field'] = source_field
        params = get_dict(col_raw, 'params')
        interval = get_str(params, 'interval') if params is not None else None
        if interval is not None and interval not in {'auto', ''}:
            # Kibana stores bare units like 'm'; compiler expects '1m'
            if re.match(r'^(ms|s|m|h|d|w|M|q|y)$', interval):
                interval = f'1{interval}'
            dim['minimum_interval'] = interval
        return 'dimension', dim

    if operation_type == 'terms':
        bd: dict[str, Any] = {'type': 'values'}
        if source_field is not None:
            bd['field'] = source_field
        params = get_dict(col_raw, 'params')
        size = get_int(params, 'size') if params is not None else None
        if size is not None:
            bd['size'] = size
        category = 'dimension' if layer_role is not None and col_id == layer_role.get('dimension_id') else 'breakdown'
        return category, bd

    if operation_type == 'filters':
        filters_list: list[dict[str, Any]] = []
        params = get_dict(col_raw, 'params')
        raw_filters = get_list(params, 'filters') if params is not None else None
        if raw_filters is not None:
            for f_raw in raw_filters:
                f = as_dict(f_raw)
                if f is None:
                    continue
                f_entry: dict[str, Any] = {}
                f_label = get_str(f, 'label')
                if f_label is not None:
                    f_entry['label'] = f_label
                inp = get_dict(f, 'input')
                if inp is not None:
                    query = get_str(inp, 'query')
                    language = get_str(inp, 'language')
                    if query is not None:
                        if language == 'lucene':
                            f_entry['query'] = {'lucene': query}
                        else:
                            f_entry['query'] = {'kql': query}
                if 'query' in f_entry:
                    filters_list.append(f_entry)
        if not filters_list:
            filters_list = [{'query': {'kql': '*'}}]
        category = 'dimension' if layer_role is not None and col_id == layer_role.get('dimension_id') else 'breakdown'
        return category, {'type': 'filters', 'filters': filters_list}

    return None


def _classify_form_columns(
    layer_columns: dict[str, Any],
    column_order: list[str],
    layer_role: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Classify form-based raw column dicts into metrics, dimensions, breakdowns, skipped."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []
    skipped: list[str] = []

    # Determine iteration order: prefer visualization accessor order
    role_ordered_ids: list[str] = []
    metric_ids: set[str] = set()
    has_role_hints = False
    role_dimension_id: str | None = None
    role_breakdown_id: str | None = None
    if layer_role is not None:
        metric_ids = {metric_id for metric_id in layer_role.get('metric_ids', []) if isinstance(metric_id, str)}
        role_dimension_id = layer_role.get('dimension_id') if isinstance(layer_role.get('dimension_id'), str) else None
        role_breakdown_id = layer_role.get('breakdown_id') if isinstance(layer_role.get('breakdown_id'), str) else None
        used_ids: list[str | None] = [
            *[metric_id for metric_id in layer_role.get('metric_ids', []) if isinstance(metric_id, str)],
            role_dimension_id,
            role_breakdown_id,
        ]
        has_role_hints = any(col_id is not None for col_id in used_ids)
        used_ids.extend([*column_order, *list(layer_columns.keys())])
        for col_id in used_ids:
            if not isinstance(col_id, str):
                continue
            if col_id in layer_columns and col_id not in role_ordered_ids:
                role_ordered_ids.append(col_id)

    if role_ordered_ids and has_role_hints:
        ordered_ids = role_ordered_ids
    elif column_order:
        ordered_ids = column_order
    else:
        ordered_ids = list(layer_columns.keys())

    for col_id in ordered_ids:
        col_raw = as_dict(layer_columns.get(col_id))
        if col_raw is None:
            continue
        if role_ordered_ids and has_role_hints:
            if col_id in metric_ids:
                metric = _build_metric_dict(col_raw)
                if metric is not None:
                    metrics.append(metric)
                    continue
                # Some visualization accessors (e.g. partition "accessor") can point at
                # bucketed terms/filters columns. Classify those as dimensions/breakdowns.
                result = _build_dimension_dict(col_raw, col_id, layer_role)
                if result is not None:
                    category, stub = result
                    if category == 'dimension':
                        dimensions.append(stub)
                    else:
                        breakdowns.append(stub)
                    continue
                # A metric accessor that can't be built directly (e.g. 'differences')
                # may reference underlying metric columns — expand metric_ids so those
                # columns get picked up in a later iteration.
                refs_raw = col_raw.get('references')
                if isinstance(refs_raw, list):
                    for ref_id in refs_raw:
                        if isinstance(ref_id, str):
                            metric_ids.add(ref_id)
                else:
                    operation_type = get_str(col_raw, 'operationType') or 'unknown'
                    skipped.append(operation_type)
                continue
            is_explicit_dimension = col_id == role_dimension_id
            is_explicit_breakdown = col_id == role_breakdown_id
            is_bucketed = col_raw.get('isBucketed') is True
            if is_explicit_dimension or is_explicit_breakdown or is_bucketed:
                result = _build_dimension_dict(col_raw, col_id, layer_role)
                if result is not None:
                    category, stub = result
                    if category == 'dimension':
                        dimensions.append(stub)
                    else:
                        breakdowns.append(stub)
            continue

        is_bucketed = col_raw.get('isBucketed') is True
        if is_bucketed:
            result = _build_dimension_dict(col_raw, col_id, layer_role)
            if result is not None:
                category, stub = result
                if category == 'dimension':
                    dimensions.append(stub)
                else:
                    breakdowns.append(stub)
        else:
            metric = _build_metric_dict(col_raw)
            if metric is not None:
                metrics.append(metric)
            else:
                operation_type = get_str(col_raw, 'operationType') or 'unknown'
                skipped.append(operation_type)

    return metrics, dimensions, breakdowns, skipped


# ---------------------------------------------------------------------------
# ES|QL column extraction
# ---------------------------------------------------------------------------


def _esql_column_entry(col: dict[str, Any]) -> dict[str, Any]:
    """Build an ES|QL column reference dict from a raw column dict."""
    field_name = col.get('fieldName') or ''
    label = col.get('label')
    entry: dict[str, Any] = {'field': field_name}
    if label is not None and label != field_name:
        entry['label'] = label
    return entry


def _classify_esql_columns(
    layer_columns: list[dict[str, Any]],
    layer_role: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify ES|QL columns into metrics, dimensions, breakdowns using layer roles."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []

    if layer_role is None:
        return metrics, dimensions, breakdowns

    columns_by_id: dict[str, dict[str, Any]] = {}
    for col in layer_columns:
        col_id = col.get('columnId')
        if col_id is not None:
            columns_by_id[col_id] = col

    for metric_id in layer_role.get('metric_ids', []):
        col = columns_by_id.get(metric_id)
        if col is not None:
            metrics.append(_esql_column_entry(col))

    dim_id = layer_role.get('dimension_id')
    if dim_id is not None:
        col = columns_by_id.get(dim_id)
        if col is not None:
            dimensions.append(_esql_column_entry(col))

    breakdown_id = layer_role.get('breakdown_id')
    if breakdown_id is not None:
        col = columns_by_id.get(breakdown_id)
        if col is not None:
            breakdowns.append(_esql_column_entry(col))

    return metrics, dimensions, breakdowns


# ---------------------------------------------------------------------------
# Legend extraction
# ---------------------------------------------------------------------------


def _extract_legend_common(  # noqa: PLR0913
    source: dict[str, Any],
    *,
    visible_key: str = 'isVisible',
    visible_is_bool: bool = True,
    position_key: str = 'position',
    truncate_key: str = 'shouldTruncate',
    max_lines_key: str = 'maxLines',
) -> dict[str, Any]:
    """Extract common legend settings from a source dict.

    Returns a (possibly empty) dict of legend settings.
    """
    legend: dict[str, Any] = {}

    if visible_is_bool:
        is_visible = get_bool(source, visible_key)
        if is_visible is not None:
            legend['visible'] = 'show' if is_visible else 'hide'
    else:
        display = get_str(source, visible_key)
        if display in ('show', 'hide'):
            legend['visible'] = display

    position = get_str(source, position_key)
    if position is not None and position != 'right':
        legend['position'] = position

    show_single = get_bool(source, 'showSingleSeries')
    if show_single is not None and show_single:
        legend['show_single_series'] = True

    legend_size = get_str(source, 'legendSize')
    if legend_size is not None and legend_size in KIBANA_LEGEND_SIZE_TO_YAML:
        legend['width'] = KIBANA_LEGEND_SIZE_TO_YAML[legend_size]

    should_truncate = get_bool(source, truncate_key)
    max_lines = get_int(source, max_lines_key)
    if should_truncate is not None and not should_truncate:
        legend['truncate_labels'] = 0
    elif max_lines is not None and max_lines > 0:
        legend['truncate_labels'] = max_lines

    return legend


def _extract_xy_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from an XY visualization state."""
    legend_raw = get_dict(vis_raw, 'legend')
    if legend_raw is None:
        return None
    legend = _extract_legend_common(legend_raw)
    return legend if legend else None


def _extract_partition_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from a partition chart (pie, waffle, mosaic, treemap) visualization layer."""
    layers = get_list(vis_raw, 'layers')
    if layers is None or len(layers) == 0:
        return None
    layer = as_dict(layers[0])
    if layer is None:
        return None
    legend = _extract_legend_common(
        layer,
        visible_key='legendDisplay',
        visible_is_bool=False,
        position_key='legendPosition',
        truncate_key='truncateLegend',
        max_lines_key='legendMaxLines',
    )
    nested_legend = get_bool(layer, 'nestedLegend')
    if nested_legend is not None and nested_legend:
        legend['nested'] = True
    return legend if legend else None


# ---------------------------------------------------------------------------
# XY Appearance extraction
# ---------------------------------------------------------------------------


def _extract_axis_config(
    vis_raw: dict[str, Any],
    scale_key: str,
    title_key: str,
    extent_key: str,
    title_visibility_axis: str,
) -> dict[str, Any] | None:
    """Extract axis configuration (scale, title, extent) for a single axis."""
    axis: dict[str, Any] = {}

    # Axis title visibility — False hides the title regardless of custom text
    title_hidden = False
    axis_vis_settings = get_dict(vis_raw, 'axisTitlesVisibilitySettings')
    if axis_vis_settings is not None:
        show_title = get_bool(axis_vis_settings, title_visibility_axis)
        if show_title is not None and not show_title:
            axis['title'] = False
            title_hidden = True

    # Custom axis title (skip if visibility is explicitly hidden)
    if not title_hidden:
        title_val = get_str(vis_raw, title_key)
        if title_val is not None and len(title_val) > 0:
            axis['title'] = title_val

    # Scale
    scale_val = get_str(vis_raw, scale_key)
    if scale_val is not None and scale_val != 'linear':
        axis['scale'] = scale_val

    # Extent
    extent_raw = get_dict(vis_raw, extent_key)
    if extent_raw is not None:
        mode = get_str(extent_raw, 'mode')
        if mode is not None and mode != 'full':
            extent: dict[str, Any] = {}
            yaml_mode = KIBANA_AXIS_EXTENT_MODE_TO_YAML.get(mode, mode)
            extent['mode'] = yaml_mode
            if mode == 'custom':
                lower = get_number(extent_raw, 'lowerBound')
                upper = get_number(extent_raw, 'upperBound')
                if lower is not None:
                    extent['min'] = lower
                if upper is not None:
                    extent['max'] = upper
            axis['extent'] = extent

    return axis if axis else None


def _extract_xy_appearance(vis_raw: dict[str, Any], chart_type: str | None) -> dict[str, Any] | None:
    """Extract appearance settings from an XY visualization state."""
    appearance: dict[str, Any] = {}

    # Missing values (fitting function) -- line/area only
    if chart_type in {'line', 'area'}:
        fitting = get_str(vis_raw, 'fittingFunction')
        if fitting is not None and fitting in KIBANA_FITTING_FUNCTION_TO_YAML:
            appearance['missing_values'] = KIBANA_FITTING_FUNCTION_TO_YAML[fitting]

        emphasize = get_bool(vis_raw, 'emphasizeFitting')
        if emphasize is not None and emphasize:
            appearance['show_as_dotted'] = True

        end_value = get_str(vis_raw, 'endValue')
        if end_value is not None and end_value in KIBANA_END_VALUE_TO_YAML:
            appearance['end_values'] = KIBANA_END_VALUE_TO_YAML[end_value]

        curve_type = get_str(vis_raw, 'curveType')
        if curve_type is not None and curve_type in KIBANA_CURVE_TYPE_TO_YAML:
            appearance['line_style'] = KIBANA_CURVE_TYPE_TO_YAML[curve_type]

        show_time_marker = get_bool(vis_raw, 'showCurrentTimeMarker')
        if show_time_marker is not None and show_time_marker:
            appearance['show_current_time_marker'] = True

        hide_endzones = get_bool(vis_raw, 'hideEndzones')
        if hide_endzones is not None and hide_endzones:
            appearance['hide_endzones'] = True

    # Fill opacity -- area only
    if chart_type == 'area':
        fill_opacity = get_number(vis_raw, 'fillOpacity')
        if fill_opacity is not None and fill_opacity != KIBANA_DEFAULT_FILL_OPACITY:
            appearance['fill_opacity'] = fill_opacity

    # Min bar height -- bar only
    if chart_type == 'bar':
        min_bar_height = get_number(vis_raw, 'minBarHeight')
        if min_bar_height is not None and min_bar_height > 0:
            appearance['min_bar_height'] = min_bar_height

    # Value labels
    value_labels = get_str(vis_raw, 'valueLabels')
    if value_labels is not None and value_labels == 'show':
        appearance.setdefault('values', {})['visible'] = True

    # Axis configs
    y_left = _extract_axis_config(vis_raw, 'yLeftScale', 'yTitle', 'yLeftExtent', 'yLeft')
    y_left_fallback = _extract_axis_config(vis_raw, 'yLeftScale', 'yLeftTitle', 'yLeftExtent', 'yLeft')
    if y_left is not None and y_left_fallback is not None:
        # Prefer yLeftTitle when present (newer Kibana), while preserving scale/extent fields.
        y_left.update(y_left_fallback)
    elif y_left_fallback is not None:
        y_left = y_left_fallback
    if y_left is not None:
        appearance['y_left_axis'] = y_left

    y_right = _extract_axis_config(vis_raw, 'yRightScale', 'yRightTitle', 'yRightExtent', 'yRight')
    if y_right is not None:
        appearance['y_right_axis'] = y_right

    x_axis = _extract_axis_config(vis_raw, 'xScale', 'xTitle', 'xExtent', 'x')
    if x_axis is not None:
        appearance['x_axis'] = x_axis

    return appearance if appearance else None


# ---------------------------------------------------------------------------
# Gauge / partition / datatable appearance extraction
# ---------------------------------------------------------------------------


def _extract_gauge_settings(
    vis_raw: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Extract gauge appearance and titles_and_text from visualization state raw dict.

    Returns (appearance_dict, titles_and_text_dict) — either may be None.
    """
    appearance: dict[str, Any] = {}
    titles: dict[str, Any] = {}

    shape = get_str(vis_raw, 'shape')
    if shape is not None and shape in KIBANA_GAUGE_SHAPE_TO_YAML and shape != KIBANA_GAUGE_DEFAULT_SHAPE:
        appearance['shape'] = KIBANA_GAUGE_SHAPE_TO_YAML[shape]

    ticks_pos = get_str(vis_raw, 'ticksPosition')
    if ticks_pos is not None and ticks_pos != 'auto':
        appearance['ticks_position'] = ticks_pos

    label_major_mode = get_str(vis_raw, 'labelMajorMode')
    label_major = get_str(vis_raw, 'labelMajor')
    if label_major_mode == 'none':
        titles['title'] = False
    elif label_major_mode in ('custom', None) and label_major is not None and len(label_major) > 0:
        titles['title'] = label_major

    label_minor = get_str(vis_raw, 'labelMinor')
    if label_minor is not None and len(label_minor) > 0:
        titles['subtitle'] = label_minor

    return (appearance if appearance else None), (titles if titles else None)


def _extract_partition_appearance(vis_raw: dict[str, Any], chart_type: str | None = None) -> dict[str, Any] | None:
    """Extract appearance settings from a partition chart (pie/treemap/waffle/mosaic) visualization state."""
    layers = get_list(vis_raw, 'layers')
    if layers is None or len(layers) == 0:
        return None
    layer = as_dict(layers[0])
    if layer is None:
        return None

    appearance: dict[str, Any] = {}

    number_display = get_str(layer, 'numberDisplay')
    if number_display is not None:
        # Pie and treemap use 'integer' for the raw Kibana 'value'; mosaic and waffle use 'value'
        number_display_map = (
            KIBANA_PIE_NUMBER_DISPLAY_TO_YAML if chart_type in (None, 'pie', 'treemap') else KIBANA_PARTITION_NUMBER_DISPLAY_TO_YAML
        )
        if number_display in number_display_map:
            yaml_val = number_display_map[number_display]
            if yaml_val != 'percent':  # percent is Kibana default — omit
                appearance.setdefault('values', {})['format'] = yaml_val

    percent_decimals = get_int(layer, 'percentDecimals')
    if percent_decimals is not None:
        appearance.setdefault('values', {})['decimal_places'] = percent_decimals

    category_display = get_str(layer, 'categoryDisplay')
    if category_display is not None and category_display in KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML:
        yaml_val = KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML[category_display]
        if yaml_val != 'auto':  # auto is Kibana default — omit
            appearance.setdefault('categories', {})['position'] = yaml_val

    return appearance if appearance else None


def _extract_datatable_options(
    vis_raw: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Extract sorting, paging, and appearance from datatable visualization state.

    Returns (sorting_dict, paging_dict, appearance_dict) — any may be None.
    """
    sorting: dict[str, Any] | None = None
    paging: dict[str, Any] | None = None
    appearance: dict[str, Any] = {}

    sorting_raw = get_dict(vis_raw, 'sorting')
    if sorting_raw is not None:
        col_id = get_str(sorting_raw, 'columnId')
        direction = get_str(sorting_raw, 'direction')
        if col_id is not None and direction is not None and direction != 'none':
            sorting = {'column_id': col_id, 'direction': direction}

    paging_raw = get_dict(vis_raw, 'paging')
    if paging_raw is not None:
        enabled = get_bool(paging_raw, 'enabled')
        size = get_int(paging_raw, 'size')
        if enabled is not None and size is not None:
            paging = {'enabled': enabled, 'page_size': size}

    row_height = get_str(vis_raw, 'rowHeight')
    if row_height is not None and row_height != 'auto':
        appearance['row_height'] = row_height

    row_height_lines = get_int(vis_raw, 'rowHeightLines')
    if row_height_lines is not None:
        appearance['row_height_lines'] = row_height_lines

    header_row_height = get_str(vis_raw, 'headerRowHeight')
    if header_row_height is not None and header_row_height != 'auto':
        appearance['header_row_height'] = header_row_height

    header_row_height_lines = get_int(vis_raw, 'headerRowHeightLines')
    if header_row_height_lines is not None:
        appearance['header_row_height_lines'] = header_row_height_lines

    density = get_str(vis_raw, 'density')
    if density is not None and density != 'normal':
        appearance['density'] = density

    return sorting, paging, (appearance if appearance else None)


# ---------------------------------------------------------------------------
# Metrics / dimensions / defaults assignment
# ---------------------------------------------------------------------------


def _assign_metrics_and_dimensions(
    chart: dict[str, Any],
    chart_type: str,
    all_metrics: list[dict[str, Any]],
    all_dimensions: list[dict[str, Any]],
    all_breakdowns: list[dict[str, Any]],
) -> None:
    """Assign extracted metrics, dimensions, and breakdowns to the chart dict based on chart type."""
    is_xy = chart_type in _XY_CHART_TYPES
    is_heatmap = chart_type == 'heatmap'

    # -- Metrics --
    if chart_type == 'metric':
        if len(all_metrics) > 0:
            chart['primary'] = all_metrics[0]
        if len(all_metrics) > 1:
            chart['secondary'] = all_metrics[1]
    elif is_heatmap or chart_type in _SINGULAR_METRIC_TYPES:
        if len(all_metrics) > 0:
            chart['metric'] = all_metrics[0]
    elif chart_type in _PLURAL_METRIC_TYPES and len(all_metrics) > 0:
        chart['metrics'] = all_metrics

    # -- Dimensions --
    if is_xy:
        if len(all_dimensions) > 0:
            chart['dimension'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['breakdown'] = all_breakdowns[0]
    elif is_heatmap:
        if len(all_dimensions) > 0:
            chart['x_axis'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['y_axis'] = all_breakdowns[0]
        elif len(all_dimensions) > 1:
            chart['y_axis'] = all_dimensions[1]
    elif chart_type in _SINGULAR_DIM_TYPES:
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            if chart_type in ('metric', 'waffle'):
                chart['breakdown'] = merged[0]
            else:
                chart['dimension'] = merged[0]
        if chart_type == 'mosaic' and len(merged) > 1:
            chart['breakdown'] = merged[1]
    elif chart_type != 'gauge':
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            chart['breakdowns'] = merged


def _fill_required_defaults(
    chart: dict[str, Any],
    chart_type: str,
    panel_type: str,
    has_skipped_metrics: bool,
) -> None:
    """Fill in TODO placeholder defaults for incomplete panels so the YAML is still valid."""
    default_metric: dict[str, Any]
    default_dim: dict[str, Any]

    if panel_type == 'lens':
        if has_skipped_metrics:
            default_metric = {'aggregation': 'sum', 'field': 'TODO_unsupported_metric_field', 'label': 'TODO_unsupported_metric'}
        else:
            default_metric = {'aggregation': 'count'}
        default_dim = {'type': 'values', 'field': 'TODO_field'}
        if 'data_view' not in chart:
            chart['data_view'] = 'TODO_data_view'
    else:
        default_metric = {'field': 'TODO_metric_field'}
        default_dim = {'field': 'TODO_dimension_field'}

    is_xy = chart_type in _XY_CHART_TYPES
    is_partition = chart_type in _PARTITION_TYPES

    if chart_type == 'metric' and 'primary' not in chart:
        chart['primary'] = default_metric
    if is_xy and 'metrics' not in chart:
        chart['metrics'] = [default_metric]
    if is_partition:
        if chart_type != 'treemap' and 'metrics' not in chart:
            chart['metrics'] = [default_metric]
        if 'breakdowns' not in chart:
            chart['breakdowns'] = [default_dim]
    if chart_type == 'datatable' and 'metrics' not in chart and 'breakdowns' not in chart:
        chart['metrics'] = [default_metric]
    if chart_type == 'heatmap':
        if 'x_axis' not in chart:
            chart['x_axis'] = default_dim
        if 'metric' not in chart:
            chart['metric'] = default_metric
    if chart_type in _SINGULAR_METRIC_TYPES and 'metric' not in chart:
        chart['metric'] = default_metric
    if chart_type in _SINGULAR_DIM_TYPES:
        if chart_type == 'metric':
            pass  # breakdown is optional for metric
        elif chart_type == 'waffle':
            if 'breakdown' not in chart:
                chart['breakdown'] = default_dim
        elif 'dimension' not in chart:
            chart['dimension'] = default_dim


# ---------------------------------------------------------------------------
# Panel type detection helpers
# ---------------------------------------------------------------------------


def _is_esql_panel_dict(panel_dict: dict[str, Any]) -> bool:
    """Return True if this panel uses the textBased (ES|QL) datasource."""
    ds_states = get_nested(panel_dict, 'embeddableConfig', 'attributes', 'state', 'datasourceStates')
    if ds_states is not None:
        text_based_layers = get_nested(ds_states, 'textBased', 'layers')
        if isinstance(text_based_layers, dict) and text_based_layers:
            return True
    query = get_nested(panel_dict, 'embeddableConfig', 'attributes', 'state', 'query')
    return query is not None and query.get('esql') is not None


def _extract_data_view_id_dict(panel_dict: dict[str, Any]) -> str | None:
    """Extract the data view ID from panel references."""
    attrs = get_nested(panel_dict, 'embeddableConfig', 'attributes')
    if attrs is None:
        return None
    refs = attrs.get('references')
    if not isinstance(refs, list):
        return None
    for ref in refs:
        ref_dict = as_dict(ref)
        if ref_dict is None:
            continue
        if get_str(ref_dict, 'type') == 'index-pattern':
            ref_id = get_str(ref_dict, 'id')
            if ref_id is not None:
                return ref_id
    return None


def _extract_esql_query_dict(panel_dict: dict[str, Any]) -> str | None:
    """Extract the ES|QL query string from a panel dict."""
    state = get_nested(panel_dict, 'embeddableConfig', 'attributes', 'state')
    if state is None:
        return None
    # Top-level query
    query = get_dict(state, 'query')
    if query is not None:
        esql = get_str(query, 'esql')
        if esql is not None:
            return esql
    # Layer queries
    ds_states = get_dict(state, 'datasourceStates')
    if ds_states is None:
        return None
    text_based_layers = get_nested(ds_states, 'textBased', 'layers')
    if isinstance(text_based_layers, dict):
        for layer_raw in text_based_layers.values():
            layer = as_dict(layer_raw)
            if layer is None:
                continue
            layer_query = get_dict(layer, 'query')
            if layer_query is not None:
                esql = get_str(layer_query, 'esql')
                if esql is not None:
                    return esql
    return None


# ---------------------------------------------------------------------------
# Panel inference
# ---------------------------------------------------------------------------


def _extract_raw_vis_type(panel_dict: dict[str, Any]) -> str | None:
    """Extract the raw visualizationType string from a panel dict."""
    attrs = get_nested(panel_dict, 'embeddableConfig', 'attributes')
    if attrs is None:
        return None
    vis_type = attrs.get('visualizationType')
    return vis_type if isinstance(vis_type, str) else None


def _infer_lens_chart(panel_dict: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Build chart config dict from a raw Kibana Lens/ES|QL panel dict.

    Returns (panel_type, chart_config_dict) where panel_type is 'lens' or 'esql'.
    """
    original_type = panel_dict.get('type')
    raw_vis_type = _extract_raw_vis_type(panel_dict)

    # Detect ESQL: explicit type='esql' or textBased datasource state
    is_esql = original_type == 'esql' or _is_esql_panel_dict(panel_dict)
    panel_type = 'esql' if is_esql else 'lens'

    chart: dict[str, Any] = {}

    # Extract visualization state as raw dict
    vis_raw: dict[str, Any] = {}
    vis_state = get_nested(panel_dict, 'embeddableConfig', 'attributes', 'state', 'visualization')
    if isinstance(vis_state, dict):
        vis_raw = vis_state
    elif vis_state is not None and hasattr(vis_state, 'model_dump'):
        vis_raw = vis_state.model_dump(exclude_none=True, by_alias=True)

    preferred_series_type = get_str(vis_raw, 'preferredSeriesType')
    shape = get_str(vis_raw, 'shape')

    # Override vis_raw with preferred_series_type / shape for type resolution
    if preferred_series_type is not None and 'preferredSeriesType' not in vis_raw:
        vis_raw = dict(vis_raw)
        vis_raw['preferredSeriesType'] = preferred_series_type
    if shape is not None and 'shape' not in vis_raw:
        vis_raw = dict(vis_raw)
        vis_raw['shape'] = shape

    # Resolve chart type
    chart_type: str | None = _resolve_vis_type(vis_raw, raw_vis_type)
    if chart_type is not None:
        chart['type'] = chart_type
        mode = _resolve_stacking_mode(vis_raw, chart_type)
        if mode is not None:
            chart['mode'] = mode
        # Donut detection
        if chart_type == 'pie' and shape == 'donut':
            chart.setdefault('appearance', {})['donut'] = 'medium'
    if chart_type is None:
        chart_type = 'metric'
        chart['type'] = chart_type

    # Extract legend and appearance from visualization state
    if vis_raw:
        if chart_type in _XY_CHART_TYPES:
            legend = _extract_xy_legend(vis_raw)
        elif chart_type in PARTITION_CHART_TYPES:
            legend = _extract_partition_legend(vis_raw)
        else:
            legend = None
        if legend is not None:
            chart['legend'] = legend

        if chart_type in _XY_CHART_TYPES:
            _merge_appearance(chart, _extract_xy_appearance(vis_raw, chart_type))
        elif chart_type == 'gauge':
            gauge_appearance, gauge_titles = _extract_gauge_settings(vis_raw)
            _merge_appearance(chart, gauge_appearance)
            if gauge_titles is not None:
                chart['titles_and_text'] = gauge_titles
        elif chart_type in PARTITION_CHART_TYPES:
            _merge_appearance(chart, _extract_partition_appearance(vis_raw, chart_type))
        elif chart_type == 'datatable':
            dt_sorting, dt_paging, dt_appearance = _extract_datatable_options(vis_raw)
            if dt_sorting is not None:
                chart['sorting'] = dt_sorting
            if dt_paging is not None:
                chart['paging'] = dt_paging
            if dt_appearance is not None:
                chart['appearance'] = dt_appearance

    # Data view / query
    if panel_type == 'lens':
        data_view_id = _extract_data_view_id_dict(panel_dict)
        if data_view_id is not None:
            chart['data_view'] = data_view_id

    if panel_type == 'esql':
        esql_query = _extract_esql_query_dict(panel_dict)
        chart['query'] = esql_query if esql_query is not None else 'TODO_esql_query'

    # Extract metrics/dimensions/breakdowns
    all_metrics: list[dict[str, Any]] = []
    all_dimensions: list[dict[str, Any]] = []
    all_breakdowns: list[dict[str, Any]] = []
    has_skipped_metrics = False

    layer_roles = _parse_layer_roles_from_vis(vis_raw)

    ds_states = get_nested(panel_dict, 'embeddableConfig', 'attributes', 'state', 'datasourceStates')

    if panel_type == 'esql' and ds_states is not None:
        text_based_layers = get_nested(ds_states, 'textBased', 'layers')
        if isinstance(text_based_layers, dict):
            for layer_id, layer_raw in text_based_layers.items():
                layer = as_dict(layer_raw) or {}
                role = layer_roles.get(layer_id)
                all_layer_cols: list[Any] = []
                seen_ids: set[str] = set()
                for col_list_key in ('columns', 'allColumns'):
                    col_list = layer.get(col_list_key)
                    if not isinstance(col_list, list):
                        continue
                    for col in col_list:
                        col_dict = as_dict(col)
                        if col_dict is None:
                            continue
                        col_id = col_dict.get('columnId')
                        if col_id is not None and col_id not in seen_ids:
                            seen_ids.add(col_id)
                            all_layer_cols.append(col_dict)
                m, d, b = _classify_esql_columns(all_layer_cols, role)
                all_metrics.extend(m)
                all_dimensions.extend(d)
                all_breakdowns.extend(b)
    elif panel_type == 'lens' and ds_states is not None:
        form_based = get_dict(ds_states, 'formBased')
        if form_based is not None:
            layers = get_dict(form_based, 'layers') or {}
            for layer_id, layer_raw in layers.items():
                layer = as_dict(layer_raw) or {}
                role = layer_roles.get(layer_id)
                column_order_raw = layer.get('columnOrder')
                column_order = column_order_raw if isinstance(column_order_raw, list) else []
                columns_raw = get_dict(layer, 'columns') or {}
                m, d, b, skipped = _classify_form_columns(columns_raw, column_order, role)
                all_metrics.extend(m)
                all_dimensions.extend(d)
                all_breakdowns.extend(b)
                if skipped:
                    has_skipped_metrics = True

    _assign_metrics_and_dimensions(chart, chart_type, all_metrics, all_dimensions, all_breakdowns)
    _fill_required_defaults(chart, chart_type, panel_type, has_skipped_metrics)

    try:
        _ = _lens_panel_adapter.validate_python(chart) if panel_type == 'lens' else _esql_panel_adapter.validate_python(chart)
    except ValidationError as exc:
        msg = f'infer_lens_chart produced invalid chart dict (type={chart_type}): {exc}'
        raise ValueError(msg) from exc

    return panel_type, chart
