"""Tests for PanelTitleRedundantPrefixRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_lint.rules.panel import PanelTitleRedundantPrefixRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_redundant_prefix() -> Dashboard:
    """Create a dashboard with redundant panel title prefix."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Chart of CPU Usage',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_good_title() -> Dashboard:
    """Create a dashboard with good panel title."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='CPU Usage',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_no_title() -> Dashboard:
    """Create a dashboard with panel without title."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
            ),
        ],
    )


class TestPanelTitleRedundantPrefixRule:
    """Tests for PanelTitleRedundantPrefixRule."""

    def test_detects_redundant_prefix(self, dashboard_with_redundant_prefix: Dashboard) -> None:
        """Should detect redundant prefixes like 'Chart of'."""
        rule = PanelTitleRedundantPrefixRule()
        violations = rule.check(dashboard_with_redundant_prefix, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'panel-title-redundant-prefix'
        assert 'Chart of' in violations[0].message
        assert 'CPU Usage' in violations[0].message  # Suggested fix
        assert violations[0].severity == Severity.INFO

    def test_passes_good_title(self, dashboard_with_good_title: Dashboard) -> None:
        """Should not flag titles without redundant prefixes."""
        rule = PanelTitleRedundantPrefixRule()
        violations = rule.check(dashboard_with_good_title, {})

        assert len(violations) == 0

    def test_passes_no_title(self, dashboard_with_no_title: Dashboard) -> None:
        """Should not flag panels without titles."""
        rule = PanelTitleRedundantPrefixRule()
        violations = rule.check(dashboard_with_no_title, {})

        assert len(violations) == 0

    def test_case_insensitive(self) -> None:
        """Should detect prefixes case-insensitively."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='GRAPH OF Memory Usage',
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                ),
            ],
        )

        rule = PanelTitleRedundantPrefixRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert 'Graph of' in violations[0].message

    def test_custom_prefixes(self, dashboard_with_good_title: Dashboard) -> None:
        """Should use custom prefix list when provided."""
        rule = PanelTitleRedundantPrefixRule()
        violations = rule.check(dashboard_with_good_title, {'prefixes': ['CPU']})

        assert len(violations) == 1
        assert 'CPU' in violations[0].message
