from typing import Literal

from pydantic import Field

from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric


class LensMetricsChart(BaseLensChart):
    """Represents a Metric chart within a Lens panel in the YAML schema."""

    type: Literal["metric"] = "metric"
    metrics: list[Metric] = Field(..., description="(Required) List of metrics for the chart.")
