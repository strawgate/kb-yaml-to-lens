"""Rule: Markdown navigation panels should be positioned at the top."""

from dataclasses import dataclass

from dashboard_lint.rules.core import DashboardRule, EmptyOptions, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.markdown import MarkdownPanel


@dashboard_rule
@dataclass(frozen=True)
class MarkdownAtTopRule(DashboardRule[EmptyOptions]):
    """Rule: Markdown navigation panels should be positioned at the top.

    Markdown panels typically contain navigation links, context information,
    or section headers. Following the dashboard style guide, these should
    be positioned at y=0 (top of dashboard) for discoverability.

    This rule checks markdown panels that appear to contain navigation content
    (links, headers) and warns if they're not at the top position.
    """

    id: str = 'markdown-at-top'
    description: str = 'Markdown panels with navigation content should be at the top of the dashboard'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check if markdown panels with navigation content are at top.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule options (empty for this rule).

        Returns:
            List of violations for mispositioned markdown panels.

        """
        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            if not isinstance(panel, MarkdownPanel):
                continue

            content = panel.markdown.content

            # Check if this appears to be navigation/header content
            # Navigation indicators: links, headers at start
            has_links = '](/' in content or '](http' in content or '](#' in content
            starts_with_header = content.strip().startswith('#')
            is_navigation_panel = has_links or starts_with_header

            if not is_navigation_panel:
                continue

            # Get panel position - y may be None if not explicitly set
            panel_y = panel.position.y if panel.position and panel.position.y is not None else 0

            if panel_y > 0:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Markdown panel with navigation content is at y={panel_y}; consider moving to y=0',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].position',
                    )
                )

        return violations
