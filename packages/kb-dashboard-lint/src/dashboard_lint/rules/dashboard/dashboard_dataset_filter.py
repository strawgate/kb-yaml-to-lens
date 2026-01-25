"""Rule: Dashboards should have a data_stream.dataset filter."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.filters import PhraseFilter, PhrasesFilter
from dashboard_lint.rules.core import DashboardRule, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation


@dashboard_rule
@dataclass(frozen=True)
class DashboardDatasetFilterRule(DashboardRule):
    """Rule: Dashboards should have a data_stream.dataset filter.

    Adding a dataset filter helps scope dashboards to specific data sources
    and improves query performance by limiting the data scanned.

    Options:
        field (str): Field name to check for. Default: 'data_stream.dataset'.
    """

    id: str = 'dashboard-dataset-filter'
    description: str = 'Dashboard should have a data_stream.dataset filter'
    default_severity: Severity = Severity.WARNING

    def check_dashboard(
        self,
        dashboard: Dashboard,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check if dashboard has a dataset filter.

        Args:
            dashboard: The dashboard to check.
            options: Rule options with optional 'field' key.

        Returns:
            Violation if no dataset filter found, None otherwise.

        """
        field_name = options.get('field', 'data_stream.dataset')

        # Check if any filter targets the dataset field
        for filter_obj in dashboard.filters:
            if isinstance(filter_obj, (PhraseFilter, PhrasesFilter)) and filter_obj.field == field_name:
                return None  # Found it, no violation

        return Violation(
            rule_id=self.id,
            message=f"Consider adding a '{field_name}' filter to scope the dashboard",
            severity=self.default_severity,
            dashboard_name=dashboard.name,
            panel_title=None,
            location='filters',
        )
