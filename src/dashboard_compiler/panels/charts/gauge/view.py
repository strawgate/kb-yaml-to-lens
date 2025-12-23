from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnGaugeStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Represents a layer within a Gauge visualization state in the Kibana JSON structure."""

    layerType: Literal['data'] = 'data'

    metricAccessor: str = Field(...)
    """The ID of the metric column."""

    minAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the minimum value column."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the maximum value column."""

    goalAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the goal/target value column."""

    shape: Annotated[Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] | None, OmitIfNone()] = Field(default=None)
    """The visual shape of the gauge."""

    ticksPosition: Annotated[Literal['auto', 'bands', 'hidden'] | None, OmitIfNone()] = Field(default=None)
    """Position of ticks on the gauge."""

    labelMajor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The major label text."""

    labelMinor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The minor label text."""

    colorMode: Annotated[Literal['none', 'palette'] | None, OmitIfNone()] = Field(default=None)
    """Color mode for the gauge."""

    respectRanges: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to respect the defined min/max ranges for coloring."""


class KbnGaugeVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Gauge chart in the Kibana JSON structure."""
