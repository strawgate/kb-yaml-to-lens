"""Tests for ESQLTSMetricsMinVersionRule."""

import pytest

from dashboard_lint.rules.chart import ESQLTSMetricsMinVersionRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLLinePanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.xy.metrics import XYESQLMetric


@pytest.fixture
def dashboard_with_ts_metrics() -> Dashboard:
    """Create a dashboard using TS against metrics-* source."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='TS metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_ts_logs() -> Dashboard:
    """Create a dashboard using TS against non-metrics source."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Logs over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='TS logs-* | STATS count = COUNT(*)',
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_from_metrics() -> Dashboard:
    """Create a dashboard using FROM against metrics-* source."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


class TestESQLTSMetricsMinVersionRule:
    """Tests for ESQLTSMetricsMinVersionRule."""

    def test_passes_ts_metrics(self, dashboard_with_ts_metrics: Dashboard) -> None:
        """Should not flag TS metrics-* usage."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_ts_metrics, {})

        assert len(violations) == 0

    def test_passes_ts_non_metrics(self, dashboard_with_ts_logs: Dashboard) -> None:
        """Should not flag TS for non-metrics sources."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_ts_logs, {})

        assert len(violations) == 0

    def test_detects_from_metrics(self, dashboard_with_from_metrics: Dashboard) -> None:
        """Should warn when FROM is used with metrics-*."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_from_metrics, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-ts-metrics-min-version'
        assert 'TS metrics-*' in violations[0].message
        assert violations[0].severity == Severity.WARNING
