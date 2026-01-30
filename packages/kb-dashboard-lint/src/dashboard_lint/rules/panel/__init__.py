"""Panel-level lint rules.

These rules check individual panels for issues like insufficient
size, missing descriptions, or markdown formatting problems.
"""

from dashboard_lint.rules.panel.markdown_header_height import MarkdownHeaderHeightRule
from dashboard_lint.rules.panel.panel_description_recommended import PanelDescriptionRecommendedRule
from dashboard_lint.rules.panel.panel_min_width import PanelMinWidthRule
from dashboard_lint.rules.panel.panel_title_redundant_prefix import PanelTitleRedundantPrefixRule

__all__ = [
    'MarkdownHeaderHeightRule',
    'PanelDescriptionRecommendedRule',
    'PanelMinWidthRule',
    'PanelTitleRedundantPrefixRule',
]
