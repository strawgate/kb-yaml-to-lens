from typing import Annotated, Any, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnLayerColorMapping
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class LabelsOrientationConfig(BaseVwModel):
    """View model for XY chart axis label orientation configuration.

    Defines the rotation angle in degrees for axis labels on the X, left Y, and right Y axes.
    This model represents the compiled structure sent to Kibana for configuring label orientations
    in XY visualizations (bar, line, area charts).

    See Also:
        Kibana type definition: `LabelsOrientationConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        x: Rotation angle in degrees for X-axis labels.
        yLeft: Rotation angle in degrees for left Y-axis labels.
        yRight: Rotation angle in degrees for right Y-axis labels.
    """

    x: float | None = None
    yLeft: float | None = None
    yRight: float | None = None


class YAxisMode(BaseVwModel):
    """View model for Y-axis mode configuration in XY charts.

    Specifies the axis mode for a Y-axis series, such as which axis (left/right) to use
    for displaying the data series.

    See Also:
        Kibana type definition: `YAxisMode` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        name: The name of the axis mode (e.g., 'left', 'right').
    """

    # Define fields based on actual Kibana structure if needed, using object for now
    name: str  # Added name field based on usage in compile logic


class AxisConfig(BaseVwModel):
    """View model for axis configuration in XY charts.

    Provides configuration options for XY chart axes, such as extent and other axis properties.
    This is a placeholder model that can be extended with specific axis configuration fields
    as needed.

    See Also:
        Kibana type definition: `AxisConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    # Define fields based on actual Kibana structure if needed, using object for now


class YConfig(BaseVwModel):
    """View model for Y-axis series configuration in XY charts.

    Defines the appearance and behavior of individual Y-axis data series, including
    color, line style, width, icons, and axis assignment. Used to customize how each
    metric is displayed in the visualization.

    See Also:
        Kibana type definition: `YConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        forAccessor: The accessor ID this configuration applies to (references a metric field).
        color: Hex color code for the series (e.g., '#FF0000').
        icon: Icon identifier for the series marker.
        lineWidth: Width of the line in pixels for line/area charts.
        lineStyle: Style of the line (e.g., solid, dashed, dotted).
        fill: Fill configuration for area charts.
        iconPosition: Position of icons relative to data points.
        textVisibility: Whether to show text labels for this series.
        axisMode: Which Y-axis (left/right) to assign this series to.
    """

    forAccessor: str
    color: str | None = None
    icon: str | None = None
    lineWidth: float | None = None
    lineStyle: Any | None = None
    fill: Any | None = None
    iconPosition: Any | None = None
    textVisibility: bool | None = None
    axisMode: YAxisMode | None = None


class XYDataLayerConfig(BaseVwModel):
    """View model for XY chart data layer configuration.

    Represents a data layer in an XY visualization (bar, line, or area chart). Each layer
    displays one or more data series from a query, with configuration for appearance,
    axes, breakdowns, and aggregations.

    This is the primary layer type for displaying data in XY charts. Multiple data layers
    can be combined in a single visualization to show different metrics or series types.

    See Also:
        Kibana type definition: `XYDataLayerConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        layerId: Unique identifier for this layer.
        accessors: List of field accessor IDs for Y-axis metrics (the values to plot).
        layerType: Always 'data' for data layers.
        seriesType: Chart type for this layer ('bar', 'line', 'area', etc.).
        xAccessor: Field accessor ID for X-axis dimension (usually time or category).
        position: Position of the layer ('top' for overlays).
        showGridlines: Whether to show gridlines for this layer.
        simpleView: Simplified view mode flag.
        yConfig: Configuration for each Y-axis series (colors, line styles, etc.).
        splitAccessor: Field accessor ID for breaking down data into multiple series.
        palette: Color palette configuration for the layer.
        collapseFn: Aggregation function when collapsing multiple values ('sum', 'avg', etc.).
        xScaleType: Scale type for X-axis (linear, time, etc.).
        isHistogram: Whether this layer displays histogram data.
        columnToLabel: Mapping of column IDs to custom labels.
        colorMapping: Advanced color mapping configuration.
    """

    layerId: str
    accessors: list[str]
    layerType: Literal['data']
    seriesType: str
    xAccessor: str | None = None
    position: Literal['top'] | None = None
    showGridlines: bool
    simpleView: Annotated[bool | None, OmitIfNone()] = None
    yConfig: Annotated[list[YConfig] | None, OmitIfNone()] = None
    splitAccessor: Annotated[str | None, OmitIfNone()] = None
    palette: Annotated[Any | None, OmitIfNone()] = None
    collapseFn: Annotated[Literal['sum', 'avg', 'min', 'max'] | None, OmitIfNone()] = None
    xScaleType: Annotated[Any | None, OmitIfNone()] = None
    isHistogram: Annotated[bool | None, OmitIfNone()] = None
    columnToLabel: Annotated[str | None, OmitIfNone()] = None
    colorMapping: KbnLayerColorMapping | None = None


class XYReferenceLineLayerConfig(BaseVwModel):
    """View model for XY chart reference line layer configuration.

    Represents a reference line layer that displays horizontal or vertical lines at specific
    values in an XY chart. Reference lines are useful for showing thresholds, targets, or
    baseline values.

    Unlike data layers, reference lines are static values or calculations that provide
    visual context to the data being displayed.

    See Also:
        Kibana type definition: `XYReferenceLineLayerConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        layerId: Unique identifier for this reference line layer.
        accessors: List of field accessor IDs for the reference line values.
        yConfig: Configuration for each reference line (color, line style, label, etc.).
        layerType: Always 'referenceLine' for reference line layers.
    """

    layerId: str
    accessors: list[str]
    yConfig: list[YConfig] | None = None
    layerType: Literal['referenceLine']


class XYAnnotationLayerConfigCachedMetadata(BaseVwModel):
    """View model for cached metadata of annotation layers.

    Stores metadata about annotation groups or saved annotations, including title,
    description, and tags. This metadata is cached with the annotation layer configuration
    for display and management purposes.

    See Also:
        Related to annotation layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        title: Display title for the annotation or annotation group.
        description: Detailed description of the annotation's purpose.
        tags: List of tags for categorizing and filtering annotations.
    """

    title: str
    description: str
    tags: list[str]


class XYByValueAnnotationLayerConfig(BaseVwModel):
    """View model for XY chart annotation layer with inline annotations.

    Represents an annotation layer where annotations are defined inline (by value) within
    the visualization configuration. Annotations mark specific events, time ranges, or
    values on the chart with visual markers and labels.

    This layer type is used when annotations are created directly in the dashboard rather
    than referencing a saved annotation group.

    See Also:
        Kibana type definition: `XYByValueAnnotationLayerConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        layerId: Unique identifier for this annotation layer.
        layerType: Always 'annotations' for annotation layers.
        annotations: List of annotation configurations (event markers, ranges, etc.).
        indexPatternId: ID of the index pattern used for querying annotation data.
        ignoreGlobalFilters: Whether to ignore dashboard-level filters for this layer.
        cachedMetadata: Cached metadata about the annotations (title, description, tags).
    """

    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None


class XYByReferenceAnnotationLayerConfig(BaseVwModel):
    """View model for XY chart annotation layer referencing a saved annotation group.

    Represents an annotation layer that references a saved annotation group (by reference)
    rather than defining annotations inline. This allows annotations to be reused across
    multiple dashboards and managed centrally.

    The referenced annotation group is identified by `annotationGroupId` and can be
    updated independently of the dashboard.

    See Also:
        Kibana type definition: Related to annotation layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        layerId: Unique identifier for this annotation layer.
        layerType: Always 'annotations' for annotation layers.
        annotations: List of annotation configurations from the referenced group.
        indexPatternId: ID of the index pattern used for querying annotation data.
        ignoreGlobalFilters: Whether to ignore dashboard-level filters for this layer.
        cachedMetadata: Cached metadata from the annotation group (title, description, tags).
        annotationGroupId: ID of the saved annotation group being referenced.
        last_saved: Timestamp of when the annotation group was last saved.
    """

    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    annotationGroupId: str
    last_saved: Any = Field(alias='__lastSaved')  # type: ignore[reportAny]


# Subclass Kbn for XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnBaseStateVisualization):
    """View model for XY chart visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for XY charts (bar, line, area)
    as stored in the Kibana saved object JSON structure. It includes all layers (data,
    reference lines, annotations), appearance settings, axis configuration, and legend
    preferences.

    The visualization state is part of the larger Lens panel configuration and defines
    how the chart should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `XYState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts

    Attributes:
        preferredSeriesType: Default series type for new layers ('bar', 'line', 'area', etc.).
        legend: Legend configuration (position, visibility, size, etc.).
        valueLabels: How to display value labels ('hide', 'show', or specific positioning).
        fittingFunction: Interpolation function for missing values in line/area charts.
        emphasizeFitting: Whether to emphasize the fitting function line.
        endValue: How to handle the end value in line/area charts.
        xExtent: X-axis extent/range configuration.
        yLeftExtent: Left Y-axis extent/range configuration.
        yRightExtent: Right Y-axis extent/range configuration.
        layers: List of all layers (data, reference lines, annotations).
        xTitle: Custom title for the X-axis.
        yTitle: Custom title for the left Y-axis (deprecated, use yLeftTitle).
        yRightTitle: Custom title for the right Y-axis.
        yLeftScale: Scale type for the left Y-axis (linear, log, sqrt, etc.).
        yRightScale: Scale type for the right Y-axis.
        axisTitlesVisibilitySettings: Control visibility of axis titles.
        tickLabelsVisibilitySettings: Control visibility of tick labels.
        gridlinesVisibilitySettings: Control visibility of gridlines.
        labelsOrientation: Rotation angles for axis labels.
        curveType: Curve interpolation type for line/area charts.
        fillOpacity: Opacity of the fill for area charts (0.0 to 1.0).
        minBarHeight: Minimum height in pixels for bars.
        hideEndzones: Whether to hide endzones in time series charts.
        showCurrentTimeMarker: Whether to show a marker for the current time.
    """

    preferredSeriesType: str | None = None
    legend: Any
    valueLabels: Literal['hide', 'show'] | None = None
    fittingFunction: Annotated[Any | None, OmitIfNone()] = None
    emphasizeFitting: Annotated[bool | None, OmitIfNone()] = None
    endValue: Annotated[Any | None, OmitIfNone()] = None
    xExtent: Annotated[Any | None, OmitIfNone()] = None
    yLeftExtent: Annotated[Any | None, OmitIfNone()] = None
    yRightExtent: Annotated[Any | None, OmitIfNone()] = None
    layers: list[XYDataLayerConfig | XYReferenceLineLayerConfig | XYByValueAnnotationLayerConfig | XYByReferenceAnnotationLayerConfig] = (
        Field(default_factory=list)
    )
    xTitle: Annotated[str | None, OmitIfNone()] = None
    yTitle: Annotated[str | None, OmitIfNone()] = None
    yRightTitle: Annotated[str | None, OmitIfNone()] = None
    yLeftScale: Annotated[Any | None, OmitIfNone()] = None
    yRightScale: Annotated[Any | None, OmitIfNone()] = None
    axisTitlesVisibilitySettings: Annotated[Any | None, OmitIfNone()] = None
    tickLabelsVisibilitySettings: Annotated[Any | None, OmitIfNone()] = None
    gridlinesVisibilitySettings: Annotated[Any | None, OmitIfNone()] = None
    labelsOrientation: Annotated[LabelsOrientationConfig | None, OmitIfNone()] = None
    curveType: Annotated[Any | None, OmitIfNone()] = None
    fillOpacity: Annotated[float | None, OmitIfNone()] = None
    minBarHeight: Annotated[float | None, OmitIfNone()] = None
    hideEndzones: Annotated[bool | None, OmitIfNone()] = None
    showCurrentTimeMarker: Annotated[bool | None, OmitIfNone()] = None


# Note: ValidLayer is not di
