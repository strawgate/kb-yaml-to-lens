"""Lint rules for Markdown panels."""

import re
from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match markdown headers (# through ######)
HEADER_PATTERN = re.compile(r'^#{1,6}\s+', re.MULTILINE)


@dataclass(frozen=True)
class MarkdownHeaderHeightRule:
    """Rule: Markdown panels with headers must have sufficient height.

    Markdown panels containing headers (lines starting with #) should have
    a height of at least 3 grid units to display properly. Smaller heights
    may cause the header text to be cut off or look cramped.
    """

    id: str = 'markdown-header-height'
    description: str = 'Markdown panels with headers must have height >= 3'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check markdown panels for insufficient height with headers.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - min_height (int): Minimum height for panels with headers. Default: 3.

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.markdown import MarkdownPanel

        violations: list[Violation] = []
        min_height = options.get('min_height', 3)

        for idx, panel in enumerate(dashboard.panels):
            if not isinstance(panel, MarkdownPanel):
                continue

            content = panel.markdown.content
            height = panel.size.h

            # Check if content contains headers
            if HEADER_PATTERN.search(content) is not None and height < min_height:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Markdown with headers should have height >= {min_height} (current: {height})',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}]',
                    )
                )

        return violations


# Register rule with the default registry
register_rule(MarkdownHeaderHeightRule())
