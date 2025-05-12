"""Configuration for a Markdown Panel in a dashboard."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel


class MarkdownPanel(BasePanel):
    """Represents a Markdown panel configuration.

    Markdown panels are used to display rich text content using Markdown syntax.
    """

    type: Literal['markdown'] = 'markdown'
    content: str = Field(..., description='The Markdown content to be displayed in the panel.')
    font_size: int | None = Field(
        default=None,
        description='The font size for the Markdown content, in pixels. Defaults to 12 if not set.',
    )
    links_in_new_tab: bool | None = Field(
        default=None,
        description='If true, links in the Markdown content will open in a new tab. Defaults to true if not set.',
    )
