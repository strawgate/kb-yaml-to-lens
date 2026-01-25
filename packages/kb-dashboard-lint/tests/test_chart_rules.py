"""Tests for chart-specific lint rules."""

from __future__ import annotations

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import (
    LensGaugePanelConfig,
    LensMetricPanelConfig,
    LensPanel,
    LensPiePanelConfig,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import LensTermsDimension
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric, LensStaticValue
from dashboard_compiler.panels.config import Size
from dashboard_lint.rules.chart_rules import (
    GaugeGoalWithoutMaxRule,
    MetricMultipleMetricsWidthRule,
    PieChartDimensionCountRule,
)
from dashboard_lint.types import Severity


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


class TestGaugeGoalWithoutMaxRule:
    """Tests for GaugeGoalWithoutMaxRule."""

    def test_detects_goal_without_max(self) -> None:
        """Should detect gauges with goal but no maximum."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Gauge Without Max',
                    size=Size(w=12, h=5),
                    lens=LensGaugePanelConfig(
                        type='gauge',
                        data_view='logs-*',
                        metric=LensCountAggregatedMetric(aggregation='count'),
                        goal=LensStaticValue(value=100),
                        # No maximum defined
                    ),
                ),
            ],
        )

        rule = GaugeGoalWithoutMaxRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'gauge-goal-without-max'
        assert 'goal' in violations[0].message
        assert 'maximum' in violations[0].message

    def test_passes_goal_with_max(self) -> None:
        """Should not flag gauges with both goal and maximum."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Gauge With Max',
                    size=Size(w=12, h=5),
                    lens=LensGaugePanelConfig(
                        type='gauge',
                        data_view='logs-*',
                        metric=LensCountAggregatedMetric(aggregation='count'),
                        goal=LensStaticValue(value=80),
                        maximum=LensStaticValue(value=100),
                    ),
                ),
            ],
        )

        rule = GaugeGoalWithoutMaxRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_no_goal(self) -> None:
        """Should not flag gauges without goals."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Gauge Without Goal',
                    size=Size(w=12, h=5),
                    lens=LensGaugePanelConfig(
                        type='gauge',
                        data_view='logs-*',
                        metric=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = GaugeGoalWithoutMaxRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0


class TestPieChartDimensionCountRule:
    """Tests for PieChartDimensionCountRule."""

    def test_detects_multi_dimension_pie(self) -> None:
        """Should detect pie charts with multiple dimensions."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Complex Pie',
                    size=Size(w=12, h=8),
                    lens=LensPiePanelConfig(
                        type='pie',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[
                            LensTermsDimension(field='host.name'),
                            LensTermsDimension(field='service.name'),
                        ],
                    ),
                ),
            ],
        )

        rule = PieChartDimensionCountRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'pie-chart-dimension-count'
        assert violations[0].severity == Severity.INFO
        assert '2 dimensions' in violations[0].message

    def test_passes_single_dimension_pie(self) -> None:
        """Should not flag pie charts with single dimension."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Simple Pie',
                    size=Size(w=12, h=8),
                    lens=LensPiePanelConfig(
                        type='pie',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                ),
            ],
        )

        rule = PieChartDimensionCountRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_custom_max_dimensions_option(self) -> None:
        """Should respect custom max_dimensions option."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Three Dimension Pie',
                    size=Size(w=12, h=8),
                    lens=LensPiePanelConfig(
                        type='pie',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[
                            LensTermsDimension(field='host.name'),
                            LensTermsDimension(field='service.name'),
                            LensTermsDimension(field='log.level'),
                        ],
                    ),
                ),
            ],
        )

        rule = PieChartDimensionCountRule()

        # With max_dimensions=2, should still flag (3 > 2)
        violations = rule.check(dashboard, {'max_dimensions': 2})
        assert len(violations) == 1

        # With max_dimensions=3, should pass
        violations = rule.check(dashboard, {'max_dimensions': 3})
        assert len(violations) == 0
