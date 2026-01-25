"""Tests for DashboardDatasetFilterRule."""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.rules.dashboard import DashboardDatasetFilterRule


class TestDashboardDatasetFilterRule:
    """Tests for DashboardDatasetFilterRule."""

    def test_detects_missing_dataset_filter(self, dashboard_without_dataset_filter: Dashboard) -> None:
        """Should detect dashboards without dataset filter."""
        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard_without_dataset_filter, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'dashboard-dataset-filter'
        assert 'data_stream.dataset' in violations[0].message

    def test_passes_with_dataset_filter(self, dashboard_with_dataset_filter: Dashboard) -> None:
        """Should not flag dashboards with dataset filter."""
        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard_with_dataset_filter, {})

        assert len(violations) == 0
