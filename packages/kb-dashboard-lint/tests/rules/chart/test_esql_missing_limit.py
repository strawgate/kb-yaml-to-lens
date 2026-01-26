"""Tests for ESQLMissingLimitRule."""

import pytest

from dashboard_lint.rules.chart import ESQLMissingLimitRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLDatatablePanelConfig, ESQLMetricPanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric


@pytest.fixture
def dashboard_with_sort_desc_no_limit() -> Dashboard:
    """Create a dashboard with SORT DESC but no LIMIT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Top Hosts',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC',
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_sort_desc_and_limit() -> Dashboard:
    """Create a dashboard with SORT DESC and proper LIMIT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Top Hosts',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC | LIMIT 10',
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_without_sort_desc() -> Dashboard:
    """Create a dashboard without SORT DESC."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Count',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLMissingLimitRule:
    """Tests for ESQLMissingLimitRule."""

    def test_detects_sort_desc_without_limit(self, dashboard_with_sort_desc_no_limit: Dashboard) -> None:
        """Should detect SORT DESC without LIMIT."""
        rule = ESQLMissingLimitRule()
        violations = rule.check(dashboard_with_sort_desc_no_limit, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-missing-limit'
        assert 'LIMIT' in violations[0].message
        assert violations[0].severity == Severity.INFO

    def test_passes_sort_desc_with_limit(self, dashboard_with_sort_desc_and_limit: Dashboard) -> None:
        """Should not flag SORT DESC with LIMIT."""
        rule = ESQLMissingLimitRule()
        violations = rule.check(dashboard_with_sort_desc_and_limit, {})

        assert len(violations) == 0

    def test_passes_without_sort_desc(self, dashboard_without_sort_desc: Dashboard) -> None:
        """Should not flag queries without SORT DESC."""
        rule = ESQLMissingLimitRule()
        violations = rule.check(dashboard_without_sort_desc, {})

        assert len(violations) == 0

    def test_custom_suggested_limit(self, dashboard_with_sort_desc_no_limit: Dashboard) -> None:
        """Should use custom suggested_limit in message."""
        rule = ESQLMissingLimitRule()
        violations = rule.check(dashboard_with_sort_desc_no_limit, {'suggested_limit': 5})

        assert len(violations) == 1
        assert 'LIMIT 5' in violations[0].message
