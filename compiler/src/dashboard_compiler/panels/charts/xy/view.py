from typing import Annotated, Any, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.view import KbnBaseStateVisualization, KbnLayerColorMapping
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class LabelsOrientationConfig(BaseVwModel):
    """View model for XY chart axis label orientation configuration.

    Defines the rotation angle in degrees for axis labels on the X, left Y, and right Y axes.
    This model represents the compiled structure sent to Kibana for configuring label orientations
    in XY visualizations (bar, line, area charts).

    See Also:
        Kibana type definition: `LabelsOrientationConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    x: float | None = None
    """Rotation angle in degrees for X-axis labels."""

    yLeft: float | None = None
    """Rotation angle in degrees for left Y-axis labels."""

    yRight: float | None = None
    """Rotation angle in degrees for right Y-axis labels."""


class AxisTitlesVisibilitySettings(BaseVwModel):
    """View model for axis title visibility settings in XY charts.

    Controls whether axis titles are visible for the X-axis, left Y-axis, and right Y-axis.
    This must be set for axis titles to render in Kibana.

    See Also:
        Kibana type definition: `AxisTitlesVisibilitySettings` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    x: bool | None = None
    """Whether to show the X-axis title."""

    yLeft: bool | None = None
    """Whether to show the left Y-axis title."""

    yRight: bool | None = None
    """Whether to show the right Y-axis title."""


YAxisMode = Literal['left', 'right']


class AxisExtentConfig(BaseVwModel):
    """View model for axis extent (bounds) configuration in XY charts.

    Defines the range/bounds of values displayed on an axis. Supports different modes:
    - 'full': Use the full extent of the data range
    - 'custom': Specify custom numeric bounds
    - 'dataBounds': Fit to actual data bounds

    See Also:
        Kibana type definition: `AxisExtentConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/plugins/shared/chart_expressions/expression_xy/common/types/expression_functions.ts
    """

    mode: Literal['full', 'custom', 'dataBounds']
    """The extent mode for the axis."""

    lowerBound: Annotated[float | None, OmitIfNone()] = None
    """Minimum value for the axis (only used when mode is 'custom')."""

    upperBound: Annotated[float | None, OmitIfNone()] = None
    """Maximum value for the axis (only used when mode is 'custom')."""

    enforce: Annotated[bool | None, OmitIfNone()] = None
    """Whether to enforce the bounds strictly."""

    niceValues: Annotated[bool | None, OmitIfNone()] = None
    """Whether to use nice rounded values for bounds."""


class YConfig(BaseVwModel):
    """View model for Y-axis series configuration in XY charts.

    Defines the appearance and behavior of individual Y-axis data series and reference lines.
    For data series, only color and axisMode are used (other fields are for reference lines).

    See Also:
        Kibana type definition: `YConfig` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    forAccessor: str
    """The accessor ID this configuration applies to (references a metric field)."""

    color: Annotated[str | None, OmitIfNone()] = None
    """Hex color code for the series (e.g., '#FF0000')."""

    axisMode: Annotated[Literal['left', 'right'] | None, OmitIfNone()] = None
    """Which Y-axis (left/right) to assign this series to."""

    lineWidth: Annotated[float | None, OmitIfNone()] = None
    """Width of the line in pixels (used by reference lines only)."""

    lineStyle: Annotated[Literal['solid', 'dashed', 'dotted'] | None, OmitIfNone()] = None
    """Style of the line (used by reference lines only)."""

    fill: Annotated[Literal['none', 'below', 'above'] | None, OmitIfNone()] = None
    """Fill configuration (used by reference lines only)."""

    icon: Annotated[str | None, OmitIfNone()] = None
    """Icon identifier (used by reference lines only)."""

    iconPosition: Annotated[Literal['auto', 'left', 'right', 'above', 'below'] | None, OmitIfNone()] = None
    """Position of icons (used by reference lines only)."""


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
    """

    layerId: str
    """Unique identifier for this layer."""

    accessors: list[str]
    """List of field accessor IDs for Y-axis metrics (the values to plot)."""

    layerType: Literal['data']
    """Always 'data' for data layers."""

    seriesType: str
    """Chart type for this layer ('bar', 'line', 'area', etc.)."""

    xAccessor: str | None = None
    """Field accessor ID for X-axis dimension (usually time or category)."""

    position: Literal['top'] | None = None
    """Position of the layer ('top' for overlays)."""

    showGridlines: bool
    """Whether to show gridlines for this layer."""

    simpleView: Annotated[bool | None, OmitIfNone()] = None
    """Simplified view mode flag."""

    yConfig: Annotated[list[YConfig] | None, OmitIfNone()] = None
    """Configuration for each Y-axis series (colors, line styles, etc.)."""

    splitAccessor: Annotated[str | None, OmitIfNone()] = None
    """Field accessor ID for breaking down data into multiple series."""

    palette: Annotated[Any | None, OmitIfNone()] = None
    """Color palette configuration for the layer."""

    collapseFn: Annotated[Literal['sum', 'avg', 'min', 'max'] | None, OmitIfNone()] = None
    """Aggregation function when collapsing multiple values ('sum', 'avg', etc.)."""

    xScaleType: Annotated[Any | None, OmitIfNone()] = None
    """Scale type for X-axis (linear, time, etc.)."""

    isHistogram: Annotated[bool | None, OmitIfNone()] = None
    """Whether this layer displays histogram data."""

    columnToLabel: Annotated[str | None, OmitIfNone()] = None
    """Mapping of column IDs to custom labels."""

    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None
    """Advanced color mapping configuration."""


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
    """

    layerId: str
    """Unique identifier for this reference line layer."""

    accessors: list[str]
    """List of field accessor IDs for the reference line values."""

    yConfig: list[YConfig] | None = None
    """Configuration for each reference line (color, line style, label, etc.)."""

    layerType: Literal['referenceLine']
    """Always 'referenceLine' for reference line layers."""


class XYAnnotationLayerConfigCachedMetadata(BaseVwModel):
    """View model for cached metadata of annotation layers.

    Stores metadata about annotation groups or saved annotations, including title,
    description, and tags. This metadata is cached with the annotation layer configuration
    for display and management purposes.

    See Also:
        Related to annotation layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    title: str
    """Display title for the annotation or annotation group."""

    description: str
    """Detailed description of the annotation's purpose."""

    tags: list[str]
    """List of tags for categorizing and filtering annotations."""


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
    """

    layerId: str
    """Unique identifier for this annotation layer."""

    layerType: Literal['annotations']
    """Always 'annotations' for annotation layers."""

    annotations: list[Any]
    """List of annotation configurations (event markers, ranges, etc.)."""

    indexPatternId: str
    """ID of the index pattern used for querying annotation data."""

    ignoreGlobalFilters: bool
    """Whether to ignore dashboard-level filters for this layer."""

    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    """Cached metadata about the annotations (title, description, tags)."""


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
    """

    layerId: str
    """Unique identifier for this annotation layer."""

    layerType: Literal['annotations']
    """Always 'annotations' for annotation layers."""

    annotations: list[Any]
    """List of annotation configurations from the referenced group."""

    indexPatternId: str
    """ID of the index pattern used for querying annotation data."""

    ignoreGlobalFilters: bool
    """Whether to ignore dashboard-level filters for this layer."""

    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    """Cached metadata from the annotation group (title, description, tags)."""

    annotationGroupId: str
    """ID of the saved annotation group being referenced."""

    last_saved: Any = Field(alias='__lastSaved')  # pyright: ignore[reportAny]
    """Timestamp of when the annotation group was last saved."""


class XYLegendConfig(BaseVwModel):
    """View model for XY legend configuration.

    Defines how the legend should be displayed in XY charts, including visibility,
    position, size, and label truncation settings.

    See Also:
        Kibana type definition: Related to legend types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/xy/types.ts
    """

    isVisible: bool
    """Whether the legend is visible."""

    position: str
    """Position of the legend ('top', 'bottom', 'left', 'right')."""

    showSingleSeries: Annotated[bool | None, OmitIfNone()] = None
    """Whether to show legend when there is only one series."""

    legendSize: Annotated[str | None, OmitIfNone()] = None
    """Size of the legend ('auto', 'small', 'medium', 'large', 'extra_large')."""

    shouldTruncate: Annotated[bool | None, OmitIfNone()] = None
    """Whether to truncate long legend labels."""

    maxLines: Annotated[int | None, OmitIfNone()] = None
    """Maximum number of lines for legend labels."""


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
    """

    preferredSeriesType: str | None = None
    """Default series type for new layers ('bar', 'line', 'area', etc.)."""

    legend: XYLegendConfig
    """Legend configuration (position, visibility, size, etc.)."""

    valueLabels: Literal['hide', 'show'] | None = None
    """How to display value labels ('hide', 'show', or specific positioning)."""

    fittingFunction: Annotated[Any | None, OmitIfNone()] = None
    """Interpolation function for missing values in line/area charts."""

    emphasizeFitting: Annotated[bool | None, OmitIfNone()] = None
    """Whether to emphasize the fitting function line."""

    endValue: Annotated[Any | None, OmitIfNone()] = None
    """How to handle the end value in line/area charts."""

    xExtent: Annotated[Any | None, OmitIfNone()] = None
    """X-axis extent/range configuration."""

    yLeftExtent: Annotated[Any | None, OmitIfNone()] = None
    """Left Y-axis extent/range configuration."""

    yRightExtent: Annotated[Any | None, OmitIfNone()] = None
    """Right Y-axis extent/range configuration."""

    layers: list[XYDataLayerConfig | XYReferenceLineLayerConfig | XYByValueAnnotationLayerConfig | XYByReferenceAnnotationLayerConfig] = (
        Field(default_factory=list)
    )
    """List of all layers (data, reference lines, annotations)."""

    xTitle: Annotated[str | None, OmitIfNone()] = None
    """Custom title for the X-axis."""

    yTitle: Annotated[str | None, OmitIfNone()] = None
    """Custom title for the left Y-axis (deprecated, use yLeftTitle)."""

    yLeftTitle: Annotated[str | None, OmitIfNone()] = None
    """Custom title for the left Y-axis."""

    yRightTitle: Annotated[str | None, OmitIfNone()] = None
    """Custom title for the right Y-axis."""

    yLeftScale: Annotated[Literal['linear', 'log', 'sqrt', 'time'] | None, OmitIfNone()] = None
    """Scale type for the left Y-axis (linear, log, sqrt, time)."""

    yRightScale: Annotated[Literal['linear', 'log', 'sqrt', 'time'] | None, OmitIfNone()] = None
    """Scale type for the right Y-axis (linear, log, sqrt, time)."""

    axisTitlesVisibilitySettings: Annotated[AxisTitlesVisibilitySettings | None, OmitIfNone()] = None
    """Control visibility of axis titles."""

    tickLabelsVisibilitySettings: Annotated[Any | None, OmitIfNone()] = None
    """Control visibility of tick labels."""

    gridlinesVisibilitySettings: Annotated[Any | None, OmitIfNone()] = None
    """Control visibility of gridlines."""

    labelsOrientation: Annotated[LabelsOrientationConfig | None, OmitIfNone()] = None
    """Rotation angles for axis labels."""

    curveType: Annotated[Any | None, OmitIfNone()] = None
    """Curve interpolation type for line/area charts."""

    fillOpacity: Annotated[float | None, OmitIfNone()] = None
    """Opacity of the fill for area charts (0.0 to 1.0)."""

    minBarHeight: Annotated[float | None, OmitIfNone()] = None
    """Minimum height in pixels for bars."""

    hideEndzones: Annotated[bool | None, OmitIfNone()] = None
    """Whether to hide endzones in time series charts."""

    showCurrentTimeMarker: Annotated[bool | None, OmitIfNone()] = None
    """Whether to show a marker for the current time."""
