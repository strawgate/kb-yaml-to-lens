from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.visualizations.view import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    layerType: Literal['data'] = 'data'
    primaryGroups: list[str]
    metrics: list[str]
    numberDisplay: str
    categoryDisplay: str
    legendDisplay: str
    nestedLegend: bool


class KbnPieVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Pie chart in the Kibana JSON structure."""

    shape: Literal['pie'] = 'pie'
    layers: list[KbnPieStateVisualizationLayer] = Field(...)
