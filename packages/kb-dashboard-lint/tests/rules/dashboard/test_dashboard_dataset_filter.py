"""Tests for DashboardDatasetFilterRule."""

from dashboard_lint.rules.dashboard import DashboardDatasetFilterRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.filters import PhraseFilter


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

    def test_custom_field_option(self) -> None:
        """Should respect custom field option."""
        # Dashboard without the custom field filter
        dashboard = Dashboard(
            name='Test Dashboard',
            filters=[],
            panels=[],
        )

        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard, {'field': 'custom.field.name'})

        assert len(violations) == 1
        assert 'custom.field.name' in violations[0].message

    def test_custom_field_passes_when_present(self) -> None:
        """Should pass when custom field filter is present."""
        dashboard = Dashboard(
            name='Test Dashboard',
            filters=[
                PhraseFilter(field='custom.field.name', equals='test-value'),
            ],
            panels=[],
        )

        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard, {'field': 'custom.field.name'})

        assert len(violations) == 0
