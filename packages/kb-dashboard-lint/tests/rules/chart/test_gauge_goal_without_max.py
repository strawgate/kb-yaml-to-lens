"""Tests for GaugeGoalWithoutMaxRule."""

from dashboard_lint.rules.chart import GaugeGoalWithoutMaxRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensGaugePanelConfig, LensPanel
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric, LensStaticValue
from kb_dashboard_core.panels.config import Size


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
