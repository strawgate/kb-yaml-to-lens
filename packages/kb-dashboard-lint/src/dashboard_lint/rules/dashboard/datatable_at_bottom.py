"""Rule: Data table panels should be positioned at the bottom of the dashboard."""

from dataclasses import dataclass

from dashboard_lint.rules.core import DashboardRule, EmptyOptions, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel


@dashboard_rule
@dataclass(frozen=True)
class DatatableAtBottomRule(DashboardRule[EmptyOptions]):
    """Rule: Data table panels should be positioned at the bottom.

    Following the dashboard style guide, data tables work best at the
    bottom of dashboards. They provide detailed drill-down data after
    users have seen the summary visualizations (metrics, charts, etc.).

    This rule warns when a datatable panel is positioned above other
    non-datatable visualization panels.
    """

    id: str = 'datatable-at-bottom'
    description: str = 'Data table panels should be positioned at the bottom of the dashboard'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check if datatable panels are positioned appropriately.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule options (empty for this rule).

        Returns:
            List of violations for datatables positioned above other visualizations.

        """
        violations: list[Violation] = []

        # Collect datatable positions and other visualization positions
        datatable_info: list[tuple[int, int, str | None]] = []  # (idx, y, title)
        other_viz_max_y = -1

        for idx, panel in enumerate(dashboard.panels):
            # Get y position, defaulting to 0 if not set
            panel_y = panel.position.y if panel.position and panel.position.y is not None else 0

            if isinstance(panel, (LensPanel, ESQLPanel)):
                config = panel.lens if isinstance(panel, LensPanel) else panel.esql
                if config.type == 'datatable':
                    title = panel.title if len(panel.title) > 0 else None
                    datatable_info.append((idx, panel_y, title))
                else:
                    # Track the maximum Y position of non-datatable visualizations
                    other_viz_max_y = max(other_viz_max_y, panel_y)

        # If no other visualizations exist, there's nothing to compare against
        if other_viz_max_y < 0:
            return violations

        # Check if any datatable is above other visualizations
        for idx, datatable_y, title in datatable_info:
            if datatable_y < other_viz_max_y:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Data table at y={datatable_y} is above other visualizations; consider moving to bottom',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=title,
                        location=f'panels[{idx}].position',
                    )
                )

        return violations
