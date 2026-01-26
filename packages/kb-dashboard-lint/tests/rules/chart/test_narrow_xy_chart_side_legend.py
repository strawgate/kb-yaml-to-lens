"""Tests for narrow-xy-chart-side-legend rule."""

from dashboard_lint.rules.chart import NarrowXYChartSideLegendRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import (
    ESQLAreaPanelConfig,
    ESQLBarPanelConfig,
    ESQLLinePanelConfig,
    ESQLPanel,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensLinePanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimension
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDateHistogramDimension
from kb_dashboard_core.panels.charts.xy.config import XYLegend
from kb_dashboard_core.panels.charts.xy.metrics import XYESQLMetric, XYLensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size


class TestNarrowXYChartSideLegendRule:
    """Tests for NarrowXYChartSideLegendRule."""

    def test_detects_narrow_line_chart_default_legend(self) -> None:
        """Should detect narrow line chart with default (right) legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Line Chart',
                    size=Size(w=16, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'narrow-xy-chart-side-legend'
        assert 'width 16' in violations[0].message
        assert 'bottom' in violations[0].message

    def test_detects_narrow_bar_chart_explicit_right_legend(self) -> None:
        """Should detect narrow bar chart with explicit right legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Bar Chart',
                    size=Size(w=12, h=10),
                    lens=LensBarPanelConfig(
                        type='bar',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(position='right'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert "position: 'right'" in violations[0].message

    def test_detects_narrow_area_chart_left_legend(self) -> None:
        """Should detect narrow area chart with left legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Area Chart',
                    size=Size(w=16, h=10),
                    lens=LensAreaPanelConfig(
                        type='area',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(position='left'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert "position: 'left'" in violations[0].message

    def test_passes_narrow_chart_with_bottom_legend(self) -> None:
        """Should not flag narrow chart with bottom legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Chart Bottom Legend',
                    size=Size(w=16, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(position='bottom'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_narrow_chart_with_top_legend(self) -> None:
        """Should not flag narrow chart with top legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Chart Top Legend',
                    size=Size(w=16, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(position='top'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_wide_chart_with_side_legend(self) -> None:
        """Should not flag wide chart with side legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Wide Chart',
                    size=Size(w=24, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(position='right'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_narrow_chart_with_hidden_legend(self) -> None:
        """Should not flag narrow chart with hidden legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Chart Hidden Legend',
                    size=Size(w=16, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                        legend=XYLegend(visible='hide'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_respects_max_width_option(self) -> None:
        """Should respect custom max_width option."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Chart',
                    size=Size(w=20, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        # Default max_width=16 should pass for width 20
        assert len(rule.check(dashboard, {})) == 0
        # Custom max_width=24 should flag width 20
        assert len(rule.check(dashboard, {'max_width': 24})) == 1

    def test_boundary_exact_max_width(self) -> None:
        """Should flag chart with width exactly at max_width threshold."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Boundary Chart',
                    size=Size(w=20, h=10),
                    lens=LensLinePanelConfig(
                        type='line',
                        data_view='metrics-*',
                        dimension=LensDateHistogramDimension(type='date_histogram', field='@timestamp'),
                        metrics=[XYLensCountAggregatedMetric(aggregation='count')],
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        # Width 20 == max_width 20: rule uses width > max_width, so 20 > 20 is false
        # meaning width <= max_width triggers the check, and default legend should be flagged
        violations = rule.check(dashboard, {'max_width': 20})
        assert len(violations) == 1
        assert 'width 20' in violations[0].message

    def test_detects_esql_line_chart(self) -> None:
        """Should detect narrow ESQL line chart with side legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                ESQLPanel(
                    title='ESQL Line Chart',
                    size=Size(w=16, h=10),
                    esql=ESQLLinePanelConfig(
                        type='line',
                        query='FROM metrics-* | STATS count=COUNT(*) BY time=BUCKET(@timestamp, 20, ?_tstart, ?_tend)',
                        dimension=ESQLDimension(field='time'),
                        metrics=[XYESQLMetric(field='count')],
                        legend=XYLegend(position='right'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1

    def test_detects_esql_bar_chart(self) -> None:
        """Should detect narrow ESQL bar chart with default legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                ESQLPanel(
                    title='ESQL Bar Chart',
                    size=Size(w=16, h=10),
                    esql=ESQLBarPanelConfig(
                        type='bar',
                        query='FROM logs-* | STATS count=COUNT(*) BY status',
                        dimension=ESQLDimension(field='status'),
                        metrics=[XYESQLMetric(field='count')],
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1

    def test_detects_esql_area_chart(self) -> None:
        """Should detect narrow ESQL area chart with side legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                ESQLPanel(
                    title='ESQL Area Chart',
                    size=Size(w=12, h=10),
                    esql=ESQLAreaPanelConfig(
                        type='area',
                        query='FROM metrics-* | STATS avg_cpu=AVG(cpu) BY time=BUCKET(@timestamp, 20, ?_tstart, ?_tend)',
                        dimension=ESQLDimension(field='time'),
                        metrics=[XYESQLMetric(field='avg_cpu')],
                        legend=XYLegend(position='left', visible='show'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1

    def test_passes_esql_chart_with_bottom_legend(self) -> None:
        """Should not flag ESQL chart with bottom legend."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                ESQLPanel(
                    title='ESQL Chart Bottom Legend',
                    size=Size(w=16, h=10),
                    esql=ESQLLinePanelConfig(
                        type='line',
                        query='FROM metrics-* | STATS count=COUNT(*) BY time=BUCKET(@timestamp, 20, ?_tstart, ?_tend)',
                        dimension=ESQLDimension(field='time'),
                        metrics=[XYESQLMetric(field='count')],
                        legend=XYLegend(position='bottom'),
                    ),
                ),
            ],
        )

        rule = NarrowXYChartSideLegendRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0
