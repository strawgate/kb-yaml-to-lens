"""Configuration for a Markdown Panel in a dashboard."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel


class ImagePanel(BasePanel):
    """Represents a Image panel configuration.

    Image panels are used to display images.
    """

    type: Literal['image'] = 'image'

    from_url: str = Field(default=...)
    """The URL of the image to be displayed in the panel. This is a required field."""

    fit: Literal['contain', 'cover', 'fill', 'none'] | None = Field(default=None)
    """The sizing of the image. Can be "contain", "cover", "fill", or "none". Defaults to "contain"."""

    description: str | None = Field(default=None)
    """Alternative text for the image, used for accessibility. Defaults to an empty string if not set."""

    background_color: str | None = Field(default=None)
    """Background color for the image panel. Defaults to an empty string if not set."""
