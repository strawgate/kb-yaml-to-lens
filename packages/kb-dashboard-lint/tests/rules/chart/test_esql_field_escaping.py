"""Tests for ESQLFieldEscapingRule."""

import pytest

from dashboard_lint.rules.chart import ESQLFieldEscapingRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLMetricPanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric


@pytest.fixture
def dashboard_with_unescaped_numeric_field() -> Dashboard:
    """Create a dashboard with unescaped numeric field suffix."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Load Average',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM metrics-* | WHERE apache.load.1 IS NOT NULL | STATS avg_load = AVG(apache.load.1)',
                    primary=ESQLMetric(field='avg_load'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_multiple_unescaped_fields() -> Dashboard:
    """Create a dashboard with multiple unescaped numeric fields."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Load Averages',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM metrics-* | WHERE apache.load.1 IS NOT NULL AND apache.load.5 IS NOT NULL',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_escaped_numeric_field() -> Dashboard:
    """Create a dashboard with properly escaped numeric field."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Load Average',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM metrics-* | WHERE `apache.load.1` IS NOT NULL | STATS avg_load = AVG(`apache.load.1`)',
                    primary=ESQLMetric(field='avg_load'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_regular_fields() -> Dashboard:
    """Create a dashboard with regular field names."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Requests',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | WHERE host.name IS NOT NULL | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLFieldEscapingRule:
    """Tests for ESQLFieldEscapingRule."""

    def test_detects_unescaped_numeric_field(self, dashboard_with_unescaped_numeric_field: Dashboard) -> None:
        """Should detect unescaped field with numeric suffix."""
        rule = ESQLFieldEscapingRule()
        violations = rule.check(dashboard_with_unescaped_numeric_field, {})

        assert len(violations) == 2  # Field appears twice in query
        assert violations[0].rule_id == 'esql-field-escaping'
        assert 'apache.load.1' in violations[0].message
        assert 'backtick' in violations[0].message.lower()
        assert violations[0].severity == Severity.WARNING

    def test_detects_multiple_unescaped_fields(self, dashboard_with_multiple_unescaped_fields: Dashboard) -> None:
        """Should detect multiple different unescaped numeric fields."""
        rule = ESQLFieldEscapingRule()
        violations = rule.check(dashboard_with_multiple_unescaped_fields, {})

        assert len(violations) == 2
        field_names = [v.message for v in violations]
        assert any('apache.load.1' in msg for msg in field_names)
        assert any('apache.load.5' in msg for msg in field_names)

    def test_passes_escaped_field(self, dashboard_with_escaped_numeric_field: Dashboard) -> None:
        """Should not flag properly escaped fields."""
        rule = ESQLFieldEscapingRule()
        violations = rule.check(dashboard_with_escaped_numeric_field, {})

        assert len(violations) == 0

    def test_passes_regular_fields(self, dashboard_with_regular_fields: Dashboard) -> None:
        """Should not flag regular field names without numeric suffix."""
        rule = ESQLFieldEscapingRule()
        violations = rule.check(dashboard_with_regular_fields, {})

        assert len(violations) == 0
