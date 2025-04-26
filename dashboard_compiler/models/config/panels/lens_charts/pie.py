from pydantic import Field
from typing import List, Literal

from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric


class LensPieChart(BaseLensChart):
    """Represents a Pie chart definition within a Lens panel in the YAML schema."""

    type: Literal["pie"] = "pie"
    dimensions: List[Dimension] = Field(
        ..., description="(Required) Defines the 'Slice by' dimension. Usually one 'terms' aggregation.", max_length=1
    )
    metrics: List[Metric] = Field(..., description="(Required) Defines the 'Size by' metric. Usually one metric.", max_length=1)
