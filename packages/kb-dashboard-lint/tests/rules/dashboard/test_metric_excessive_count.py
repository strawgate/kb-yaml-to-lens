"""Tests for MetricExcessiveCountRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_lint.rules.dashboard import MetricExcessiveCountRule
from dashboard_lint.types import Severity


def create_metric_panel(title: str) -> LensPanel:
    """Create a metric panel."""
    return LensPanel(
        title=title,
        lens=LensMetricPanelConfig(
            type='metric',
            data_view='logs-*',
            primary=LensCountAggregatedMetric(aggregation='count'),
        ),
    )


@pytest.fixture
def dashboard_with_few_metrics() -> Dashboard:
    """Create a dashboard with few metric panels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            create_metric_panel('Metric 1'),
            create_metric_panel('Metric 2'),
        ],
    )


@pytest.fixture
def dashboard_with_many_metrics() -> Dashboard:
    """Create a dashboard with many metric panels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            create_metric_panel('Metric 1'),
            create_metric_panel('Metric 2'),
            create_metric_panel('Metric 3'),
            create_metric_panel('Metric 4'),
            create_metric_panel('Metric 5'),
            create_metric_panel('Metric 6'),
        ],
    )


class TestMetricExcessiveCountRule:
    """Tests for MetricExcessiveCountRule."""

    def test_passes_few_metrics(self, dashboard_with_few_metrics: Dashboard) -> None:
        """Should not flag dashboards with few metric panels."""
        rule = MetricExcessiveCountRule()
        violations = rule.check(dashboard_with_few_metrics, {})

        assert len(violations) == 0

    def test_detects_many_metrics(self, dashboard_with_many_metrics: Dashboard) -> None:
        """Should detect excessive metric panels."""
        rule = MetricExcessiveCountRule()
        violations = rule.check(dashboard_with_many_metrics, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'metric-excessive-count'
        assert '6' in violations[0].message
        assert '4' in violations[0].message  # Default max
        assert violations[0].severity == Severity.INFO

    def test_custom_max_count(self, dashboard_with_few_metrics: Dashboard) -> None:
        """Should use custom max_count when provided."""
        rule = MetricExcessiveCountRule()
        violations = rule.check(dashboard_with_few_metrics, {'max_count': 1})

        assert len(violations) == 1
        assert '2' in violations[0].message
        assert '1' in violations[0].message
