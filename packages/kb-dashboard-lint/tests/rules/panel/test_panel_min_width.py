"""Tests for PanelMinWidthRule."""

from dashboard_lint.rules.panel import PanelMinWidthRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensMetricPanelConfig, LensPanel
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size


class TestPanelMinWidthRule:
    """Tests for PanelMinWidthRule."""

    def test_detects_narrow_panel(self) -> None:
        """Should detect panels with width below minimum."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Panel',
                    size=Size(w=4, h=5),  # Width 4 is below default min of 6
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'panel-min-width'
        assert violations[0].severity == Severity.WARNING
        assert 'width 4' in violations[0].message

    def test_passes_adequate_width(self) -> None:
        """Should not flag panels with adequate width."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Wide Panel',
                    size=Size(w=12, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_custom_min_width_option(self) -> None:
        """Should respect custom min_width option."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Panel',
                    size=Size(w=8, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()

        # With min_width=6, should pass
        violations = rule.check(dashboard, {'min_width': 6})
        assert len(violations) == 0

        # With min_width=12, should fail
        violations = rule.check(dashboard, {'min_width': 12})
        assert len(violations) == 1

    def test_semantic_width_half_passes(self) -> None:
        """Should correctly handle semantic width 'half' (24 grid units)."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Half Width Panel',
                    size=Size(w='half', h=5),  # 'half' resolves to 24
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_semantic_width_eighth_fails(self) -> None:
        """Should correctly detect semantic width 'eighth' as too narrow."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Eighth Width Panel',
                    size=Size(w='eighth', h=5),  # 'eighth' resolves to 6
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()
        # With min_width=8, 'eighth' (6) should fail
        violations = rule.check(dashboard, {'min_width': 8})

        assert len(violations) == 1
        assert 'width 6' in violations[0].message

    def test_width_at_boundary_passes(self) -> None:
        """Width exactly at min_width should pass (uses >= comparison)."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Boundary Panel',
                    size=Size(w=6, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelMinWidthRule()
        violations = rule.check(dashboard, {'min_width': 6})

        assert len(violations) == 0
