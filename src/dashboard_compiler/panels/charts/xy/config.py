from typing import Literal, Self

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class XYReferenceLineValue(BaseCfgModel):
    """Defines the value for a reference line.

    Ode to Reference Lines
    By Claude, for @graphaelli

    How do you know something is good
    Without a reference to compare?
    A line upon the graph, understood—
    A threshold floating in the air.

    Is your response time fast or slow?
    Are metrics high or are they low?
    Without that line to tell you so,
    You simply cannot truly know.

    I draw a line at not knowing whether
    My dashboards show the truth or not.
    So mark your targets, tethered
    To values that define the plot.

    A reference line—both guide and guard,
    Your SLA in visual form.
    When metrics stray, you're not caught off guard—
    The line reveals what's not the norm.

    So draw your lines with purpose clear,
    Let thresholds guide your watchful eye.
    For in this graph we hold most dear,
    A reference line shows bad from high.
    """

    type: Literal['static'] = 'static'
    value: float = Field(..., description='The static value for the reference line.')


class XYReferenceLine(BaseCfgModel):
    """Configuration for a single reference line in an XY chart."""

    id: str | None = Field(default=None, description='Optional ID for the reference line.')
    label: str | None = Field(default=None, description='Optional label for the reference line.')
    value: XYReferenceLineValue | float = Field(
        ..., description='The value for the reference line. Can be a float or XYReferenceLineValue object.'
    )
    axis: Literal['left', 'right'] | None = Field(default='left', description='The axis to assign the reference line to.')
    color: str | None = Field(default=None, description='The color of the reference line.')
    line_width: int | None = Field(default=None, ge=1, le=10, description='The width of the reference line (1-10).')
    line_style: Literal['solid', 'dashed', 'dotted'] | None = Field(default=None, description='The style of the reference line.')
    fill: Literal['above', 'below', 'none'] | None = Field(default=None, description='Fill area above or below the line.')
    icon: str | None = Field(default=None, description='Icon to display on the reference line.')
    icon_position: Literal['auto', 'left', 'right', 'above', 'below'] | None = Field(
        default=None, description='Position of the icon on the reference line.'
    )


type XYChartTypes = LensXYChartTypes | ESQLXYChartTypes

type LensXYChartTypes = LensBarChart | LensLineChart | LensAreaChart
type ESQLXYChartTypes = ESQLBarChart | ESQLLineChart | ESQLAreaChart


class XYLegend(BaseCfgModel):
    """Represents legend formatting options for XY charts."""

    visible: bool | None = Field(default=None, description='Whether the legend is visible.')


class XYAppearance(BaseCfgModel):
    """Represents chart appearance formatting options for XY charts."""


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

    reference_lines: list[XYReferenceLine] | None = Field(
        None,
        description='Reference lines to display on the chart for threshold visualization.',
    )


class LensXYChartMixin:
    """Shared fields for Lens-based XY charts."""

    data_view: str = Field(default=..., description='The data view to use for the chart.')  # type: ignore[reportAny]
    dimensions: list[LensDimensionTypes] = Field(..., description='Defines the dimensions for the chart.')  # type: ignore[reportAny]
    metrics: list[LensMetricTypes] = Field(..., description='Defines the metrics for the chart.')  # type: ignore[reportAny]
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


class ESQLXYChartMixin:
    """Shared fields for ESQL-based XY charts."""

    dimensions: list[ESQLDimensionTypes] = Field(..., description='Defines the dimensions for the chart.')  # type: ignore[reportAny]

    metrics: list[ESQLMetricTypes] = Field(..., description='Defines the metrics for the chart.')  # type: ignore[reportAny]

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
