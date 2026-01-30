"""Tests for PieChartDimensionCountRule."""

from dashboard_lint.rules.chart import PieChartDimensionCountRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensPanel, LensPiePanelConfig
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensTermsDimension
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size


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
