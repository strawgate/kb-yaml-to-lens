"""Rule: Markdown panels with headers must have sufficient height."""

import re
from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_lint.rules.core import PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match markdown headers (# through ######)
HEADER_PATTERN = re.compile(r'^#{1,6}\s+', re.MULTILINE)


@panel_rule(panel_types=(MarkdownPanel,))
@dataclass(frozen=True)
class MarkdownHeaderHeightRule(PanelRule):
    """Rule: Markdown panels with headers must have sufficient height.

    Markdown panels containing headers (lines starting with #) should have
    a height of at least 3 grid units to display properly. Smaller heights
    may cause the header text to be cut off or look cramped.

    Options:
        min_height (int): Minimum height for panels with headers. Default: 3.
    """

    id: str = 'markdown-header-height'
    description: str = 'Markdown panels with headers must have height >= 3'
    default_severity: Severity = Severity.WARNING
    panel_types: tuple[type[BasePanel], ...] | None = (MarkdownPanel,)

    def check_panel(
        self,
        panel: BasePanel,
        context: PanelContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check markdown panel for insufficient height with headers.

        Args:
            panel: The markdown panel to check.
            context: Panel context with location helpers.
            options: Rule options with optional 'min_height' key.

        Returns:
            Violation if header present and height too small, None otherwise.

        """
        # Type is guaranteed by panel_types filter
        if not isinstance(panel, MarkdownPanel):
            return None

        min_height = options.get('min_height', 3)
        content = panel.markdown.content
        height = panel.size.h

        # Check if content contains headers
        if HEADER_PATTERN.search(content) is not None and height < min_height:
            return Violation(
                rule_id=self.id,
                message=f'Markdown with headers should have height >= {min_height} (current: {height})',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
