"""Tests for ESQLGroupBySyntaxRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLMetricPanelConfig, ESQLPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_lint.rules.chart import ESQLGroupBySyntaxRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_group_by() -> Dashboard:
    """Create a dashboard using GROUP BY (SQL syntax)."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events by Host',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*) GROUP BY host.name',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_correct_by() -> Dashboard:
    """Create a dashboard using correct BY syntax."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events by Host',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*) BY host.name',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLGroupBySyntaxRule:
    """Tests for ESQLGroupBySyntaxRule."""

    def test_detects_group_by(self, dashboard_with_group_by: Dashboard) -> None:
        """Should detect GROUP BY and suggest BY."""
        rule = ESQLGroupBySyntaxRule()
        violations = rule.check(dashboard_with_group_by, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-group-by-syntax'
        assert 'BY' in violations[0].message
        assert 'GROUP BY' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_passes_correct_by(self, dashboard_with_correct_by: Dashboard) -> None:
        """Should not flag correct BY syntax."""
        rule = ESQLGroupBySyntaxRule()
        violations = rule.check(dashboard_with_correct_by, {})

        assert len(violations) == 0
