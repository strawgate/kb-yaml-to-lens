from typing import Literal

from pydantic import Field

from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric


class LensPieChart(BaseLensChart):
    """Represents a Pie chart definition within a Lens panel in the YAML schema."""

    type: Literal["pie"] = "pie"
    dimensions: list[Dimension] = Field(
        ..., description="(Required) Defines the 'Slice by' dimension. Usually one 'terms' aggregation.", max_length=1
    )
    metrics: list[Metric] = Field(..., description="(Required) Defines the 'Size by' metric. Usually one metric.", max_length=1)
