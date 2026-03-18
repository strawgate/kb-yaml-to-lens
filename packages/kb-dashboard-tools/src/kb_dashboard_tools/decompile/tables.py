"""Mapping tables for Kibana JSON → Dashboard YAML decompilation."""

LENS_VISUALIZATION_TYPES: dict[str, str | None] = {
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
    'lnsxy': None,  # resolved via preferredSeriesType
}

XY_SERIES_TYPES: dict[str, str] = {
    'line': 'line',
    'bar': 'bar',
    'bar_stacked': 'bar',
    'bar_horizontal': 'bar',
    'bar_horizontal_stacked': 'bar',
    'bar_percentage_stacked': 'bar',
    'bar_horizontal_percentage_stacked': 'bar',
    'area': 'area',
    'area_stacked': 'area',
    'area_percentage_stacked': 'area',
}

XY_STACKING_MODES: dict[str, str] = {
    'bar_stacked': 'stacked',
    'bar_horizontal_stacked': 'stacked',
    'bar_percentage_stacked': 'percentage',
    'bar_horizontal_percentage_stacked': 'percentage',
    'area_stacked': 'stacked',
    'area_percentage_stacked': 'percentage',
}

PIE_SHAPES: dict[str, str] = {
    'pie': 'pie',
    'donut': 'pie',
    'treemap': 'treemap',
    'mosaic': 'mosaic',
    'waffle': 'waffle',
}

OPERATION_TYPE_MAP: dict[str, str] = {
    'count': 'count',
    'sum': 'sum',
    'avg': 'average',
    'average': 'average',
    'min': 'min',
    'max': 'max',
    'median': 'median',
    'unique_count': 'unique_count',
    'last_value': 'last_value',
    'percentile': 'percentile',
    'percentile_rank': 'percentile_rank',
}

SKIP_OPERATION_TYPES = frozenset({'differences', 'math', 'cumulative_sum', 'counter_rate', 'moving_average'})

CONTROL_TYPE_MAP: dict[str, str] = {
    'optionsListControl': 'options',
    'rangeSliderControl': 'range',
    'timeSliderControl': 'time',
    'timeSlider': 'time',
}

# ---------------------------------------------------------------------------
# Reverse mapping tables: Kibana JSON → YAML config values
# ---------------------------------------------------------------------------

KIBANA_FITTING_FUNCTION_TO_YAML: dict[str, str] = {
    'Linear': 'linear',
    'Carry': 'carry',
    'Lookahead': 'lookahead',
    'Average': 'average',
    'Nearest': 'nearest',
}

KIBANA_END_VALUE_TO_YAML: dict[str, str] = {
    'Zero': 'zero',
    'Nearest': 'nearest',
}

KIBANA_CURVE_TYPE_TO_YAML: dict[str, str] = {
    'CURVE_MONOTONE_X': 'monotone-x',
    'CURVE_STEP_AFTER': 'step-after',
}

KIBANA_LEGEND_SIZE_TO_YAML: dict[str, str] = {
    'small': 'small',
    'medium': 'medium',
    'large': 'large',
    'xlarge': 'extra_large',
}

KIBANA_AXIS_EXTENT_MODE_TO_YAML: dict[str, str] = {
    'dataBounds': 'data_bounds',
    'full': 'full',
    'custom': 'custom',
}

PARTITION_CHART_TYPES = frozenset({'pie', 'treemap', 'waffle', 'mosaic'})

KIBANA_DEFAULT_FILL_OPACITY = 0.3

KIBANA_GAUGE_SHAPE_TO_YAML: dict[str, str] = {
    'horizontalBullet': 'horizontal_bullet',
    'verticalBullet': 'vertical_bullet',
    'arc': 'arc',
    'circle': 'circle',
    'semiCircle': 'semi_circle',
}

# Default Kibana gauge shape — omit from YAML when present
KIBANA_GAUGE_DEFAULT_SHAPE = 'horizontalBullet'

KIBANA_PIE_NUMBER_DISPLAY_TO_YAML: dict[str, str] = {
    'percent': 'percent',
    'value': 'integer',
    'hidden': 'hide',
}

KIBANA_PARTITION_NUMBER_DISPLAY_TO_YAML: dict[str, str] = {
    'percent': 'percent',
    'value': 'value',
    'hidden': 'hide',
}

KIBANA_PIE_CATEGORY_DISPLAY_TO_YAML: dict[str, str] = {
    'default': 'auto',
    'inside': 'inside',
    'hide': 'hide',
}
