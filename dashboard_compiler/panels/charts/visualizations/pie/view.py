from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.visualizations.view import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    layerType: Literal['data'] = 'data'
    primaryGroups: list[str]
    metrics: list[str]
    numberDisplay: str
    categoryDisplay: str
    legendDisplay: str
    nestedLegend: bool
    emptySizeRatio: Annotated[float | None, OmitIfNone()] = Field(None)
    legendSize: Annotated[str | None, OmitIfNone()] = Field(None)
    truncateLegend: Annotated[bool | None, OmitIfNone()] = Field(None)
    legendMaxLines: Annotated[int | None, OmitIfNone()] = Field(None)


class KbnPieVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Pie chart in the Kibana JSON structure."""

    shape: Literal['pie', 'donut']
    layers: list[KbnPieStateVisualizationLayer] = Field(...)
