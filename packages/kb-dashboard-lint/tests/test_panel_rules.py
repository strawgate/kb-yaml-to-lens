"""Tests for panel sizing and layout rules."""

from __future__ import annotations

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Size
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.markdown.config import MarkdownPanelConfig
from dashboard_lint.rules.panel_rules import (
    PanelDescriptionRecommendedRule,
    PanelHeightForContentRule,
    PanelMinWidthRule,
)
from dashboard_lint.types import Severity


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


class TestPanelHeightForContentRule:
    """Tests for PanelHeightForContentRule."""

    def test_detects_short_datatable(self) -> None:
        """Should detect datatables with insufficient height."""
        from dashboard_compiler.panels.charts.config import LensDatatablePanelConfig

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
        from dashboard_compiler.panels.charts.config import LensDatatablePanelConfig

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


class TestPanelDescriptionRecommendedRule:
    """Tests for PanelDescriptionRecommendedRule."""

    def test_detects_missing_description(self) -> None:
        """Should detect panels without descriptions."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Undocumented Panel',
                    size=Size(w=24, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelDescriptionRecommendedRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'panel-description-recommended'
        assert violations[0].severity == Severity.INFO
        assert 'description' in violations[0].message

    def test_passes_with_description(self) -> None:
        """Should not flag panels with descriptions."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Documented Panel',
                    description='This panel shows the count of requests.',
                    size=Size(w=24, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelDescriptionRecommendedRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_skips_markdown_panels(self) -> None:
        """Should not flag markdown panels (they are self-describing)."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Documentation',
                    size=Size(w=24, h=5),
                    markdown=MarkdownPanelConfig(content='# Welcome'),
                ),
            ],
        )

        rule = PanelDescriptionRecommendedRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_skips_panels_without_title(self) -> None:
        """Should not flag panels without titles."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='',  # Empty title
                    size=Size(w=24, h=5),
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelDescriptionRecommendedRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0
