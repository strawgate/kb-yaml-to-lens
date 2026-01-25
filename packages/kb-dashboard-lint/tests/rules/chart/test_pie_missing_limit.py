"""Tests for PieMissingLimitRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLPanel, ESQLPiePanelConfig, LensPanel, LensPiePanelConfig
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimension, ESQLMetric
from dashboard_compiler.panels.charts.lens.dimensions.config import LensTermsDimension
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_lint.rules.chart import PieMissingLimitRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_lens_pie_no_size() -> Dashboard:
    """Create a dashboard with Lens pie chart without explicit size."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Events by Status',
                lens=LensPiePanelConfig(
                    type='pie',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[
                        LensTermsDimension(field='status'),  # No size set
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_lens_pie_good_size() -> Dashboard:
    """Create a dashboard with Lens pie chart with good size."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Events by Status',
                lens=LensPiePanelConfig(
                    type='pie',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[
                        LensTermsDimension(field='status', size=5),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_lens_pie_excessive_size() -> Dashboard:
    """Create a dashboard with Lens pie chart with excessive size."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Events by Status',
                lens=LensPiePanelConfig(
                    type='pie',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[
                        LensTermsDimension(field='status', size=20),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_esql_pie_no_limit() -> Dashboard:
    """Create a dashboard with ESQL pie chart without LIMIT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events by Status',
                esql=ESQLPiePanelConfig(
                    type='pie',
                    query='FROM logs-* | STATS count = COUNT(*) BY status',
                    metrics=[ESQLMetric(field='count')],
                    dimensions=[ESQLDimension(field='status')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_esql_pie_good_limit() -> Dashboard:
    """Create a dashboard with ESQL pie chart with good LIMIT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events by Status',
                esql=ESQLPiePanelConfig(
                    type='pie',
                    query='FROM logs-* | STATS count = COUNT(*) BY status | LIMIT 5',
                    metrics=[ESQLMetric(field='count')],
                    dimensions=[ESQLDimension(field='status')],
                ),
            ),
        ],
    )


class TestPieMissingLimitRule:
    """Tests for PieMissingLimitRule."""

    def test_detects_lens_pie_no_size(self, dashboard_with_lens_pie_no_size: Dashboard) -> None:
        """Should detect Lens pie chart without explicit size."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_lens_pie_no_size, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'pie-missing-limit'
        assert 'size' in violations[0].message.lower()
        assert violations[0].severity == Severity.INFO

    def test_passes_lens_pie_good_size(self, dashboard_with_lens_pie_good_size: Dashboard) -> None:
        """Should not flag Lens pie chart with good size."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_lens_pie_good_size, {})

        assert len(violations) == 0

    def test_detects_lens_pie_excessive_size(self, dashboard_with_lens_pie_excessive_size: Dashboard) -> None:
        """Should detect Lens pie chart with excessive size."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_lens_pie_excessive_size, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'pie-missing-limit'
        assert '20' in violations[0].message

    def test_detects_esql_pie_no_limit(self, dashboard_with_esql_pie_no_limit: Dashboard) -> None:
        """Should detect ESQL pie chart without LIMIT."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_esql_pie_no_limit, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'pie-missing-limit'
        assert 'LIMIT' in violations[0].message

    def test_passes_esql_pie_good_limit(self, dashboard_with_esql_pie_good_limit: Dashboard) -> None:
        """Should not flag ESQL pie chart with good LIMIT."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_esql_pie_good_limit, {})

        assert len(violations) == 0

    def test_custom_recommended_max(self, dashboard_with_lens_pie_good_size: Dashboard) -> None:
        """Should use custom recommended_max when provided."""
        rule = PieMissingLimitRule()
        violations = rule.check(dashboard_with_lens_pie_good_size, {'recommended_max': 3})

        # size=5 should now be flagged since max is 3
        assert len(violations) == 1
        assert '5' in violations[0].message
        assert '3' in violations[0].message
