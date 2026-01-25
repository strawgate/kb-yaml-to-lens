"""Tests for ESQLMetricMissingLabelRule."""

import pytest

from dashboard_lint.rules.chart import ESQLMetricMissingLabelRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLDatatablePanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimension, ESQLMetric, ESQLStaticValue


@pytest.fixture
def dashboard_esql_metric_no_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with metrics without labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*), avg_cpu = AVG(cpu)',
                    dimensions=[
                        ESQLDimension(field='server_name', label='Server Name'),
                    ],
                    metrics=[
                        ESQLMetric(field='count'),  # No label
                        ESQLMetric(field='avg_cpu'),  # No label
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_esql_metric_with_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with metrics with labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*), avg_cpu = AVG(cpu)',
                    dimensions=[
                        ESQLDimension(field='server_name', label='Server Name'),
                    ],
                    metrics=[
                        ESQLMetric(field='count', label='Request Count'),
                        ESQLMetric(field='avg_cpu', label='Avg CPU'),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_esql_metric_empty_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with metrics with empty labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*)',
                    dimensions=[
                        ESQLDimension(field='server_name', label='Server Name'),
                    ],
                    metrics=[
                        ESQLMetric(field='count', label=''),  # Empty label
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_esql_static_value() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with static value metrics."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*)',
                    dimensions=[
                        ESQLDimension(field='server_name', label='Server Name'),
                    ],
                    metrics=[
                        ESQLStaticValue(value=100),  # Static values don't need labels
                    ],
                ),
            ),
        ],
    )


class TestESQLMetricMissingLabelRule:
    """Tests for ESQLMetricMissingLabelRule."""

    def test_detects_missing_metric_label(self, dashboard_esql_metric_no_label: Dashboard) -> None:
        """Should detect ES|QL datatable metrics without labels."""
        rule = ESQLMetricMissingLabelRule()
        violations = rule.check(dashboard_esql_metric_no_label, {})

        assert len(violations) == 2
        assert violations[0].rule_id == 'esql-metric-missing-label'
        assert 'count' in violations[0].message
        assert 'avg_cpu' in violations[1].message

    def test_passes_with_metric_label(self, dashboard_esql_metric_with_label: Dashboard) -> None:
        """Should not flag ES|QL datatable metrics with labels."""
        rule = ESQLMetricMissingLabelRule()
        violations = rule.check(dashboard_esql_metric_with_label, {})

        assert len(violations) == 0

    def test_detects_empty_label(self, dashboard_esql_metric_empty_label: Dashboard) -> None:
        """Should detect ES|QL datatable metrics with empty labels."""
        rule = ESQLMetricMissingLabelRule()
        violations = rule.check(dashboard_esql_metric_empty_label, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-metric-missing-label'
        assert 'count' in violations[0].message

    def test_ignores_static_values(self, dashboard_esql_static_value: Dashboard) -> None:
        """Should not flag static value metrics (they don't need labels)."""
        rule = ESQLMetricMissingLabelRule()
        violations = rule.check(dashboard_esql_static_value, {})

        assert len(violations) == 0
