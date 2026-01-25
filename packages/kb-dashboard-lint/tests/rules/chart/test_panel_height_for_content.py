"""Tests for PanelHeightForContentRule."""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensDatatablePanelConfig, LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Size
from dashboard_lint.rules.chart import PanelHeightForContentRule


class TestPanelHeightForContentRule:
    """Tests for PanelHeightForContentRule."""

    def test_detects_short_datatable(self) -> None:
        """Should detect datatables with insufficient height."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Short Table',
                    size=Size(w=24, h=3),  # Too short for datatable (needs 5)
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                    ),
                ),
            ],
        )

        rule = PanelHeightForContentRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'panel-height-for-content'
        assert 'datatable' in violations[0].message
        assert 'at least 5' in violations[0].message

    def test_passes_adequate_height(self) -> None:
        """Should not flag panels with adequate height."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Tall Table',
                    size=Size(w=24, h=8),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                    ),
                ),
            ],
        )

        rule = PanelHeightForContentRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_metric_min_height(self) -> None:
        """Should check metric panels for minimum height of 3."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Short Metric',
                    size=Size(w=24, h=2),  # Too short for metric (needs 3)
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelHeightForContentRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert 'metric' in violations[0].message
