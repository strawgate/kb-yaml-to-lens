"""Tests for ESQLSqlSyntaxRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLMetricPanelConfig, ESQLPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_lint.rules.chart import ESQLSqlSyntaxRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_order_by() -> Dashboard:
    """Create a dashboard with ORDER BY in ES|QL query."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*) | ORDER BY count DESC',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_select() -> Dashboard:
    """Create a dashboard starting with SELECT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='SELECT COUNT(*) FROM logs-*',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_single_equals() -> Dashboard:
    """Create a dashboard with single = comparison."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | WHERE status = 200 | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_percent_wildcard() -> Dashboard:
    """Create a dashboard with % wildcard in LIKE."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Errors',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query="FROM logs-* | WHERE status == 200 AND message LIKE '%error%' | STATS count = COUNT(*)",
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_valid_esql() -> Dashboard:
    """Create a dashboard with valid ES|QL syntax."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | WHERE status == 200 | STATS count = COUNT(*) | SORT count DESC',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLSqlSyntaxRule:
    """Tests for ESQLSqlSyntaxRule."""

    def test_detects_order_by(self, dashboard_with_order_by: Dashboard) -> None:
        """Should detect ORDER BY and suggest SORT."""
        rule = ESQLSqlSyntaxRule()
        violations = rule.check(dashboard_with_order_by, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-sql-syntax'
        assert 'SORT' in violations[0].message
        assert 'ORDER BY' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_detects_select(self, dashboard_with_select: Dashboard) -> None:
        """Should detect SELECT at query start."""
        rule = ESQLSqlSyntaxRule()
        violations = rule.check(dashboard_with_select, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-sql-syntax'
        assert 'SELECT' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_detects_single_equals(self, dashboard_with_single_equals: Dashboard) -> None:
        """Should detect single = and suggest ==."""
        rule = ESQLSqlSyntaxRule()
        violations = rule.check(dashboard_with_single_equals, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-sql-syntax'
        assert '==' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_detects_percent_wildcard(self, dashboard_with_percent_wildcard: Dashboard) -> None:
        """Should detect % wildcard and suggest *."""
        rule = ESQLSqlSyntaxRule()
        violations = rule.check(dashboard_with_percent_wildcard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-sql-syntax'
        assert '*' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_passes_valid_esql(self, dashboard_with_valid_esql: Dashboard) -> None:
        """Should not flag valid ES|QL syntax."""
        rule = ESQLSqlSyntaxRule()
        violations = rule.check(dashboard_with_valid_esql, {})

        assert len(violations) == 0
