"""Tagcloud chart view models for Kibana JSON output."""

from typing import Annotated

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnTagcloudVisualizationState(BaseVwModel):
    """Tagcloud visualization state in Kibana JSON.

    Note: Unlike pie/XY charts, tagcloud uses a flat structure without a layers array.
    The visualization state directly contains the layer ID and accessor configuration.
    """

    layerId: str
    """Layer ID reference for the data source."""

    tagAccessor: Annotated[str | None, OmitIfNone()] = Field(None)
    """Column ID for the bucketed dimension (tags/terms)."""

    valueAccessor: Annotated[str | None, OmitIfNone()] = Field(None)
    """Column ID for the numeric metric dimension (frequency)."""

    maxFontSize: int = Field(default=72)
    """Maximum font size for tags."""

    minFontSize: int = Field(default=12)
    """Minimum font size for tags."""

    orientation: str = Field(default='single')
    """Text orientation configuration."""

    showLabel: bool = Field(default=True)
    """Toggle for label visibility."""
