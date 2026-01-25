"""Tests for ESQLDimensionMissingLabelRule."""

import pytest

from dashboard_lint.rules.chart import ESQLDimensionMissingLabelRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLDatatablePanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimension, ESQLMetric


@pytest.fixture
def dashboard_esql_dimension_no_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with dimensions without labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*) BY server_name',
                    dimensions=[
                        ESQLDimension(field='server_name'),  # No label
                        ESQLDimension(field='server_port'),  # No label
                    ],
                    metrics=[
                        ESQLMetric(field='count', label='Count'),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_esql_dimension_with_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with dimensions with labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*) BY server_name',
                    dimensions=[
                        ESQLDimension(field='server_name', label='Server Name'),
                        ESQLDimension(field='server_port', label='Port'),
                    ],
                    metrics=[
                        ESQLMetric(field='count', label='Count'),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_esql_dimension_empty_label() -> Dashboard:
    """Create a dashboard with an ES|QL datatable with dimensions with empty labels."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Server Summary',
                esql=ESQLDatatablePanelConfig(
                    type='datatable',
                    query='FROM metrics-* | STATS count = COUNT(*) BY server_name',
                    dimensions=[
                        ESQLDimension(field='server_name', label=''),  # Empty label
                    ],
                    metrics=[
                        ESQLMetric(field='count', label='Count'),
                    ],
                ),
            ),
        ],
    )


class TestESQLDimensionMissingLabelRule:
    """Tests for ESQLDimensionMissingLabelRule."""

    def test_detects_missing_dimension_label(self, dashboard_esql_dimension_no_label: Dashboard) -> None:
        """Should detect ES|QL datatable dimensions without labels."""
        rule = ESQLDimensionMissingLabelRule()
        violations = rule.check(dashboard_esql_dimension_no_label, {})

        assert len(violations) == 2
        assert violations[0].rule_id == 'esql-dimension-missing-label'
        assert 'server_name' in violations[0].message
        assert 'server_port' in violations[1].message

    def test_passes_with_dimension_label(self, dashboard_esql_dimension_with_label: Dashboard) -> None:
        """Should not flag ES|QL datatable dimensions with labels."""
        rule = ESQLDimensionMissingLabelRule()
        violations = rule.check(dashboard_esql_dimension_with_label, {})

        assert len(violations) == 0

    def test_detects_empty_label(self, dashboard_esql_dimension_empty_label: Dashboard) -> None:
        """Should detect ES|QL datatable dimensions with empty labels."""
        rule = ESQLDimensionMissingLabelRule()
        violations = rule.check(dashboard_esql_dimension_empty_label, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-dimension-missing-label'
        assert 'server_name' in violations[0].message
