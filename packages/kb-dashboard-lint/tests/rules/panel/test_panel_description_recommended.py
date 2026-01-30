"""Tests for PanelDescriptionRecommendedRule."""

from dashboard_lint.rules.panel import PanelDescriptionRecommendedRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensMetricPanelConfig, LensPanel
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig


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
