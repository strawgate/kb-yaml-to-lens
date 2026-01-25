"""Rule: Dashboards should have a data_stream.dataset filter."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.filters import PhraseFilter, PhrasesFilter
from dashboard_lint.rules.core import DashboardRule, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation


class DashboardDatasetFilterOptions(BaseModel):
    """Options for the dashboard-dataset-filter rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    field: str = Field(
        default='data_stream.dataset',
        description='Field name to check for a filter',
    )


@dashboard_rule
@dataclass(frozen=True)
class DashboardDatasetFilterRule(DashboardRule[DashboardDatasetFilterOptions]):
    """Rule: Dashboards should have a data_stream.dataset filter.

    Adding a dataset filter helps scope dashboards to specific data sources
    and improves query performance by limiting the data scanned.

    Only value-matching filters (PhraseFilter and PhrasesFilter) satisfy this
    rule because they restrict the dataset to specific values. ExistsFilter
    only asserts the presence of the dataset field without limiting which
    datasets are included.

    The rule inspects dashboard.filters for PhraseFilter or PhrasesFilter
    matching the configured field name.

    Options:
        field (str): Field name to check for. Default: 'data_stream.dataset'.
    """

    id: str = 'dashboard-dataset-filter'
    description: str = 'Dashboard should have a data_stream.dataset filter'
    default_severity: Severity = Severity.WARNING
    options_model: type[DashboardDatasetFilterOptions] = DashboardDatasetFilterOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: DashboardDatasetFilterOptions,
    ) -> ViolationResult:
        """Check if dashboard has a dataset filter.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule options.

        Returns:
            Violation if no dataset filter found, None otherwise.

        """
        # Check if any filter targets the dataset field
        for filter_obj in dashboard.filters:
            if isinstance(filter_obj, (PhraseFilter, PhrasesFilter)) and filter_obj.field == options.field:
                return None  # Found it, no violation

        return Violation(
            rule_id=self.id,
            message=f"Consider adding a '{options.field}' filter to scope the dashboard",
            severity=self.default_severity,
            dashboard_name=dashboard.name,
            panel_title=None,
            location='filters',
        )
