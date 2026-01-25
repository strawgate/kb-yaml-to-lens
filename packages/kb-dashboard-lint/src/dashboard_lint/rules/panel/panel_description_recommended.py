"""Rule: Panels should have descriptions for accessibility."""

from dataclasses import dataclass

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_lint.rules.core import EmptyOptions, PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation


@panel_rule
@dataclass(frozen=True)
class PanelDescriptionRecommendedRule(PanelRule[BasePanel, EmptyOptions]):
    """Rule: Panels should have descriptions for accessibility.

    Panel descriptions provide context for dashboard viewers and improve
    accessibility for screen readers.

    Note: This rule skips markdown panels (self-describing) and untitled
    panels (likely decorative or don't need descriptions).
    """

    id: str = 'panel-description-recommended'
    description: str = 'Panels should have descriptions for accessibility'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_panel(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: BasePanel,
        context: PanelContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check panel for missing description.

        Args:
            panel: The panel to check.
            context: Panel context with location helpers.
            options: Validated rule options (empty for this rule).

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
