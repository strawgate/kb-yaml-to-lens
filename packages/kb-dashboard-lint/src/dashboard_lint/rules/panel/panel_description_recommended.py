"""Rule: Panels should have descriptions for accessibility."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_lint.rules.core import PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation


@panel_rule
@dataclass(frozen=True)
class PanelDescriptionRecommendedRule(PanelRule[BasePanel]):
    """Rule: Panels should have descriptions for accessibility.

    Panel descriptions provide context for dashboard viewers and improve
    accessibility for screen readers.

    Note: This rule skips markdown panels (self-describing) and untitled
    panels (likely decorative or don't need descriptions).
    """

    id: str = 'panel-description-recommended'
    description: str = 'Panels should have descriptions for accessibility'
    default_severity: Severity = Severity.INFO

    def check_panel(
        self,
        panel: BasePanel,
        context: PanelContext,
        options: dict[str, Any],  # noqa: ARG002
    ) -> ViolationResult:
        """Check panel for missing description.

        Args:
            panel: The panel to check.
            context: Panel context with location helpers.
            options: Rule options (currently unused).

        Returns:
            Violation if description missing, None otherwise.

        """
        # Skip markdown panels (they are self-describing)
        if isinstance(panel, MarkdownPanel):
            return None

        # Skip panels without titles (they likely don't need descriptions)
        if len(panel.title) == 0:
            return None

        if panel.description is None or len(panel.description.strip()) == 0:
            return Violation(
                rule_id=self.id,
                message='Consider adding a description to improve accessibility',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
