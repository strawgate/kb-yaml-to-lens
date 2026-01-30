"""Rule: Dashboards should have a description."""

from dataclasses import dataclass

from dashboard_lint.rules.core import DashboardRule, EmptyOptions, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.dashboard.config import Dashboard


@dashboard_rule
@dataclass(frozen=True)
class DashboardMissingDescriptionRule(DashboardRule[EmptyOptions]):
    """Rule: Dashboards should have a description.

    Dashboard descriptions help users understand the purpose of the
    dashboard and what data it displays. They appear in the dashboard
    list and help with discoverability.
    """

    id: str = 'dashboard-missing-description'
    description: str = 'Dashboards should have a description for discoverability'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check if dashboard has a description.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if description is missing or empty, None otherwise.

        """
        if dashboard.description is None or len(dashboard.description.strip()) == 0:
            return Violation(
                rule_id=self.id,
                message='Dashboard is missing a description; add a description to improve discoverability',
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='description',
            )

        return None
