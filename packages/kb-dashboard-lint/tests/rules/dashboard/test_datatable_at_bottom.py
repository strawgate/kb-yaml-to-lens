"""Tests for DatatableAtBottomRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import (
    LensDatatablePanelConfig,
    LensMetricPanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import LensTermsDimension
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.config import Position
from dashboard_lint.rules.dashboard import DatatableAtBottomRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_datatable_at_bottom() -> Dashboard:
    """Create a dashboard with datatable at bottom."""
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
            LensPanel(
                title='Data Table',
                lens=LensDatatablePanelConfig(
                    type='datatable',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[LensTermsDimension(field='host.name')],
                ),
                position=Position(x=0, y=10),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_datatable_above_other() -> Dashboard:
    """Create a dashboard with datatable above other visualizations."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Data Table',
                lens=LensDatatablePanelConfig(
                    type='datatable',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[LensTermsDimension(field='host.name')],
                ),
                position=Position(x=0, y=0),
            ),
            LensPanel(
                title='Metric',
                lens=LensMetricPanelConfig(
                    type='metric',
                    data_view='logs-*',
                    primary=LensCountAggregatedMetric(aggregation='count'),
                ),
                position=Position(x=0, y=10),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_only_datatable() -> Dashboard:
    """Create a dashboard with only a datatable."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            LensPanel(
                title='Data Table',
                lens=LensDatatablePanelConfig(
                    type='datatable',
                    data_view='logs-*',
                    metrics=[LensCountAggregatedMetric(aggregation='count')],
                    dimensions=[LensTermsDimension(field='host.name')],
                ),
                position=Position(x=0, y=0),
            ),
        ],
    )


class TestDatatableAtBottomRule:
    """Tests for DatatableAtBottomRule."""

    def test_passes_datatable_at_bottom(self, dashboard_with_datatable_at_bottom: Dashboard) -> None:
        """Should not flag datatables at bottom."""
        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard_with_datatable_at_bottom, {})

        assert len(violations) == 0

    def test_detects_datatable_above_other(self, dashboard_with_datatable_above_other: Dashboard) -> None:
        """Should detect datatables above other visualizations."""
        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard_with_datatable_above_other, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'datatable-at-bottom'
        assert 'y=' in violations[0].message
        assert violations[0].severity == Severity.INFO

    def test_passes_only_datatable(self, dashboard_with_only_datatable: Dashboard) -> None:
        """Should not flag when datatable is the only panel."""
        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard_with_only_datatable, {})

        assert len(violations) == 0

    def test_detects_only_datatable_above_when_multiple(self) -> None:
        """Should flag only the datatable above other visualizations when multiple exist."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Data Table Above',
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                    position=Position(x=0, y=0),
                ),
                LensPanel(
                    title='Metric',
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                    position=Position(x=0, y=10),
                ),
                LensPanel(
                    title='Data Table Below',
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                    position=Position(x=0, y=20),
                ),
            ],
        )

        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'datatable-at-bottom'
        assert 'Data Table Above' in violations[0].message or 'y=0' in violations[0].message

    def test_passes_datatable_same_y_as_non_datatable(self) -> None:
        """Should not flag datatable at same y-coordinate as non-datatable."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Data Table',
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                    position=Position(x=0, y=10),
                ),
                LensPanel(
                    title='Metric',
                    lens=LensMetricPanelConfig(
                        type='metric',
                        data_view='logs-*',
                        primary=LensCountAggregatedMetric(aggregation='count'),
                    ),
                    position=Position(x=24, y=10),
                ),
            ],
        )

        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_multiple_datatables_only(self) -> None:
        """Should not flag when dashboard has only datatables (no other visualizations)."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Data Table 1',
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                    position=Position(x=0, y=0),
                ),
                LensPanel(
                    title='Data Table 2',
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[LensTermsDimension(field='host.name')],
                    ),
                    position=Position(x=0, y=10),
                ),
            ],
        )

        rule = DatatableAtBottomRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0
