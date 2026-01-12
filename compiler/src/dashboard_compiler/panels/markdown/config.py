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

    Examples:
        Minimal Markdown panel:
        ```yaml
        dashboards:
          - name: "Dashboard with Markdown"
            panels:
              - title: "Welcome Note"
                grid: { x: 0, y: 0, w: 48, h: 3 }
                markdown:
                  content: |
                    ## Welcome to the Dashboard!
                    This panel provides an overview of the key metrics and reports available.

                    - Item 1
                    - Item 2
        ```

        Markdown panel with custom font size:
        ```yaml
        dashboards:
          - name: "Informational Dashboard"
            panels:
              - title: "Important Instructions"
                grid: { x: 0, y: 0, w: 32, h: 5 }
                markdown:
                  content: |
                    # Setup Guide

                    Please follow the [official documentation](https://strawgate.github.io/kb-yaml-to-lens/) for setup instructions.

                    Key steps:
                    1. **Download** the installer.
                    2. **Configure** the `config.yaml` file.
                    3. **Run** the start script.
                  font_size: 14
                  links_in_new_tab: false
        ```
    """

    markdown: MarkdownPanelConfig = Field(...)
    """Markdown panel configuration."""
