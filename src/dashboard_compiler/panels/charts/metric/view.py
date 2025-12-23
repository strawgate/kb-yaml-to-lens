from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnMetricStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Represents a layer within a Metric visualization state in the Kibana JSON structure."""

    layerType: Literal['data'] = 'data'

    metricAccessor: str = Field(...)
    """The ID of the metric column."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the max metric column (for sparkline)."""

    showBar: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to show the sparkline bar."""

    secondaryMetricAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the secondary metric column."""

    breakdownByAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the dimension column for breakdown."""


class KbnMetricVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Metric chart in the Kibana JSON structure."""
