"""Lint rules for Dashboard-level configurations."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation


@dataclass(frozen=True)
class DashboardDatasetFilterRule:
    """Rule: Dashboards should have a data_stream.dataset filter.

    Adding a dataset filter helps scope dashboards to specific data sources
    and improves query performance by limiting the data scanned.
    """

    id: str = 'dashboard-dataset-filter'
    description: str = 'Dashboard should have a data_stream.dataset filter'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check if dashboard has a dataset filter.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - field (str): Field name to check for. Default: 'data_stream.dataset'.

        Returns:
            List of violations found.

        """
        from dashboard_compiler.filters import PhraseFilter, PhrasesFilter

        violations: list[Violation] = []
        field_name = options.get('field', 'data_stream.dataset')

        # Check if any filter targets the dataset field
        has_dataset_filter = False

        for filter_obj in dashboard.filters:
            if isinstance(filter_obj, (PhraseFilter, PhrasesFilter)) and filter_obj.field == field_name:
                has_dataset_filter = True
                break

        if not has_dataset_filter:
            violations.append(
                Violation(
                    rule_id=self.id,
                    message=f"Consider adding a '{field_name}' filter to scope the dashboard",
                    severity=self.default_severity,
                    dashboard_name=dashboard.name,
                    panel_title=None,
                    location='filters',
                )
            )

        return violations


# Register rule with the default registry
register_rule(DashboardDatasetFilterRule())
