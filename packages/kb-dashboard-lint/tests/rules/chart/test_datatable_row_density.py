"""Tests for DatatableRowDensityRule."""

from dashboard_lint.rules.chart import DatatableRowDensityRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import LensDatatablePanelConfig, LensPanel
from kb_dashboard_core.panels.charts.datatable.config import (
    DatatableAppearance,
    DatatableDensityEnum,
)
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensTermsDimension
from kb_dashboard_core.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from kb_dashboard_core.panels.config import Size


class TestDatatableRowDensityRule:
    """Tests for DatatableRowDensityRule."""

    def test_detects_many_columns_without_compact(self) -> None:
        """Should detect datatables with many columns that don't use compact density."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Wide Table',
                    size=Size(w=48, h=10),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[],
                        dimensions=[
                            LensTermsDimension(id='dim1', field='field1', type='values'),
                            LensTermsDimension(id='dim2', field='field2', type='values'),
                            LensTermsDimension(id='dim3', field='field3', type='values'),
                            LensTermsDimension(id='dim4', field='field4', type='values'),
                            LensTermsDimension(id='dim5', field='field5', type='values'),
                        ],
                    ),
                ),
            ],
        )

        rule = DatatableRowDensityRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'datatable-row-density'
        assert '5 columns' in violations[0].message
        assert 'compact' in violations[0].message

    def test_passes_many_columns_with_compact(self) -> None:
        """Should not flag datatables with many columns using compact density."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Compact Wide Table',
                    size=Size(w=48, h=10),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[],
                        dimensions=[
                            LensTermsDimension(id='dim1', field='field1', type='values'),
                            LensTermsDimension(id='dim2', field='field2', type='values'),
                            LensTermsDimension(id='dim3', field='field3', type='values'),
                            LensTermsDimension(id='dim4', field='field4', type='values'),
                            LensTermsDimension(id='dim5', field='field5', type='values'),
                        ],
                        appearance=DatatableAppearance(
                            density=DatatableDensityEnum.COMPACT,
                        ),
                    ),
                ),
            ],
        )

        rule = DatatableRowDensityRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_few_columns(self) -> None:
        """Should not flag datatables with few columns."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Narrow Table',
                    size=Size(w=24, h=8),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[
                            LensTermsDimension(id='dim1', field='field1', type='values'),
                            LensTermsDimension(id='dim2', field='field2', type='values'),
                        ],
                    ),
                ),
            ],
        )

        rule = DatatableRowDensityRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_passes_no_columns_config(self) -> None:
        """Should not flag datatables without explicit column configuration."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Auto Columns Table',
                    size=Size(w=24, h=8),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[
                            LensTermsDimension(id='dim1', field='field1', type='values'),
                        ],
                    ),
                ),
            ],
        )

        rule = DatatableRowDensityRule()
        violations = rule.check(dashboard, {})

        assert len(violations) == 0

    def test_custom_min_columns_threshold(self) -> None:
        """Should respect custom min_columns option."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                LensPanel(
                    title='Table With 3 Columns',
                    size=Size(w=24, h=8),
                    lens=LensDatatablePanelConfig(
                        type='datatable',
                        data_view='logs-*',
                        metrics=[LensCountAggregatedMetric(aggregation='count')],
                        dimensions=[
                            LensTermsDimension(id='dim1', field='field1', type='values'),
                            LensTermsDimension(id='dim2', field='field2', type='values'),
                        ],
                    ),
                ),
            ],
        )

        rule = DatatableRowDensityRule()
        violations = rule.check(dashboard, {'min_columns': 3})

        assert len(violations) == 1
        assert '3 columns' in violations[0].message
