from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.dimensions.config import ESQLDimensionTypes, LensDimensionTypes
from dashboard_compiler.panels.charts.metrics.config import ESQLMetricTypes, LensMetricTypes
from dashboard_compiler.shared.charts.config import ESQLChartMixin, LensChartMixin
from dashboard_compiler.shared.config import BaseCfgModel


class PieLegendWidthEnum(StrEnum):
    """Represents the possible values for the width of the legend in a pie chart."""

    SMALL = 'small'
    """Small legend."""

    MEDIUM = 'medium'
    """Medium legend."""

    LARGE = 'large'
    """Large legend."""

    EXTRA_LARGE = 'extra_large'
    """Extra large legend."""


class PieLegendVisibleEnum(StrEnum):
    """Represents the possible values for the visibility of the legend in a pie chart."""

    SHOW = 'show'
    """Show the legend."""

    HIDE = 'hide'
    """Hide the legend."""

    AUTO = 'auto'
    """Automatically determine the visibility of the legend based on the data."""


class PieLegend(BaseCfgModel):
    """Represents legend formatting options for pie charts."""

    visible: PieLegendVisibleEnum | None = Field(default=None, strict=False) # Turn off strict for enums
    """Visibility of the legend in the pie chart. Kibana defaults to 'auto' if not specified."""

    width: PieLegendWidthEnum | None = Field(default=None, strict=False) # Turn off strict for enums
    """Width of the legend in the pie chart. Kibana defaults to 'medium' if not specified."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""


class PieSliceValuesEnum(StrEnum):
    """Represents the possible values for slice values in a pie chart."""

    HIDE = 'hide'
    """Hide the slice values."""

    INTEGER = 'integer'
    """Show the slice values as integers."""

    PERCENT = 'percent'
    """Show the slice values as percentages."""


class PieSliceLabelsEnum(StrEnum):
    """Represents the possible values for slice labels in a pie chart."""

    HIDE = 'hide'
    """Hide the slice labels."""

    INSIDE = 'inside'
    """Show the slice labels on the inside of the pie chart."""

    AUTO = 'auto'
    """Automatically determine the slice labels based on the data."""


class PieTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for pie charts."""

    slice_labels: PieSliceLabelsEnum | None = Field(default=None, strict=False) # Turn off strict for enums
    """Controls the visibility of slice labels in the pie chart. Kibana defaults to 'auto' if not specified."""

    slice_values: PieSliceValuesEnum | None = Field(default=None, strict=False) # Turn off strict for enums
    """Controls the display of slice values in the pie chart. Kibana defaults to 'percentage' if not specified."""

    value_decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for slice values in the pie chart. Kibana defaults to 2, if not specified."""


class PieChartAppearance(BaseCfgModel):
    """Represents chart appearance formatting options for charts."""

    donut: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """Controls the size of the donut hole in the pie chart. Kibana defaults to 'medium' if not specified."""


class BasePieChart(BaseCfgModel):
    """Base model for defining Pie chart objects."""

    type: Literal['pie'] = Field(default='pie')

    appearance: PieChartAppearance | None = Field(default=None)
    """Formatting options for the chart appearance, including donut size."""

    titles_and_text: PieTitlesAndText | None = Field(default=None)
    """Formatting options for the chart titles and text."""

    legend: PieLegend | None = Field(default=None)
    """Formatting options for the chart legend."""


class LensPieChart(BasePieChart, LensChartMixin):
    """Represents a Pie chart configuration within a Lens panel.

    Pie charts are used to visualize the proportion of categories.
    """

    metric: LensMetricTypes = Field(default=...)
    """A metric that determines the size of the slice of the pie chart."""

    slice_by: list[LensDimensionTypes] = Field(default=...)
    """The dimensions that determine the slices of the pie chart."""


class ESQLPieChart(BasePieChart, ESQLChartMixin):
    """Represents a Pie chart configuration within an ES|QL panel."""

    metric: ESQLMetricTypes = Field(default=...)
    """A metric that determines the size of the slice of the pie chart."""

    slice_by: list[ESQLDimensionTypes] = Field(default=...)
    """The dimensions that determine the slices of the pie chart."""

    # query: str = Field(default=...)
    # """The ES|QL query that determines the data for the pie chart."""
