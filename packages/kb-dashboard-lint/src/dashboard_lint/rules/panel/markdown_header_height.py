"""Rule: Markdown panels with headers must have sufficient height."""

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_lint.rules.core import PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match markdown headers (# through ######)
HEADER_PATTERN = re.compile(r'^#{1,6}\s+', re.MULTILINE)


class MarkdownHeaderHeightOptions(BaseModel):
    """Options for the markdown-header-height rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    min_height: int = Field(default=3, ge=1, description='Minimum height for panels with headers')


@panel_rule
@dataclass(frozen=True)
class MarkdownHeaderHeightRule(PanelRule[MarkdownPanel, MarkdownHeaderHeightOptions]):
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
    options_model: type[MarkdownHeaderHeightOptions] = MarkdownHeaderHeightOptions

    def check_panel(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: MarkdownPanel,
        context: PanelContext,
        options: MarkdownHeaderHeightOptions,
    ) -> ViolationResult:
        """Check markdown panel for insufficient height with headers.

        Args:
            panel: The markdown panel to check.
            context: Panel context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if header present and height too small, None otherwise.

        """
        content = panel.markdown.content
        height = panel.size.h

        # Check if content contains headers
        if HEADER_PATTERN.search(content) is not None and height < options.min_height:
            return Violation(
                rule_id=self.id,
                message=f'Markdown with headers should have height >= {options.min_height} (current: {height})',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
