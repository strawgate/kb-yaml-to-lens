from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class XYReferenceLineValue(BaseCfgModel):
    """Defines the value for a reference line."""

    type: Literal['static'] = 'static'
    """The type of value (always 'static' for now)."""

    value: float
    """The static value for the reference line."""


class XYReferenceLine(BaseCfgModel):
    """Configuration for a single reference line in an XY chart."""

    id: str | None = None
    """Optional ID for the reference line."""

    label: str | None = None
    """Optional label for the reference line."""

    value: XYReferenceLineValue | float
    """The value for the reference line. Can be a float or XYReferenceLineValue object."""

    axis: Literal['left', 'right'] | None = 'left'
    """The axis to assign the reference line to."""

    color: str | None = None
    """The color of the reference line."""

    line_width: int | None = Field(default=None, ge=1, le=10)
    """The width of the reference line (1-10)."""

    line_style: Literal['solid', 'dashed', 'dotted'] | None = None
    """The style of the reference line."""

    fill: Literal['above', 'below', 'none'] | None = None
    """Fill area above or below the line."""

    icon: str | None = None
    """Icon to display on the reference line."""

    icon_position: Literal['auto', 'left', 'right', 'above', 'below'] | None = None
    """Position of the icon on the reference line."""


type XYChartTypes = LensXYChartTypes | ESQLXYChartTypes

type LensXYChartTypes = LensBarChart | LensLineChart | LensAreaChart
type ESQLXYChartTypes = ESQLBarChart | ESQLLineChart | ESQLAreaChart


class XYLegend(BaseCfgModel):
    """Represents legend formatting options for XY charts."""

    visible: bool | None = Field(default=None, description='Whether the legend is visible.')

    position: Literal['top', 'bottom', 'left', 'right'] | None = Field(
        default=None,
        description="Position of the legend. Kibana defaults to 'right' if not specified.",
    )


class AxisExtent(BaseCfgModel):
    """Represents axis extent (bounds) configuration for XY chart axes.

    Controls the range of values displayed on an axis. Can be set to:
    - 'full': Use the full extent of the data
    - 'custom': Specify custom bounds with min/max values
    - 'data_bounds': Fit to the actual data bounds
    """

    mode: Literal['full', 'custom', 'data_bounds'] = Field(default='full')
    """The extent mode for the axis. Defaults to 'full'."""

    min: float | None = Field(default=None)
    """Minimum value for the axis (only used when mode is 'custom')."""

    max: float | None = Field(default=None)
    """Maximum value for the axis (only used when mode is 'custom')."""

    enforce: bool | None = Field(default=None)
    """Whether to enforce the bounds strictly. Defaults to false."""

    nice_values: bool | None = Field(default=None)
    """Whether to use nice rounded values for bounds. Defaults to true."""

    @model_validator(mode='after')
    def validate_custom_bounds(self) -> Self:
        """Validate that custom mode has both min and max bounds specified.

        Kibana requires both bounds to be set when using custom mode.
        """
        if self.mode == 'custom' and (self.min is None or self.max is None):
            msg = "mode='custom' requires both 'min' and 'max' to be specified"
            raise ValueError(msg)
        return self


class AxisConfig(BaseCfgModel):
    """Represents configuration for a single axis in XY charts."""

    title: str | None = Field(default=None)
    """Custom title for the axis."""

    scale: Literal['linear', 'log', 'sqrt', 'time'] | None = Field(default=None)
    """Scale type for the axis. Defaults to 'linear'."""

    extent: AxisExtent | None = Field(default=None)
    """Extent/bounds configuration for the axis."""


class XYAppearance(BaseCfgModel):
    """Represents chart appearance formatting options for XY charts.

    Includes axis configuration for left Y-axis, right Y-axis, and X-axis,
    as well as per-series visual styling.
    """

    x_axis: AxisConfig | None = Field(default=None)
    """Configuration for the X-axis."""

    y_left_axis: AxisConfig | None = Field(default=None)
    """Configuration for the left Y-axis."""

    y_right_axis: AxisConfig | None = Field(default=None)
    """Configuration for the right Y-axis."""

    series: list['XYSeries'] | None = Field(default=None)
    """Per-series visual configuration (axis assignment, colors, line styles, etc.)."""


class BarChartAppearance(BaseCfgModel):
    """Represents bar chart appearance formatting options."""

    min_bar_height: float | None = Field(default=None, description='The minimum height for bars in bar charts.')


class LineChartAppearance(BaseCfgModel):
    """Represents line chart appearance formatting options."""

    fitting_function: Literal['Linear'] | None = Field(default=None, description='The fitting function to apply to line/area charts.')
    emphasize_fitting: bool | None = Field(default=None, description='If `true`, emphasize the fitting function line. Defaults to `false`.')
    curve_type: Literal['linear', 'cardinal', 'catmull-rom', 'natural', 'step', 'step-after', 'step-before', 'monotone-x'] | None = Field(
        default=None,
        description='The curve type for line/area charts.',
    )


class AreaChartAppearance(LineChartAppearance):
    """Represents area chart appearance formatting options."""

    fill_opacity: float | None = Field(default=None, description='The fill opacity for area charts (0.0 to 1.0).')


class XYTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for XY charts."""


class XYSeries(BaseCfgModel):
    """Represents per-series visual configuration for XY charts.

    Defines how a specific metric should be displayed, including axis assignment
    and color customization.
    """

    metric_id: str = Field(...)
    """The ID of the metric this series configuration applies to."""

    axis: Literal['left', 'right'] | None = Field(default=None)
    """Which Y-axis to assign this series to ('left' or 'right')."""

    color: str | None = Field(default=None)
    """Custom color for this series (hex color code, e.g., '#2196F3')."""


class BaseXYChart(BaseChart):
    """Base model for defining XY chart objects."""

    appearance: XYAppearance | None = Field(
        None,
        description='Formatting options for the chart appearance.',
    )

    titles_and_text: XYTitlesAndText | None = Field(
        None,
        description='Formatting options for the chart titles and text.',
    )

    legend: XYLegend | None = Field(
        None,
        description='Formatting options for the chart legend.',
    )

    color: ColorMapping | None = Field(
        None,
        description='Formatting options for the chart color palette.',
    )


class LensXYChartMixin(BaseCfgModel):
    """Shared fields for Lens-based XY charts."""

    data_view: str = Field(default=..., description='The data view to use for the chart.')
    dimensions: list[LensDimensionTypes] = Field(default_factory=list, description='Defines the dimensions for the chart.')
    metrics: list[LensMetricTypes] = Field(
        min_length=1,
        description='Defines the metrics for the chart. At least one metric is required.',
    )
    breakdown: LensDimensionTypes | None = Field(
        None,
        description=(
            'An optional dimension to split the series by. If provided, it will be used to break down the data into multiple series.'
        ),
    )

    def add_dimension(self, lens_dimension: LensDimensionTypes) -> Self:
        """Add a dimension to the lens Chart."""
        self.dimensions.append(lens_dimension)

        return self

    def add_metric(self, lens_metric: LensMetricTypes) -> Self:
        """Add a metric to the lens Chart."""
        self.metrics.append(lens_metric)

        return self


class ESQLXYChartMixin(BaseCfgModel):
    """Shared fields for ESQL-based XY charts."""

    dimensions: list[ESQLDimensionTypes] = Field(default_factory=list, description='Defines the dimensions for the chart.')

    metrics: list[ESQLMetricTypes] = Field(
        min_length=1,
        description='Defines the metrics for the chart. At least one metric is required.',
    )

    breakdown: ESQLDimensionTypes | None = Field(
        None,
        description=(
            'An optional dimension to split the series by. If provided, it will be used to break down the data into multiple series.'
        ),
    )

    def add_dimension(self, esql_dimension: ESQLDimensionTypes) -> Self:
        """Add a dimension to the ESQL Chart."""
        self.dimensions.append(esql_dimension)

        return self

    def add_metric(self, esql_metric: ESQLMetricTypes) -> Self:
        """Add a metric to the ESQL Chart."""
        self.metrics.append(esql_metric)

        return self


class BaseXYBarChart(BaseXYChart):
    """Represents a Bar chart configuration within a Lens panel."""

    type: Literal['bar'] = Field('bar', description="The type of XY chart to display. Defaults to 'bar'.")

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field(
        'stacked',
        description="The stacking mode for bar and area charts. Defaults to 'stacked'.",
    )


class BaseXYLineChart(BaseXYChart):
    """Represents a Line chart configuration within a Lens panel."""

    type: Literal['line'] = Field('line', description="The type of XY chart to display. Defaults to 'line'.")


class BaseXYAreaChart(BaseXYLineChart):
    """Represents an Area chart configuration within a Lens panel."""

    type: Literal['area'] = Field('area', description="The type of XY chart to display. Defaults to 'area'.")

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field(
        'stacked',
        description="The stacking mode for bar and area charts. Defaults to 'stacked'.",
    )


class LensBarChart(BaseXYBarChart, LensXYChartMixin):
    """Represents a Bar chart configuration within a Lens panel."""


class LensLineChart(BaseXYLineChart, LensXYChartMixin):
    """Represents a Line chart configuration within a Lens panel."""


class LensAreaChart(BaseXYAreaChart, LensXYChartMixin):
    """Represents an Area chart configuration within a Lens panel."""


class ESQLBarChart(BaseXYBarChart, ESQLXYChartMixin):
    """Represents a Bar chart configuration within a ESQL panel."""


class ESQLLineChart(BaseXYLineChart, ESQLXYChartMixin):
    """Represents a Line chart configuration within a ESQL panel."""


class ESQLAreaChart(BaseXYAreaChart, ESQLXYChartMixin):
    """Represents an Area chart configuration within a ESQL panel."""


class LensReferenceLineLayer(BaseChart):
    """Represents a reference line layer configuration for multi-layer panels.

    Reference lines display static threshold values, SLA targets, or baseline values
    on XY charts. They appear as horizontal or vertical lines with optional styling,
    labels, and icons.

    Unlike data layers, reference lines don't query data - they display static values
    for visual context and comparison.
    """

    type: Literal['reference_line'] = 'reference_line'
    """The type of layer. Always 'reference_line'."""

    data_view: str
    """The data view to use for the layer (required for Kibana compatibility)."""

    reference_lines: list[XYReferenceLine] = Field(default_factory=list)
    """List of reference lines to display in this layer."""
