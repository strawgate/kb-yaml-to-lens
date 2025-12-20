from typing import Literal, Self

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel

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


class LensXYChartMixin:
    """Shared fields for Lens-based XY charts."""

    data_view: str = Field(default=..., description='The data view to use for the chart.')
    dimensions: list[LensDimensionTypes] = Field(..., description='Defines the dimensions for the chart.')
    metrics: list[LensMetricTypes] = Field(..., description='Defines the metrics for the chart.')
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

    dimensions: list[ESQLDimensionTypes] = Field(..., description='Defines the dimensions for the chart.')

    metrics: list[ESQLMetricTypes] = Field(..., description='Defines the metrics for the chart.')

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
