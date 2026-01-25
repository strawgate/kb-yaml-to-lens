from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping, LegendVisibleEnum, LegendWidthEnum
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes
from dashboard_compiler.panels.charts.lens.dimensions import LensDimensionTypes
from dashboard_compiler.panels.charts.xy.metrics import ESQLXYMetricTypes, LensXYMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel, BaseIdentifiableModel


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
    """Axis extent (bounds) configuration.

    Modes: 'full' (full data range), 'data_bounds' (fit to data), 'custom' (manual min/max).
    """

    mode: Literal['full', 'custom', 'data_bounds'] = Field(default='full')
    """Extent mode. Defaults to 'full'."""

    min: float | None = Field(default=None)
    """Minimum (required for 'custom' mode)."""

    max: float | None = Field(default=None)
    """Maximum (required for 'custom' mode)."""

    enforce: bool | None = Field(default=None)
    """Enforce bounds strictly. Defaults to false."""

    nice_values: bool | None = Field(default=None)
    """Round to nice values. Defaults to true."""

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
    """Area chart appearance options."""

    fill_opacity: float | None = Field(default=None, ge=0.0, le=1.0, description='Fill opacity (0.0 to 1.0).')


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
    """Base bar chart configuration."""

    type: Literal['bar'] = Field('bar')

    appearance: BarChartAppearance | None = Field(None)

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field('stacked')
    """Stacking mode. Defaults to 'stacked'."""


class BaseXYLineChart(BaseXYChart):
    """Base line chart configuration."""

    type: Literal['line'] = Field('line')

    appearance: LineChartAppearance | None = Field(None)

    show_current_time_marker: bool | None = Field(default=None)
    """Show vertical line at current time."""

    hide_endzones: bool | None = Field(default=None)
    """Hide end zones where data is incomplete."""


class BaseXYAreaChart(BaseXYLineChart):
    """Base area chart configuration."""

    type: Literal['area'] = Field('area')

    appearance: AreaChartAppearance | None = Field(None)

    mode: Literal['stacked', 'unstacked', 'percentage'] = Field('stacked')
    """Stacking mode. Defaults to 'stacked'."""


class LensBarChart(BaseXYBarChart, LensXYChartMixin):
    """Lens bar chart configuration.

    Examples:
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
    """Lens line chart configuration.

    Examples:
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
    """Lens area chart configuration.

    Examples:
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
    """ES|QL bar chart configuration.

    Field names must match columns from your ES|QL query.

    Examples:
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
    """ES|QL line chart configuration.

    Field names must match columns from your ES|QL query.

    Examples:
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
    """ES|QL area chart configuration.

    Field names must match columns from your ES|QL query.

    Examples:
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
    """Reference line layer for XY charts (thresholds, SLA targets, etc.)."""

    type: Literal['reference_line'] = 'reference_line'

    data_view: str = Field(default=...)
    """Data view (required for Kibana compatibility)."""

    reference_lines: list[XYReferenceLine] = Field(default_factory=list)
    """Reference lines to display."""
