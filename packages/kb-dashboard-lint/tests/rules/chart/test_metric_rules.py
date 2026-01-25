"""Tests for metric-related chart rules."""

from dashboard_lint.rules.chart import MetricMultipleMetricsWidthRule, MetricRedundantLabelRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensMetricPanelConfig, LensPanel
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size


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

    def test_detects_narrow_triple_metric(self) -> None:
        """Should detect three-metric panels with insufficient width."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Triple Metric',
                    size=Size(w=8, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                        secondary=LensCountAggregatedMetric(aggregation='count'),
                        maximum=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = MetricMultipleMetricsWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert '3 metrics' in violations[0].message

    def test_respects_min_width_option(self) -> None:
        """Should respect custom min_width_multiple option."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Multi Metric',
                    size=Size(w=10, h=5),  # Between 8 and 12
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
        # Default min_width=12 should flag this
        assert len(rule.check(dashboard, {})) == 1
        # Custom min_width=8 should pass
        assert len(rule.check(dashboard, {'min_width_multiple': 8})) == 0

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

    def test_detects_case_insensitive_redundant_label(self) -> None:
        """Should detect redundant labels using case-insensitive matching."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='CPU Usage',  # Title with different case
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(
                            aggregation='count',
                            label='cpu usage',  # Label with different case
                        ),
                    ),
                ),
            ],
        )

        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'metric-redundant-label'

    def test_passes_with_empty_title(self) -> None:
        """Should not flag panels with empty titles."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='',  # Empty title
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(
                            aggregation='count',
                            label='Some Label',
                        ),
                    ),
                ),
            ],
        )

        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_with_hidden_title(self, dashboard_with_hidden_title: Dashboard) -> None:
        """Should not flag panels with hide_title=True."""
        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard_with_hidden_title, {})

        assert len(violations) == 0
