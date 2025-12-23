"""Tagcloud chart view models for Kibana JSON output."""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnTagcloudStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Tagcloud visualization layer in Kibana JSON."""

    layerType: Literal['data'] = 'data'
    tagAccessor: Annotated[str | None, OmitIfNone()] = Field(None)
    """Column ID for the bucketed dimension (tags/terms)."""

    valueAccessor: Annotated[str | None, OmitIfNone()] = Field(None)
    """Column ID for the numeric metric dimension (frequency)."""

    maxFontSize: int = Field(default=72)
    """Maximum font size for tags."""

    minFontSize: int = Field(default=18)
    """Minimum font size for tags."""

    orientation: str = Field(default='single')
    """Text orientation configuration."""

    showLabel: bool = Field(default=True)
    """Toggle for label visibility."""

    palette: Annotated[dict[str, str] | None, OmitIfNone()] = Field(None)
    """Legacy palette configuration."""


class KbnTagcloudVisualizationState(KbnBaseStateVisualization):
    """Tagcloud visualization state in Kibana JSON."""

    layers: list[KbnTagcloudStateVisualizationLayer] = Field(...)
