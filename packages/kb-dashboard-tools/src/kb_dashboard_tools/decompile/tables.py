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
}

SKIP_OPERATION_TYPES = frozenset({'formula', 'differences', 'math', 'cumulative_sum', 'counter_rate', 'moving_average'})

CONTROL_TYPE_MAP: dict[str, str] = {
    'optionsListControl': 'options',
    'rangeSliderControl': 'range',
    'timeSliderControl': 'time',
}
