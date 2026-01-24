"""Decompile Kibana Lens chart panels back to config models."""

from typing import Any

from dashboard_compiler.panels.charts.base.config import LegendVisibleEnum
from dashboard_compiler.panels.charts.config import (
    LensGaugePanelConfig,
    LensMetricPanelConfig,
    LensPanel,
    LensPiePanelConfig,
)
from dashboard_compiler.panels.charts.gauge.config import GaugeAppearance
from dashboard_compiler.panels.charts.lens.dimensions.decompile import decompile_lens_dimension
from dashboard_compiler.panels.charts.lens.metrics.decompile import decompile_lens_metric
from dashboard_compiler.panels.charts.pie.config import (
    PieChartAppearance,
    PieLegend,
    PieSliceLabelsEnum,
    PieSliceValuesEnum,
    PieTitlesAndText,
)
from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext


def get_layer_id(viz_state: dict[str, Any]) -> str | None:
    """Extract the primary layer ID from visualization state.

    Args:
        viz_state: The visualization state dict.

    Returns:
        The layer ID, or None if not found.

    """
    # Most visualizations have a 'layers' array or 'layerId' field
    if 'layerId' in viz_state:
        return viz_state['layerId']
    if 'layers' in viz_state and len(viz_state['layers']) > 0:
        first_layer = viz_state['layers'][0]
        if isinstance(first_layer, dict):
            return first_layer.get('layerId')
    return None


def get_data_view_from_references(
    references: list[dict[str, Any]],
    layer_id: str | None,
) -> str:
    """Extract data view ID from references for a given layer.

    Args:
        references: List of reference objects.
        layer_id: The layer ID to find the data view for.

    Returns:
        The data view ID string.

    """
    if layer_id is None:
        # Find any index-pattern reference
        for ref in references:
            if ref.get('type') == 'index-pattern':
                return ref.get('id', '')
        return ''

    # Look for reference matching the layer
    ref_name = f'indexpattern-datasource-layer-{layer_id}'
    for ref in references:
        if ref.get('name') == ref_name:
            return ref.get('id', '')

    # Fallback to first index-pattern
    for ref in references:
        if ref.get('type') == 'index-pattern':
            return ref.get('id', '')
    return ''


def get_layer_columns(
    kbn_panel: dict[str, Any],
    layer_id: str,
) -> dict[str, Any]:
    """Extract column definitions from a form-based layer.

    Args:
        kbn_panel: The Kibana panel dict.
        layer_id: The layer ID to extract columns from.

    Returns:
        Dictionary of column ID to column definition.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    state = attributes.get('state', {})
    datasource_states = state.get('datasourceStates', {})
    form_based = datasource_states.get('formBased', {})
    layers = form_based.get('layers', {})
    layer = layers.get(layer_id, {})
    return layer.get('columns', {})


def decompile_lens_metric_chart(
    kbn_panel: dict[str, Any],
    layer_id: str,  # noqa: ARG001
    columns: dict[str, Any],
    data_view: str,
    *,
    context: DecompileContext,
) -> LensMetricPanelConfig | None:
    """Decompile a Lens metric chart.

    Args:
        kbn_panel: The Kibana panel dict.
        layer_id: The layer ID.
        columns: The column definitions for the layer.
        data_view: The data view ID.
        context: Decompilation context for warnings.

    Returns:
        The decompiled LensMetricChart config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    state = attributes.get('state', {})
    viz_state = state.get('visualization', {})

    # Extract accessors
    primary_accessor = viz_state.get('metricAccessor')
    secondary_accessor = viz_state.get('secondaryMetricAccessor')
    breakdown_accessor = viz_state.get('breakdownByAccessor')

    if primary_accessor is None:
        context.warn('Metric chart missing primary metric accessor')
        return None

    # Decompile primary metric
    primary_column = columns.get(primary_accessor)
    if primary_column is None:
        context.warn(f'Primary metric column {primary_accessor} not found')
        return None

    primary_metric = decompile_lens_metric(primary_column, primary_accessor, context=context)
    if primary_metric is None:
        return None

    # Decompile secondary metric if present
    secondary_metric = None
    if secondary_accessor is not None:
        secondary_column = columns.get(secondary_accessor)
        if secondary_column is not None:
            secondary_metric = decompile_lens_metric(secondary_column, secondary_accessor, context=context)

    # Decompile breakdown dimension if present
    breakdown_dimension = None
    if breakdown_accessor is not None:
        breakdown_column = columns.get(breakdown_accessor)
        if breakdown_column is not None:
            breakdown_dimension = decompile_lens_dimension(breakdown_column, breakdown_accessor, context=context)

    return LensMetricPanelConfig(
        type='metric',
        data_view=data_view,
        primary=primary_metric,
        secondary=secondary_metric,
        breakdown=breakdown_dimension,
    )


def decompile_lens_gauge_chart(
    kbn_panel: dict[str, Any],
    layer_id: str,  # noqa: ARG001
    columns: dict[str, Any],
    data_view: str,
    *,
    context: DecompileContext,
) -> LensGaugePanelConfig | None:
    """Decompile a Lens gauge chart.

    Args:
        kbn_panel: The Kibana panel dict.
        layer_id: The layer ID.
        columns: The column definitions for the layer.
        data_view: The data view ID.
        context: Decompilation context for warnings.

    Returns:
        The decompiled LensGaugeChart config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    state = attributes.get('state', {})
    viz_state = state.get('visualization', {})

    # Extract accessors
    metric_accessor = viz_state.get('metricAccessor')
    min_accessor = viz_state.get('minAccessor')
    max_accessor = viz_state.get('maxAccessor')
    goal_accessor = viz_state.get('goalAccessor')

    if metric_accessor is None:
        context.warn('Gauge chart missing metric accessor')
        return None

    # Decompile metric
    metric_column = columns.get(metric_accessor)
    if metric_column is None:
        context.warn(f'Gauge metric column {metric_accessor} not found')
        return None

    metric = decompile_lens_metric(metric_column, metric_accessor, context=context)
    if metric is None:
        return None

    # Decompile min/max/goal if present
    minimum = None
    if min_accessor is not None:
        min_column = columns.get(min_accessor)
        if min_column is not None:
            minimum = decompile_lens_metric(min_column, min_accessor, context=context)

    maximum = None
    if max_accessor is not None:
        max_column = columns.get(max_accessor)
        if max_column is not None:
            maximum = decompile_lens_metric(max_column, max_accessor, context=context)

    goal = None
    if goal_accessor is not None:
        goal_column = columns.get(goal_accessor)
        if goal_column is not None:
            goal = decompile_lens_metric(goal_column, goal_accessor, context=context)

    # Extract appearance settings
    appearance = None
    shape = viz_state.get('shape')
    ticks_position = viz_state.get('ticksPosition')
    label_major = viz_state.get('labelMajor')
    label_minor = viz_state.get('labelMinor')
    color_mode = viz_state.get('colorMode')

    if shape is not None or ticks_position is not None or label_major is not None or label_minor is not None or color_mode is not None:
        appearance = GaugeAppearance(
            shape=shape,
            ticks_position=ticks_position,
            label_major=label_major,
            label_minor=label_minor,
            color_mode=color_mode,
        )

    return LensGaugePanelConfig(
        type='gauge',
        data_view=data_view,
        metric=metric,
        minimum=minimum,
        maximum=maximum,
        goal=goal,
        appearance=appearance,
    )


def decompile_lens_pie_chart(  # noqa: PLR0912, PLR0915
    kbn_panel: dict[str, Any],
    layer_id: str,  # noqa: ARG001
    columns: dict[str, Any],
    data_view: str,
    *,
    context: DecompileContext,
) -> LensPiePanelConfig | None:
    """Decompile a Lens pie chart.

    Args:
        kbn_panel: The Kibana panel dict.
        layer_id: The layer ID.
        columns: The column definitions for the layer.
        data_view: The data view ID.
        context: Decompilation context for warnings.

    Returns:
        The decompiled LensPieChart config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    state = attributes.get('state', {})
    viz_state = state.get('visualization', {})

    # Pie charts have layers array
    layers = viz_state.get('layers', [])
    if len(layers) == 0:
        context.warn('Pie chart has no layers')
        return None

    # Get first layer
    layer = layers[0]
    primary_groups = layer.get('primaryGroups', [])
    metric_accessors = layer.get('metrics', [])

    if len(metric_accessors) == 0:
        context.warn('Pie chart has no metrics')
        return None

    # Decompile metrics
    metrics = []
    for metric_accessor in metric_accessors:
        metric_column = columns.get(metric_accessor)
        if metric_column is not None:
            metric = decompile_lens_metric(metric_column, metric_accessor, context=context)
            if metric is not None:
                metrics.append(metric)

    # Decompile dimensions
    dimensions = []
    for dimension_accessor in primary_groups:
        dimension_column = columns.get(dimension_accessor)
        if dimension_column is not None:
            dimension = decompile_lens_dimension(dimension_column, dimension_accessor, context=context)
            if dimension is not None:
                dimensions.append(dimension)

    # Extract appearance settings
    appearance = None
    shape = viz_state.get('shape')
    if shape == 'donut':
        empty_size_ratio = layer.get('emptySizeRatio')
        if empty_size_ratio is not None:
            # Map ratio to size: small=0.3, medium=0.54, large=0.7
            # Thresholds are midpoints between sizes
            small_medium_threshold = 0.42
            medium_large_threshold = 0.62
            if empty_size_ratio <= small_medium_threshold:
                donut_size = 'small'
            elif empty_size_ratio <= medium_large_threshold:
                donut_size = 'medium'
            else:
                donut_size = 'large'
            appearance = PieChartAppearance(donut=donut_size)

    # Extract titles and text settings
    titles_and_text = None
    category_display = layer.get('categoryDisplay')
    number_display = layer.get('numberDisplay')
    percent_decimals = layer.get('percentDecimals')

    # Map Kibana values to config values
    slice_labels = None
    if category_display == 'default':
        slice_labels = PieSliceLabelsEnum.AUTO
    elif category_display == 'inside':
        slice_labels = PieSliceLabelsEnum.INSIDE
    elif category_display == 'hide':
        slice_labels = PieSliceLabelsEnum.HIDE

    slice_values = None
    if number_display == 'percent':
        slice_values = PieSliceValuesEnum.PERCENT
    elif number_display == 'value':
        slice_values = PieSliceValuesEnum.INTEGER
    elif number_display == 'hidden':
        slice_values = PieSliceValuesEnum.HIDE

    if slice_labels is not None or slice_values is not None or percent_decimals is not None:
        titles_and_text = PieTitlesAndText(
            slice_labels=slice_labels,
            slice_values=slice_values,
            value_decimal_places=percent_decimals,
        )

    # Extract legend settings
    legend = None
    legend_display = layer.get('legendDisplay')
    legend_size = layer.get('legendSize')
    legend_max_lines = layer.get('legendMaxLines')
    nested_legend = layer.get('nestedLegend')
    show_single_series = layer.get('showSingleSeries')

    # Map Kibana values to config values
    legend_visible = None
    if legend_display == 'default':
        legend_visible = LegendVisibleEnum.AUTO
    elif legend_display == 'show':
        legend_visible = LegendVisibleEnum.SHOW
    elif legend_display == 'hide':
        legend_visible = LegendVisibleEnum.HIDE

    if (
        legend_visible is not None
        or legend_size is not None
        or legend_max_lines is not None
        or nested_legend is not None
        or show_single_series is not None
    ):
        legend = PieLegend(
            visible=legend_visible,
            width=legend_size,
            truncate_labels=legend_max_lines,
            nested=nested_legend,
            show_single_series=show_single_series,
        )

    return LensPiePanelConfig(
        type='pie',
        data_view=data_view,
        metrics=metrics,
        dimensions=dimensions,
        appearance=appearance,
        titles_and_text=titles_and_text,
        legend=legend,
    )


def decompile_esql_chart(
    kbn_panel: dict[str, Any],
    viz_type: str,
    *,
    context: DecompileContext,
) -> PanelTypes | None:
    """Decompile an ES|QL-based chart panel.

    Args:
        kbn_panel: The Kibana panel dict.
        viz_type: The visualization type.
        context: Decompilation context for warnings.

    Returns:
        The decompiled ESQLPanel config, or None if unsupported.

    Note:
        This is a basic implementation that extracts chart type and query.
        Full metric/dimension extraction requires additional implementation.
        Currently returns None and warns about incomplete decompilation.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    title = attributes.get('title', '')

    # For now, warn that full ES|QL chart decompilation is not yet complete
    context.warn(
        f'ES|QL {viz_type} chart decompilation not yet fully implemented - requires manual metric/dimension configuration',
        panel_title=title,
    )
    return None


def decompile_lens_chart(
    kbn_panel: dict[str, Any],
    viz_type: str,
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,  # noqa: ARG001
) -> PanelTypes | None:
    """Decompile a form-based (data view) Lens chart panel.

    Args:
        kbn_panel: The Kibana panel dict.
        viz_type: The visualization type.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled LensPanel config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    title = attributes.get('title', '')
    state = attributes.get('state', {})
    viz_state = state.get('visualization', {})

    # Get layer ID
    layer_id = get_layer_id(viz_state)
    if layer_id is None:
        context.warn(f'Unable to extract layer ID from {viz_type} chart', panel_title=title)
        return None

    # Get data view from references
    references = attributes.get('references', [])
    data_view = get_data_view_from_references(references, layer_id)
    if data_view == '':
        context.warn(f'Unable to extract data view from {viz_type} chart', panel_title=title)
        return None

    # Get layer columns
    columns = get_layer_columns(kbn_panel, layer_id)
    if len(columns) == 0:
        context.warn(f'{viz_type} chart has no columns', panel_title=title)
        return None

    # Extract panel metadata
    grid_data = kbn_panel.get('gridData', {})
    size = Size(
        w=grid_data.get('w', 12),
        h=grid_data.get('h', 8),
    )
    position = Position(
        x=grid_data.get('x'),
        y=grid_data.get('y'),
    )
    panel_id = kbn_panel.get('panelIndex')
    description = attributes.get('description', '') or None
    hide_title = embeddable_config.get('hidePanelTitles')

    # Route to specific chart decompiler based on visualization type
    chart_config = None
    if viz_type == 'lnsMetric':
        chart_config = decompile_lens_metric_chart(kbn_panel, layer_id, columns, data_view, context=context)
    elif viz_type == 'lnsGauge':
        chart_config = decompile_lens_gauge_chart(kbn_panel, layer_id, columns, data_view, context=context)
    elif viz_type == 'lnsPie':
        chart_config = decompile_lens_pie_chart(kbn_panel, layer_id, columns, data_view, context=context)
    else:
        # Unsupported chart type
        context.warn(
            f'Lens {viz_type} chart decompilation not yet fully implemented - requires manual metric/dimension configuration',
            panel_title=title,
        )
        return None

    if chart_config is None:
        return None

    # Wrap chart config in LensPanel
    return LensPanel(
        id=panel_id,
        title=title,
        description=description,
        hide_title=hide_title if hide_title else None,
        size=size,
        position=position,
        lens=chart_config,
    )


def decompile_lens_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> PanelTypes | None:
    """Decompile a Kibana Lens panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled panel config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    viz_type = attributes.get('visualizationType', 'unknown')
    state = attributes.get('state', {})
    datasource = state.get('datasourceStates', {})

    # Determine if this is ES|QL or form-based
    text_based = datasource.get('textBased', {})
    text_layers = text_based.get('layers', {}) if text_based else {}

    if text_layers and len(text_layers) > 0:
        # ES|QL-based chart
        return decompile_esql_chart(kbn_panel, viz_type, context=context)
    # Form-based (data view) chart
    return decompile_lens_chart(
        kbn_panel,
        viz_type,
        context=context,
        reference_resolver=reference_resolver,
    )
