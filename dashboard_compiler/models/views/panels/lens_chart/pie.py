from typing import Literal

from pydantic import Field

from dashboard_compiler.models.views.panels.lens import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    primaryGroups: list[str]  # List of column IDs for dimensions
    metrics: list[str]  # List of column IDs for metrics
    layerType: str = "data"
    numberDisplay: str
    categoryDisplay: str
    legendDisplay: str
    nestedLegend: bool


# Subclass Kbnfor Pie visualizations state (JSON structure)
class KbnPieVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Pie chart in the Kibana JSON structure."""

    shape: Literal["pie"] = "pie"
    layers: list[KbnPieStateVisualizationLayer] = Field(default_factory=list)  # Use specific layer model
    # palette: Dict[str, Any] | None = Field(None, description="Palette configuration for the pie chart, if applicable")
