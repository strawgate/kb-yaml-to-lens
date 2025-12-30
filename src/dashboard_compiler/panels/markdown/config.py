"""Configuration for a Markdown Panel in a dashboard."""

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.shared.config import BaseCfgModel


class MarkdownPanelConfig(BaseCfgModel):
    """Configuration specific to Markdown panels."""

    content: str = Field(...)
    """The Markdown content to be displayed in the panel."""

    font_size: int | None = Field(default=None)
    """The font size for the Markdown content, in pixels. Defaults to 12 if not set."""

    links_in_new_tab: bool | None = Field(default=None)
    """If true, links in the Markdown content will open in a new tab. Defaults to false if not set."""


class MarkdownPanel(BasePanel):
    """Represents a Markdown panel configuration.

    Markdown panels are used to display rich text content using Markdown syntax.
    """

    markdown: MarkdownPanelConfig = Field(...)
    """Markdown panel configuration."""
