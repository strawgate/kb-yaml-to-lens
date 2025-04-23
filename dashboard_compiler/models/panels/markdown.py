from typing import Dict, Any, Literal, Optional

from pydantic import model_serializer

from dashboard_compiler.models.panels import Panel

DEFAULT_MARKDOWN_FONT_SIZE = 12
DEFAULT_MARKDOWN_OPEN_LINKS_IN_NEW_TAB = False


class MarkdownPanel(Panel):
    """Represents a Markdown panel in a dashboard.

    Typically defined as:
    {
        "id": "", # This appears blank in our samples
        "title": "Markdown Panel",
        "description": "Cool description",
        "type": "markdown",
        "params": {
            "fontSize": 12,
            "openLinksInNewTab": false,
            "markdown": "# This is a basic markdown test"
        },
        "uiState": {},
        "data": {
            "aggs": [],
            "searchSource": {
                "query": {
                    "query": "",
                    "language": "kuery"
                },
                "filter": []
            }
        }
    }

    Arguments:
        content: The markdown content to display in the panel.
        font_size: Optional; the font size for the markdown text.
        open_links_in_new_tab: Optional; whether to open links in a new tab.
    """

    content: str
    type: Literal["markdown"] = "markdown"

    font_size: Optional[int] = DEFAULT_MARKDOWN_FONT_SIZE
    open_links_in_new_tab: Optional[bool] = DEFAULT_MARKDOWN_OPEN_LINKS_IN_NEW_TAB

    @model_serializer
    def to_dict(self) -> Dict[str, Any]:
        """Convert the MarkdownPanel to a dictionary representation."""

        base_panel = super().to_dict()

        markdown_panel_config = {
            "embeddableConfig": {
                "enhancements": {"dynamicActions": {"events": []}},
                "savedVis": {
                    "description": self.description,
                    "id": "",
                    "params": {
                        "fontSize": self.font_size,
                        "openLinksInNewTab": self.open_links_in_new_tab,
                        "markdown": self.content,
                    },
                    "title": self.title,
                    "type": "markdown",
                    "uiState": {},
                    "data": {
                        "aggs": [],
                        "searchSource": {
                            "query": {"query": "", "language": "kuery"},
                            "filter": [],
                        },
                    },
                },
            }
        }

        markdown_panel = base_panel | markdown_panel_config

        return markdown_panel
