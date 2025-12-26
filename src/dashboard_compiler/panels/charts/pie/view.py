from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Represents a data layer within a Pie/Donut visualization state in the Kibana JSON structure."""

    layerType: Literal['data'] = 'data'
    """Layer type identifier for pie chart data layers."""

    primaryGroups: list[str]
    """Column IDs for primary dimension grouping (slice categories)."""

    secondaryGroups: Annotated[list[str] | None, OmitIfNone()] = Field(None)
    """Column IDs for secondary dimension grouping (nested slices)."""

    metrics: list[str]
    """Column IDs for metric values (slice sizes)."""

    allowMultipleMetrics: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to allow multiple metrics in the visualization."""

    collapseFns: Annotated[dict[str, str] | None, OmitIfNone()] = Field(None)
    """Aggregation functions for collapsing multiple values."""

    numberDisplay: str
    """Display format for numeric values (e.g., 'percent', 'value')."""

    categoryDisplay: str
    """Display format for category labels."""

    legendDisplay: str
    """Legend visibility setting (e.g., 'show', 'hide', 'default')."""

    nestedLegend: bool
    """Whether to show legend in nested format."""

    emptySizeRatio: Annotated[float | None, OmitIfNone()] = Field(None)
    """Size ratio for the empty center (donut hole) as a value between 0 and 1."""

    legendSize: Annotated[str | None, OmitIfNone()] = Field(None)
    """Legend size setting (e.g., 'small', 'medium', 'large', 'auto')."""

    truncateLegend: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to truncate long legend labels."""

    legendMaxLines: Annotated[int | None, OmitIfNone()] = Field(None)
    """Maximum number of lines for legend labels when truncated."""


class KbnPieVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Pie chart in the Kibana JSON structure."""

    shape: Literal['pie', 'donut']
    layers: list[KbnPieStateVisualizationLayer] = Field(...)
