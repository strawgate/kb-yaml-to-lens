"""Rule: Dashboards should not have excessive metric panels."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_lint.rules.core import DashboardRule, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation


class MetricExcessiveCountOptions(BaseModel):
    """Options for the metric-excessive-count rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    max_count: int = Field(
        default=4,
        ge=0,
        description='Maximum number of metric panels before warning',
    )


@dashboard_rule
@dataclass(frozen=True)
class MetricExcessiveCountRule(DashboardRule[MetricExcessiveCountOptions]):
    """Rule: Dashboards should not have excessive metric panels.

    According to the dashboard style guide, 0-4 metric cards is typical.
    Having too many metric panels can make the dashboard cluttered and
    make it harder for users to focus on important data.

    Options:
        max_count (int): Maximum metric panels before warning. Default: 4.
    """

    id: str = 'metric-excessive-count'
    description: str = 'Dashboards should not have excessive metric panels (style guide recommends 0-4)'
    default_severity: Severity = Severity.INFO
    options_model: type[MetricExcessiveCountOptions] = MetricExcessiveCountOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: MetricExcessiveCountOptions,
    ) -> ViolationResult:
        """Check if dashboard has excessive metric panels.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule options.

        Returns:
            Violation if metric count exceeds max_count, None otherwise.

        """
        metric_count = 0

        for panel in dashboard.panels:
            if isinstance(panel, (LensPanel, ESQLPanel)):
                config = panel.lens if isinstance(panel, LensPanel) else panel.esql
                if config.type == 'metric':
                    metric_count += 1

        if metric_count > options.max_count:
            return Violation(
                rule_id=self.id,
                message=f'Dashboard has {metric_count} metric panels, which exceeds the recommended maximum of {options.max_count}',
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='panels',
            )

        return None
