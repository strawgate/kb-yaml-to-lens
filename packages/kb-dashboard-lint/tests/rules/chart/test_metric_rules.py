"""Tests for metric-related chart rules."""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Size
from dashboard_lint.rules.chart import MetricMultipleMetricsWidthRule, MetricRedundantLabelRule


class TestMetricMultipleMetricsWidthRule:
    """Tests for MetricMultipleMetricsWidthRule."""

    def test_detects_narrow_multi_metric(self) -> None:
        """Should detect multi-metric panels with insufficient width."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Multi Metric',
                    size=Size(w=8, h=5),  # Width 8 is below 12 for multi-metric
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count', label='Count'),
                        secondary=LensCountAggregatedMetric(aggregation='count', label='Secondary'),
                    ),
                ),
            ],
        )

        rule = MetricMultipleMetricsWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'metric-multiple-metrics-width'
        assert '2 metrics' in violations[0].message

    def test_passes_wide_multi_metric(self) -> None:
        """Should not flag wide multi-metric panels."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Wide Multi Metric',
                    size=Size(w=16, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                        secondary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = MetricMultipleMetricsWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_single_metric(self) -> None:
        """Should not flag single-metric panels regardless of width."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Single Metric',
                    size=Size(w=6, h=5),  # Narrow but only one metric
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = MetricMultipleMetricsWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0


class TestMetricRedundantLabelRule:
    """Tests for MetricRedundantLabelRule."""

    def test_detects_redundant_label(self, dashboard_with_redundant_label: Dashboard) -> None:
        """Should detect metric panels with redundant labels."""
        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard_with_redundant_label, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'metric-redundant-label'
        assert 'hide_title' in violations[0].message

    def test_passes_with_hidden_title(self, dashboard_with_hidden_title: Dashboard) -> None:
        """Should not flag panels with hide_title=True."""
        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard_with_hidden_title, {})

        assert len(violations) == 0
