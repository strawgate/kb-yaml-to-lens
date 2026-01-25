"""Tests for MarkdownAtTopRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.markdown.config import MarkdownPanelConfig
from dashboard_lint.rules.dashboard import MarkdownAtTopRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_markdown_at_top() -> Dashboard:
    """Create a dashboard with markdown navigation at top."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            MarkdownPanel(
                title='Navigation',
                markdown=MarkdownPanelConfig(content='# Welcome\n\n[Link to other dashboard](/app/dashboard/123)'),
                size=Size(w=48, h=3),
                position=Position(x=0, y=0),
            ),
            LensPanel(
                title='Metric',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
                position=Position(x=0, y=3),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_markdown_not_at_top() -> Dashboard:
    """Create a dashboard with markdown navigation not at top."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Metric',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
                position=Position(x=0, y=0),
            ),
            MarkdownPanel(
                title='Navigation',
                markdown=MarkdownPanelConfig(content='# Welcome\n\n[Link](/app/dashboard/123)'),
                size=Size(w=48, h=3),
                position=Position(x=0, y=5),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_plain_markdown() -> Dashboard:
    """Create a dashboard with plain markdown (no navigation content)."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Metric',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
                position=Position(x=0, y=0),
            ),
            MarkdownPanel(
                title='Description',
                markdown=MarkdownPanelConfig(content='This is just a description.'),
                size=Size(w=48, h=3),
                position=Position(x=0, y=5),
            ),
        ],
    )


class TestMarkdownAtTopRule:
    """Tests for MarkdownAtTopRule."""

    def test_passes_markdown_at_top(self, dashboard_with_markdown_at_top: Dashboard) -> None:
        """Should not flag markdown navigation at top."""
        rule = MarkdownAtTopRule()
        violations = rule.check(dashboard_with_markdown_at_top, {})

        assert len(violations) == 0

    def test_detects_markdown_not_at_top(self, dashboard_with_markdown_not_at_top: Dashboard) -> None:
        """Should detect markdown navigation not at top."""
        rule = MarkdownAtTopRule()
        violations = rule.check(dashboard_with_markdown_not_at_top, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'markdown-at-top'
        assert 'y=' in violations[0].message
        assert violations[0].severity == Severity.INFO

    def test_ignores_plain_markdown(self, dashboard_with_plain_markdown: Dashboard) -> None:
        """Should not flag plain markdown without navigation content."""
        rule = MarkdownAtTopRule()
        violations = rule.check(dashboard_with_plain_markdown, {})

        assert len(violations) == 0
