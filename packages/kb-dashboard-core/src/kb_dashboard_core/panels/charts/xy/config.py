from typing import Literal, Self

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, ColorMapping, LegendVisibleEnum, LegendWidthEnum
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes
from kb_dashboard_core.panels.charts.lens.dimensions import LensDimensionTypes
from kb_dashboard_core.panels.charts.xy.metrics import ESQLXYMetricTypes, LensXYMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel, BaseIdentifiableModel


class XYReferenceLineValue(BaseCfgModel):
    """Defines the value for a reference line."""

    type: Literal['static'] = 'static'
    """The type of value (always 'static' for now)."""

    value: float
    """The static value for the reference line."""


class XYReferenceLine(BaseIdentifiableModel):
    """Configuration for a single reference line in an XY chart.

    Inherits from BaseIdentifiableModel for automatic deterministic ID generation.
    """

    label: str | None = Field(default=None)
    """Optional label for the reference line."""

    value: XYReferenceLineValue | float
    """The value for the reference line. Can be a float or XYReferenceLineValue object."""

    axis: Literal['left', 'right'] | None = 'left'
    """The axis to assign the reference line to."""

    color: str | None = Field(default=None)
    """The color of the reference line."""

    line_width: int | None = Field(default=None, ge=1, le=10)
    """The width of the reference line (1-10)."""

    line_style: Literal['solid', 'dashed', 'dotted'] | None = Field(default=None)
    """The style of the reference line."""

    fill: Literal['above', 'below', 'none'] | None = Field(default=None)
    """Fill area above or below the line."""

    icon: str | None = Field(default=None)
    """Icon to display on the reference line."""

    icon_position: Literal['auto', 'left', 'right', 'above', 'below'] | None = Field(default=None)
    """Position of the icon on the reference line."""


type XYChartTypes = LensXYChartTypes | ESQLXYChartTypes

type LensXYChartTypes = LensBarChart | LensLineChart | LensAreaChart
type ESQLXYChartTypes = ESQLBarChart | ESQLLineChart | ESQLAreaChart


class XYLegend(BaseCfgModel):
    """Represents legend formatting options for XY charts."""

    visible: LegendVisibleEnum | None = Field(
        default=None,
        strict=False,  # Turn off strict for enums
        description='Visibility of the legend (show, hide, or auto). Kibana defaults to show if not specified.',
    )

    position: Literal['top', 'bottom', 'left', 'right'] | None = Field(
        default=None,
        description="Position of the legend. Kibana defaults to 'right' if not specified.",
    )

    show_single_series: bool | None = Field(
        default=None,
        description='Whether to show legend when there is only one series. Kibana defaults to false if not specified.',
    )

    size: LegendWidthEnum | None = Field(
        default=None,
        strict=False,  # Turn off strict for enums
        description='Size of the legend (small, medium, large, extra_large). If not specified, Kibana uses automatic sizing.',
    )

    truncate_labels: int | None = Field(
        default=None,
        ge=0,
        le=5,
        description='Number of lines to truncate legend labels to. Set to 0 to disable truncation. Kibana defaults to 1 if not specified.',
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


class BaseXYChartAppearance(BaseCfgModel):
    """Base class for XY chart appearance formatting options.

    Includes axis configuration for left Y-axis, right Y-axis, and X-axis.
    Not intended to be used directly by users.
    """

    x_axis: AxisConfig | None = Field(default=None)
    """Configuration for the X-axis."""

    y_left_axis: AxisConfig | None = Field(default=None)
    """Configuration for the left Y-axis."""

    y_right_axis: AxisConfig | None = Field(default=None)
    """Configuration for the right Y-axis."""


class BarChartAppearance(BaseXYChartAppearance):
    """Represents bar chart appearance formatting options.

    Extends BaseXYChartAppearance to include bar-specific options.
    """

    min_bar_height: float | None = Field(default=None, description='The minimum height for bars in bar charts.')


class LineChartAppearance(BaseXYChartAppearance):
    """Represents line chart appearance formatting options.

    Extends BaseXYChartAppearance to include line-specific options.
    """

    missing_values: Literal['None', 'Linear', 'Carry', 'Lookahead', 'Average', 'Nearest'] | None = Field(
        default=None,
        description='How to handle missing data points. Controls interpolation for gaps in your data.',
    )
    show_as_dotted: bool | None = Field(
        default=None,
        description='If `true`, visually distinguish interpolated data from real data points. Defaults to `false`.',
    )
    end_values: Literal['None', 'Zero', 'Nearest'] | None = Field(
        default=None,
        description='How to handle the end of the time range in line/area charts.',
    )
    line_style: Literal['linear', 'monotone-x', 'step-after'] | None = Field(
        default=None,
        description=(
            'The line style for line/area charts. '
            'Only 3 types are supported by Kibana: linear (straight), monotone-x (smooth), step-after (stepped).'
        ),
    )


class AreaChartAppearance(LineChartAppearance):
    """Represents area chart appearance formatting options."""

    fill_opacity: float | None = Field(default=None, ge=0.0, le=1.0, description='The fill opacity for area charts (0.0 to 1.0).')


class XYTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for XY charts."""


class BaseXYChart(BaseChart):
    """Base model for defining XY chart objects."""

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
    dimension: LensDimensionTypes | None = Field(
        default=None,
        description='Defines the X-axis dimension for the chart. XY charts support 0 or 1 dimension.',
    )
    metrics: list[LensXYMetricTypes] = Field(
        min_length=1,
        description='Defines the metrics for the chart. At least one metric is required.',
    )
    breakdown: LensDimensionTypes | None = Field(
        None,
        description=(
            'An optional dimension to split the series by. If provided, it will be used to break down the data into multiple series.'
        ),
    )

    def set_dimension(self, lens_dimension: LensDimensionTypes) -> Self:
        """Set the X-axis dimension for the lens Chart."""
        self.dimension = lens_dimension

        return self

    def add_metric(self, lens_metric: LensXYMetricTypes) -> Self:
        """Add a metric to the lens Chart."""
        self.metrics.append(lens_metric)

        return self


class ESQLXYChartMixin(BaseCfgModel):
    """Shared fields for ESQL-based XY charts."""

    dimension: ESQLDimensionTypes | None = Field(
        default=None,
        description='Defines the X-axis dimension for the chart. XY charts support 0 or 1 dimension.',
    )

    metrics: list[ESQLXYMetricTypes] = Field(
        min_length=1,
        description='Defines the metrics for the chart. At least one metric is required.',
    )

    breakdown: ESQLDimensionTypes | None = Field(
        None,
        description=(
            'An optional dimension to split the series by. If provided, it will be used to break down the data into multiple series.'
        ),
    )

    def set_dimension(self, esql_dimension: ESQLDimensionTypes) -> Self:
        """Set the X-axis dimension for the ESQL Chart."""
        self.dimension = esql_dimension

        return self

    def add_metric(self, esql_metric: ESQLXYMetricTypes) -> Self:
        """Add a metric to the ESQL Chart."""
        self.metrics.append(esql_metric)

        return self


class BaseXYBarChart(BaseXYChart):
    """Represents a Bar chart configuration within a Lens panel."""

    type: Literal['bar'] = Field('bar', description="The type of XY chart to display. Defaults to 'bar'.")

    appearance: BarChartAppearance | None = Field(
        None,
        description='Formatting options for the chart appearance.',
    )

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field(
        'stacked',
        description="The stacking mode for bar and area charts. Defaults to 'stacked'.",
    )


class BaseXYLineChart(BaseXYChart):
    """Represents a Line chart configuration within a Lens panel."""

    type: Literal['line'] = Field('line', description="The type of XY chart to display. Defaults to 'line'.")

    appearance: LineChartAppearance | None = Field(
        None,
        description='Formatting options for the chart appearance.',
    )

    show_current_time_marker: bool | None = Field(
        default=None,
        description='Whether to show a vertical line at the current time in time series charts.',
    )

    hide_endzones: bool | None = Field(
        default=None,
        description='Whether to hide end zones in time series charts (areas where data is incomplete).',
    )


class BaseXYAreaChart(BaseXYLineChart):
    """Represents an Area chart configuration within a Lens panel."""

    type: Literal['area'] = Field('area', description="The type of XY chart to display. Defaults to 'area'.")

    appearance: AreaChartAppearance | None = Field(
        None,
        description='Formatting options for the chart appearance. AreaChartAppearance includes all line chart options plus fill_opacity.',
    )

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field(
        'stacked',
        description="The stacking mode for bar and area charts. Defaults to 'stacked'.",
    )


class LensBarChart(BaseXYBarChart, LensXYChartMixin):
    """Represents a Bar chart configuration within a Lens panel.

    Examples:
        Simple bar chart with time series:
        ```yaml
        lens:
          type: bar
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: count
        ```

        Stacked bar chart with breakdown:
        ```yaml
        lens:
          type: bar
          mode: stacked
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          breakdown:
            type: values
            field: "service.name"
          metrics:
            - aggregation: count
        ```
    """


class LensLineChart(BaseXYLineChart, LensXYChartMixin):
    """Represents a Line chart configuration within a Lens panel.

    Examples:
        Simple line chart with time series:
        ```yaml
        lens:
          type: line
          data_view: "metrics-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: average
              field: response_time
        ```

        Line chart with dual Y-axes:
        ```yaml
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: count
              id: "request_count"
              axis: left
            - aggregation: average
              field: "error.rate"
              id: "error_rate"
              axis: right
        ```
    """


class LensAreaChart(BaseXYAreaChart, LensXYChartMixin):
    """Represents an Area chart configuration within a Lens panel.

    Examples:
        Simple area chart with time series:
        ```yaml
        lens:
          type: area
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: count
        ```

        Stacked area chart with percentage mode:
        ```yaml
        lens:
          type: area
          mode: percentage
          data_view: "metrics-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          breakdown:
            type: values
            field: "service.name"
          metrics:
            - aggregation: count
        ```
    """


class ESQLBarChart(BaseXYBarChart, ESQLXYChartMixin):
    """Represents a Bar chart configuration within an ES|QL panel.

    Bar charts display categorical or time-series data using vertical or horizontal bars,
    where bar height/length represents metric values. Ideal for comparing values across
    categories or showing distributions over time.

    The `field` names used in dimension, metrics, and breakdown must correspond to
    columns returned by your ES|QL query.

    Examples:
        ES|QL bar chart with time series:
        ```yaml
        esql:
          type: bar
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend)
          dimension:
            field: "@timestamp"
          metrics:
            - field: "count"
        ```

        Stacked bar chart with breakdown:
        ```yaml
        esql:
          type: bar
          mode: stacked
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend), service.name
          dimension:
            field: "@timestamp"
          breakdown:
            field: "service.name"
          metrics:
            - field: "count"
        ```
    """


class ESQLLineChart(BaseXYLineChart, ESQLXYChartMixin):
    """Represents a Line chart configuration within an ES|QL panel.

    Line charts display data points connected by lines, ideal for visualizing trends
    and changes over time. Supports multiple metrics and optional breakdown for
    comparing series.

    The `field` names used in dimension, metrics, and breakdown must correspond to
    columns returned by your ES|QL query.

    Examples:
        ES|QL line chart for time series:
        ```yaml
        esql:
          type: line
          query: |
            FROM metrics-*
            | STATS avg_cpu = AVG(system.cpu.total.pct) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend)
          dimension:
            field: "@timestamp"
          metrics:
            - field: "avg_cpu"
        ```

        Line chart with breakdown by host:
        ```yaml
        esql:
          type: line
          query: |
            FROM metrics-*
            | STATS avg_cpu = AVG(system.cpu.total.pct) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend), host.name
          dimension:
            field: "@timestamp"
          breakdown:
            field: "host.name"
          metrics:
            - field: "avg_cpu"
        ```
    """


class ESQLAreaChart(BaseXYAreaChart, ESQLXYChartMixin):
    """Represents an Area chart configuration within an ES|QL panel.

    Area charts display data with filled areas beneath the lines, useful for
    visualizing cumulative values or showing the magnitude of trends over time.
    Supports stacked and percentage modes for comparing proportions.

    The `field` names used in dimension, metrics, and breakdown must correspond to
    columns returned by your ES|QL query.

    Examples:
        ES|QL area chart for resource usage:
        ```yaml
        esql:
          type: area
          query: |
            FROM metrics-*
            | STATS avg_mem = AVG(system.memory.used.pct) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend)
          dimension:
            field: "@timestamp"
          metrics:
            - field: "avg_mem"
        ```

        Stacked area chart with percentage mode:
        ```yaml
        esql:
          type: area
          mode: percentage
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY @timestamp = BUCKET(@timestamp, 20, ?_tstart, ?_tend), service.name
          dimension:
            field: "@timestamp"
          breakdown:
            field: "service.name"
          metrics:
            - field: "count"
        ```
    """


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

    data_view: str = Field(default=...)
    """The data view to use for the layer (required for Kibana compatibility)."""

    reference_lines: list[XYReferenceLine] = Field(default_factory=list)
    """List of reference lines to display in this layer."""
