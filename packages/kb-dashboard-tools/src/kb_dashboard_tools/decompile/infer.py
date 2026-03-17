"""Phase 2: Infer Dashboard config objects from parsed intermediate structures.

Maps parsed Kibana/Kbn view data to actual kb-dashboard-core config models,
producing dicts that can be validated into ``Dashboard`` instances.
"""

import logging
from typing import Any

from kb_dashboard_core.dashboard.config import Dashboard

from .parse import (
    ParsedColumn,
    ParsedControl,
    ParsedDashboard,
    ParsedESQLColumn,
    ParsedESQLLayer,
    ParsedFilter,
    ParsedFormLayer,
    ParsedLensPanel,
    ParsedPanel,
    ParsedSimplePanel,
    ParsedVisualizationLayerRole,
    ParsedVisualizationState,
    as_dict,
)
from .tables import (
    CONTROL_TYPE_MAP,
    KIBANA_AXIS_EXTENT_MODE_TO_YAML,
    KIBANA_CURVE_TYPE_TO_YAML,
    KIBANA_DEFAULT_FILL_OPACITY,
    KIBANA_END_VALUE_TO_YAML,
    KIBANA_FITTING_FUNCTION_TO_YAML,
    KIBANA_LEGEND_SIZE_TO_YAML,
    LENS_VISUALIZATION_TYPES,
    OPERATION_TYPE_MAP,
    PARTITION_CHART_TYPES,
    PIE_SHAPES,
    SKIP_OPERATION_TYPES,
    XY_SERIES_TYPES,
    XY_STACKING_MODES,
)

logger = logging.getLogger(__name__)

# Chart-type classification sets (reused across functions)
_XY_CHART_TYPES = frozenset({'line', 'bar', 'area'})
_SINGULAR_METRIC_TYPES = frozenset({'gauge', 'tagcloud', 'waffle', 'mosaic'})
_SINGULAR_DIM_TYPES = frozenset({'tagcloud', 'waffle', 'mosaic'})
_PARTITION_TYPES = frozenset({'pie', 'treemap'})
_PLURAL_METRIC_TYPES = frozenset({'pie', 'treemap', 'datatable', 'line', 'bar', 'area'})

# Sentinel field name Kibana uses for record-count metrics
_RECORDS_FIELD = 'Records'

# ---------------------------------------------------------------------------
# Chart type resolution
# ---------------------------------------------------------------------------


def _resolve_chart_type(vis_state: ParsedVisualizationState) -> str | None:
    """Map Kibana visualization type + series preferences to a YAML chart type."""
    raw = vis_state.raw_type
    if raw is None:
        return None
    normalized = LENS_VISUALIZATION_TYPES.get(raw.lower())
    if raw.lower() in {'lnsxy', 'xy'}:
        pst = vis_state.preferred_series_type
        if pst is not None:
            return XY_SERIES_TYPES.get(pst, 'line')
        return 'line'
    if raw.lower() in {'lnspie', 'pie'}:
        shape = vis_state.shape
        if shape is not None:
            resolved = PIE_SHAPES.get(shape)
            if resolved is not None and resolved != 'pie':
                return resolved
    return normalized


def _resolve_stacking_mode(vis_state: ParsedVisualizationState, chart_type: str | None) -> str | None:
    """Determine stacking mode (stacked/percentage) for bar and area charts."""
    if chart_type not in {'bar', 'area'}:
        return None
    pst = vis_state.preferred_series_type
    if pst is None:
        return None
    return XY_STACKING_MODES.get(pst)


# ---------------------------------------------------------------------------
# Metric / dimension / breakdown extraction (form-based)
# ---------------------------------------------------------------------------


def _extract_metric_filter(col: ParsedColumn) -> dict[str, str] | None:
    """Extract the metric-level KQL/Lucene filter from a column, if present."""
    if col.filter_query is not None:
        if col.filter_language == 'kuery':
            return {'kql': col.filter_query}
        if col.filter_language == 'lucene':
            return {'lucene': col.filter_query}
    kql = col.params.get('kql')
    if isinstance(kql, str) and len(kql) > 0:
        return {'kql': kql}
    return None


def _extract_metric_format(col: ParsedColumn) -> dict[str, Any] | None:
    """Extract number/byte/percent format configuration from a column."""
    format_config = as_dict(col.params.get('format'))
    if format_config is None:
        return None
    format_type = format_config.get('id')
    if not (isinstance(format_type, str) and format_type in {'number', 'bytes', 'bits', 'percent', 'duration', 'custom'}):
        return None
    fmt: dict[str, Any] = {'type': format_type}
    format_params = as_dict(format_config.get('params'))
    if format_params is None:
        return fmt
    for key in ('decimals', 'suffix', 'compact', 'pattern'):
        val = format_params.get(key)
        if val is not None:
            fmt[key] = val
    return fmt


def _build_metric_dict(col: ParsedColumn) -> dict[str, Any] | None:
    """Build a metric config dict from a form-based column. Returns None if skipped."""
    if col.operation_type in SKIP_OPERATION_TYPES:
        return None

    # Formula metrics bypass the normal aggregation mapping
    if col.operation_type == 'formula':
        formula_str = col.params.get('formula')
        if not isinstance(formula_str, str):
            return None
        metric: dict[str, Any] = {'formula': formula_str}
        if col.label is not None and len(col.label) > 0:
            metric['label'] = col.label
        fmt = _extract_metric_format(col)
        if fmt is not None:
            metric['format'] = fmt
        return metric

    aggregation = OPERATION_TYPE_MAP.get(col.operation_type)
    if aggregation is None:
        return None

    metric = {'aggregation': aggregation}
    if col.source_field is not None and col.source_field != _RECORDS_FIELD:
        metric['field'] = col.source_field
    if col.label is not None and len(col.label) > 0:
        metric['label'] = col.label

    # Extract percentile-specific parameters
    if col.operation_type == 'percentile':
        percentile_val = col.params.get('percentile')
        if isinstance(percentile_val, (int, float)):
            metric['percentile'] = int(percentile_val)
    elif col.operation_type == 'percentile_rank':
        rank_val = col.params.get('value')
        if isinstance(rank_val, (int, float)):
            metric['rank'] = rank_val

    filt = _extract_metric_filter(col)
    if filt is not None:
        metric['filter'] = filt
    fmt = _extract_metric_format(col)
    if fmt is not None:
        metric['format'] = fmt
    return metric


def _build_dimension_dict(col: ParsedColumn) -> tuple[str, dict[str, Any]] | None:
    """Build a dimension or breakdown dict. Returns (category, dict) or None."""
    if col.operation_type == 'date_histogram':
        dim: dict[str, Any] = {'type': 'date_histogram'}
        if col.source_field is not None:
            dim['field'] = col.source_field
        interval = col.params.get('interval')
        if isinstance(interval, str) and interval != 'auto':
            dim['minimum_interval'] = interval
        return 'dimension', dim

    if col.operation_type == 'terms':
        bd: dict[str, Any] = {'type': 'values'}
        if col.source_field is not None:
            bd['field'] = col.source_field
        size = col.params.get('size')
        if isinstance(size, int):
            bd['size'] = size
        return 'breakdown', bd

    if col.operation_type == 'filters':
        filters_list: list[dict[str, Any]] = []
        raw_filters = col.params.get('filters')
        if isinstance(raw_filters, list):
            for f in raw_filters:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(f, dict):
                    f_entry: dict[str, Any] = {}
                    label = f.get('label')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                    if isinstance(label, str):
                        f_entry['label'] = label
                    inp = f.get('input')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                    if isinstance(inp, dict):
                        query = inp.get('query')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                        language = inp.get('language')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                        if isinstance(query, str):
                            if language == 'lucene':
                                f_entry['query'] = {'lucene': query}
                            else:
                                f_entry['query'] = {'kql': query}
                    if 'query' in f_entry:
                        filters_list.append(f_entry)
        if not filters_list:
            filters_list = [{'query': {'kql': '*'}}]
        return 'breakdown', {'type': 'filters', 'filters': filters_list}

    return None


def _classify_form_columns(
    layer: ParsedFormLayer,
    layer_role: ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Classify form-based columns into metrics, dimensions, breakdowns, skipped."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []
    skipped: list[str] = []

    # Determine iteration order: prefer visualization accessor order
    if layer_role is not None and layer_role.accessors:
        ordered_ids = list(dict.fromkeys([*layer_role.accessors, *layer.column_order, *list(layer.columns.keys())]))
    elif layer.column_order:
        ordered_ids = layer.column_order
    else:
        ordered_ids = list(layer.columns.keys())

    for col_id in ordered_ids:
        col = layer.columns.get(col_id)
        if col is None:
            continue
        if col.is_bucketed:
            result = _build_dimension_dict(col)
            if result is not None:
                category, stub = result
                if category == 'dimension':
                    dimensions.append(stub)
                else:
                    breakdowns.append(stub)
        else:
            metric = _build_metric_dict(col)
            if metric is not None:
                metrics.append(metric)
            elif col.operation_type in SKIP_OPERATION_TYPES:
                skipped.append(col.operation_type)
            else:
                skipped.append(col.operation_type)

    return metrics, dimensions, breakdowns, skipped


# ---------------------------------------------------------------------------
# ES|QL column extraction
# ---------------------------------------------------------------------------


def _classify_esql_columns(
    layer: ParsedESQLLayer,
    layer_role: ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify ES|QL columns into metrics, dimensions, breakdowns using layer roles."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []

    columns_by_id: dict[str, ParsedESQLColumn] = {c.column_id: c for c in layer.columns}

    if layer_role is None:
        return metrics, dimensions, breakdowns

    for metric_id in layer_role.metric_ids:
        col = columns_by_id.get(metric_id)
        if col is None:
            continue
        m: dict[str, Any] = {'field': col.field_name}
        if col.label is not None and col.label != col.field_name:
            m['label'] = col.label
        metrics.append(m)

    if layer_role.dimension_id is not None:
        col = columns_by_id.get(layer_role.dimension_id)
        if col is not None:
            d: dict[str, Any] = {'field': col.field_name}
            if col.label is not None and col.label != col.field_name:
                d['label'] = col.label
            dimensions.append(d)

    if layer_role.breakdown_id is not None:
        col = columns_by_id.get(layer_role.breakdown_id)
        if col is not None:
            b: dict[str, Any] = {'field': col.field_name}
            if col.label is not None and col.label != col.field_name:
                b['label'] = col.label
            breakdowns.append(b)

    return metrics, dimensions, breakdowns


# ---------------------------------------------------------------------------
# Legend extraction
# ---------------------------------------------------------------------------


def _extract_xy_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from an XY visualization state."""
    legend_raw = as_dict(vis_raw.get('legend'))
    if legend_raw is None:
        return None

    legend: dict[str, Any] = {}

    is_visible = legend_raw.get('isVisible')
    if isinstance(is_visible, bool):
        legend['visible'] = 'show' if is_visible else 'hide'

    position = legend_raw.get('position')
    if isinstance(position, str) and position != 'right':
        legend['position'] = position

    show_single = legend_raw.get('showSingleSeries')
    if isinstance(show_single, bool) and show_single:
        legend['show_single_series'] = True

    legend_size = legend_raw.get('legendSize')
    if isinstance(legend_size, str) and legend_size in KIBANA_LEGEND_SIZE_TO_YAML:
        legend['width'] = KIBANA_LEGEND_SIZE_TO_YAML[legend_size]

    should_truncate = legend_raw.get('shouldTruncate')
    max_lines = legend_raw.get('maxLines')
    if isinstance(should_truncate, bool) and not should_truncate:
        legend['truncate_labels'] = 0
    elif isinstance(max_lines, int) and max_lines > 0:
        legend['truncate_labels'] = max_lines

    return legend if legend else None


def _extract_partition_legend(vis_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract legend settings from a partition chart (pie, waffle, mosaic, treemap) visualization layer."""
    layers = vis_raw.get('layers')
    if not isinstance(layers, list) or len(layers) == 0:  # pyright: ignore[reportUnknownArgumentType]
        return None
    layer = as_dict(layers[0])  # pyright: ignore[reportUnknownArgumentType]
    if layer is None:
        return None

    legend: dict[str, Any] = {}

    legend_display = layer.get('legendDisplay')
    if isinstance(legend_display, str):
        if legend_display == 'hide':
            legend['visible'] = 'hide'
        elif legend_display == 'show':
            legend['visible'] = 'show'

    legend_position = layer.get('legendPosition')
    if isinstance(legend_position, str) and legend_position != 'right':
        legend['position'] = legend_position

    show_single = layer.get('showSingleSeries')
    if isinstance(show_single, bool) and show_single:
        legend['show_single_series'] = True

    legend_size = layer.get('legendSize')
    if isinstance(legend_size, str) and legend_size in KIBANA_LEGEND_SIZE_TO_YAML:
        legend['width'] = KIBANA_LEGEND_SIZE_TO_YAML[legend_size]

    truncate_legend = layer.get('truncateLegend')
    legend_max_lines = layer.get('legendMaxLines')
    if isinstance(truncate_legend, bool) and not truncate_legend:
        legend['truncate_labels'] = 0
    elif isinstance(legend_max_lines, int) and legend_max_lines > 0:
        legend['truncate_labels'] = legend_max_lines

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
    axis_vis_settings = as_dict(vis_raw.get('axisTitlesVisibilitySettings'))
    if axis_vis_settings is not None:
        show_title = axis_vis_settings.get(title_visibility_axis)
        if isinstance(show_title, bool) and not show_title:
            axis['title'] = False
            title_hidden = True

    # Custom axis title (skip if visibility is explicitly hidden)
    if not title_hidden:
        title_val = vis_raw.get(title_key)
        if isinstance(title_val, str) and len(title_val) > 0:
            axis['title'] = title_val

    # Scale
    scale_val = vis_raw.get(scale_key)
    if isinstance(scale_val, str) and scale_val != 'linear':
        axis['scale'] = scale_val

    # Extent
    extent_raw = as_dict(vis_raw.get(extent_key))
    if extent_raw is not None:
        mode = extent_raw.get('mode')
        if isinstance(mode, str) and mode != 'full':
            extent: dict[str, Any] = {}
            yaml_mode = KIBANA_AXIS_EXTENT_MODE_TO_YAML.get(mode, mode)
            extent['mode'] = yaml_mode
            if mode == 'custom':
                lower = extent_raw.get('lowerBound')
                upper = extent_raw.get('upperBound')
                if isinstance(lower, (int, float)):
                    extent['min'] = lower
                if isinstance(upper, (int, float)):
                    extent['max'] = upper
            axis['extent'] = extent

    return axis if axis else None


def _extract_xy_appearance(vis_raw: dict[str, Any], chart_type: str | None) -> dict[str, Any] | None:
    """Extract appearance settings from an XY visualization state."""
    appearance: dict[str, Any] = {}

    # Missing values (fitting function) -- line/area only
    if chart_type in {'line', 'area'}:
        fitting = vis_raw.get('fittingFunction')
        if isinstance(fitting, str) and fitting in KIBANA_FITTING_FUNCTION_TO_YAML:
            appearance['missing_values'] = KIBANA_FITTING_FUNCTION_TO_YAML[fitting]

        emphasize = vis_raw.get('emphasizeFitting')
        if isinstance(emphasize, bool) and emphasize:
            appearance['show_as_dotted'] = True

        end_value = vis_raw.get('endValue')
        if isinstance(end_value, str) and end_value in KIBANA_END_VALUE_TO_YAML:
            appearance['end_values'] = KIBANA_END_VALUE_TO_YAML[end_value]

        curve_type = vis_raw.get('curveType')
        if isinstance(curve_type, str) and curve_type in KIBANA_CURVE_TYPE_TO_YAML:
            appearance['line_style'] = KIBANA_CURVE_TYPE_TO_YAML[curve_type]

        show_time_marker = vis_raw.get('showCurrentTimeMarker')
        if isinstance(show_time_marker, bool) and show_time_marker:
            appearance['show_current_time_marker'] = True

        hide_endzones = vis_raw.get('hideEndzones')
        if isinstance(hide_endzones, bool) and hide_endzones:
            appearance['hide_endzones'] = True

    # Fill opacity -- area only
    if chart_type == 'area':
        fill_opacity = vis_raw.get('fillOpacity')
        if isinstance(fill_opacity, (int, float)) and fill_opacity != KIBANA_DEFAULT_FILL_OPACITY:
            appearance['fill_opacity'] = fill_opacity

    # Min bar height -- bar only
    if chart_type == 'bar':
        min_bar_height = vis_raw.get('minBarHeight')
        if isinstance(min_bar_height, (int, float)) and min_bar_height > 0:
            appearance['min_bar_height'] = min_bar_height

    # Value labels
    value_labels = vis_raw.get('valueLabels')
    if isinstance(value_labels, str) and value_labels == 'show':
        appearance.setdefault('values', {})['visible'] = True

    # Axis configs
    y_left = _extract_axis_config(vis_raw, 'yLeftScale', 'yTitle', 'yLeftExtent', 'yLeft')
    if y_left is None:
        # Also check yLeftTitle (newer Kibana)
        y_left = _extract_axis_config(vis_raw, 'yLeftScale', 'yLeftTitle', 'yLeftExtent', 'yLeft')
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
            if chart_type == 'waffle':
                chart['breakdown'] = merged[0]
            else:
                chart['dimension'] = merged[0]
        if chart_type == 'mosaic' and len(merged) > 1:
            chart['breakdown'] = merged[1]
    else:
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
        if 'metrics' not in chart:
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
        if chart_type == 'waffle':
            if 'breakdown' not in chart:
                chart['breakdown'] = default_dim
        elif 'dimension' not in chart:
            chart['dimension'] = default_dim


# ---------------------------------------------------------------------------
# Panel inference
# ---------------------------------------------------------------------------


def _infer_lens_chart(parsed: ParsedLensPanel) -> dict[str, Any]:
    """Build chart config dict from a parsed Lens/ES|QL panel."""
    chart: dict[str, Any] = {}
    vis_state = parsed.visualization_state

    # Resolve chart type
    chart_type: str | None = None
    if vis_state is not None:
        chart_type = _resolve_chart_type(vis_state)
        if chart_type is not None:
            chart['type'] = chart_type
            mode = _resolve_stacking_mode(vis_state, chart_type)
            if mode is not None:
                chart['mode'] = mode
            # Donut detection
            if chart_type == 'pie' and vis_state.shape == 'donut':
                chart.setdefault('appearance', {})['donut'] = 'medium'
    if chart_type is None:
        chart_type = 'metric'
        chart['type'] = chart_type

    # Extract legend and appearance from visualization state
    if vis_state is not None:
        vis_raw = vis_state.raw

        # Legend extraction
        if chart_type in _XY_CHART_TYPES:
            legend = _extract_xy_legend(vis_raw)
        elif chart_type in PARTITION_CHART_TYPES:
            legend = _extract_partition_legend(vis_raw)
        else:
            legend = None
        if legend is not None:
            chart['legend'] = legend

        # XY appearance extraction
        if chart_type in _XY_CHART_TYPES:
            xy_appearance = _extract_xy_appearance(vis_raw, chart_type)
            if xy_appearance is not None:
                existing = chart.get('appearance')
                if isinstance(existing, dict):
                    existing.update(xy_appearance)  # pyright: ignore[reportUnknownMemberType]
                else:
                    chart['appearance'] = xy_appearance

    # Data view / query
    if parsed.panel_type == 'lens' and parsed.data_view_id is not None:
        chart['data_view'] = parsed.data_view_id

    esql_query: str | None = None
    if parsed.panel_type == 'esql':
        # Check top-level query first, then layer queries
        esql_query = parsed.esql_query
        if esql_query is None:
            for layer in parsed.esql_layers.values():
                esql_query = layer.query
                break
        chart['query'] = esql_query if esql_query is not None else 'TODO_esql_query'

    # Extract metrics/dimensions/breakdowns
    all_metrics: list[dict[str, Any]] = []
    all_dimensions: list[dict[str, Any]] = []
    all_breakdowns: list[dict[str, Any]] = []
    has_skipped_metrics = False

    if parsed.panel_type == 'esql':
        for layer_id, layer in parsed.esql_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b = _classify_esql_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
    else:
        for layer_id, layer in parsed.form_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b, skipped = _classify_form_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
            if skipped:
                has_skipped_metrics = True

    _assign_metrics_and_dimensions(chart, chart_type, all_metrics, all_dimensions, all_breakdowns)
    _fill_required_defaults(chart, chart_type, parsed.panel_type, has_skipped_metrics)

    return chart


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


def _infer_filter(pf: ParsedFilter) -> dict[str, Any]:
    """Infer a single filter config dict."""
    f: dict[str, Any] = {}
    if pf.filter_type == 'exists':
        f['exists'] = pf.key
    elif pf.filter_type == 'phrase':
        f['field'] = pf.key
        params = pf.meta.get('params')
        if isinstance(params, dict):
            query = params.get('query')  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
            if isinstance(query, (str, int, float, bool)):
                f['equals'] = query
        else:
            value = pf.meta.get('value')
            if isinstance(value, (str, int, float, bool)):
                f['equals'] = value
    elif pf.filter_type == 'phrases':
        f['field'] = pf.key
        params = pf.meta.get('params')
        if isinstance(params, list):
            f['in'] = [p for p in params if isinstance(p, (str, int, float, bool))]  # pyright: ignore[reportUnknownVariableType]
    elif pf.filter_type == 'range':
        f['field'] = pf.key
        range_params = as_dict(pf.raw.get('range'))
        if range_params is not None:
            field_range = as_dict(range_params.get(pf.key))
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = field_range.get(bound)
                    if isinstance(val, (str, int, float, bool)):
                        f[bound] = val
    else:
        f['field'] = pf.key

    # Apply metadata
    disabled = pf.meta.get('disabled')
    if isinstance(disabled, bool) and disabled:
        f['disabled'] = True
    alias = pf.meta.get('alias')
    if isinstance(alias, str) and len(alias) > 0:
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
        dashboard['filters'] = [_infer_filter(f) for f in parsed.filters]

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
