from pydantic import Field
from typing import Literal

from dashboard_compiler.models.config.panels.base import BasePanel


class MarkdownPanel(BasePanel):
    """Represents a Markdown panel in the YAML schema."""

    type: Literal["markdown"] = "markdown"
    content: str = Field(..., description="(Required) The markdown content to display.")
