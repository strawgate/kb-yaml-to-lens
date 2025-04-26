from pydantic import Field
from typing import List, Literal

from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric


class LensXYChart(BaseLensChart):
    """Represents a Bar/Line/Area chart definition within a Lens panel in the YAML schema."""

    type: Literal["bar_stacked", "line", "area"] = "bar_stacked"  # Default to bar_stacked
    dimensions: List[Dimension] = Field(
        ..., description="(Required) Defines the axes (usually x-axis or split/breakdown dimensions).", min_length=1
    )
    metrics: List[Metric] = Field(..., description="(Required) Defines the values (usually y-axis).", min_length=1)
