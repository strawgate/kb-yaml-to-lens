"""Pytest fixtures for dashboard lint tests."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.filters import PhraseFilter
from dashboard_compiler.panels.charts.config import ESQLMetricPanelConfig, ESQLPanel, LensMetricPanelConfig, LensPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_compiler.panels.charts.lens.dimensions.config import LensTermsDimension
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Size
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.markdown.config import MarkdownPanelConfig


@pytest.fixture
def dashboard_with_markdown_header() -> Dashboard:
    """Create a dashboard with a markdown panel containing a header."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            MarkdownPanel(
                title='Navigation',
                markdown=MarkdownPanelConfig(content='# Welcome\n\nThis is a test.'),
                size=Size(w=24, h=2),  # Too small for header
            ),
        ],
    )


@pytest.fixture
def dashboard_with_good_markdown() -> Dashboard:
    """Create a dashboard with a properly sized markdown panel."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            MarkdownPanel(
                title='Navigation',
                markdown=MarkdownPanelConfig(content='# Welcome\n\nThis is a test.'),
                size=Size(w=24, h=4),  # Good height
            ),
        ],
    )


@pytest.fixture
def dashboard_without_dataset_filter() -> Dashboard:
    """Create a dashboard without a dataset filter."""
    return Dashboard(
        name='Test Dashboard',
        filters=[],
        panels=[],
    )


@pytest.fixture
def dashboard_with_dataset_filter() -> Dashboard:
    """Create a dashboard with a dataset filter."""
    return Dashboard(
        name='Test Dashboard',
        filters=[
            PhraseFilter(field='data_stream.dataset', equals='test'),
        ],
        panels=[],
    )


@pytest.fixture
def dashboard_with_esql_no_where() -> Dashboard:
    """Create a dashboard with an ES|QL panel without WHERE clause."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Request Count',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_esql_where() -> Dashboard:
    """Create a dashboard with an ES|QL panel with WHERE clause."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Request Count',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | WHERE status == 200 | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_redundant_label() -> Dashboard:
    """Create a dashboard with a metric panel where label matches title."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Total Requests',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(
                        aggregation='count',
                        label='Total Requests',  # Same as title
                    ),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_hidden_title() -> Dashboard:
    """Create a dashboard with a metric panel with hide_title=True."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Total Requests',
                hide_title=True,
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(
                        aggregation='count',
                        label='Total Requests',  # Same as title but hidden
                    ),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_dimension_no_label() -> Dashboard:
    """Create a dashboard with a dimension without a label."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Requests by Host',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                    breakdown=LensTermsDimension(
                        field='host.name',
                        # No label set
                    ),
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_dimension_label() -> Dashboard:
    """Create a dashboard with a dimension with a label."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Requests by Host',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                    breakdown=LensTermsDimension(
                        field='host.name',
                        label='Host Name',
                    ),
                ),
            ),
        ],
    )
