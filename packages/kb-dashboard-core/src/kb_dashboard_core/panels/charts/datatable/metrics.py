"""Datatable metric types with nested appearance configuration."""

from kb_dashboard_core.panels.charts.datatable.appearance import DatatableMetricAppearanceMixin
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric
from kb_dashboard_core.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
    LensFormulaMetric,
    LensLastValueAggregatedMetric,
    LensOtherAggregatedMetric,
    LensPercentileAggregatedMetric,
    LensPercentileRankAggregatedMetric,
    LensSumAggregatedMetric,
)


class DatatableLensCountAggregatedMetric(LensCountAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable count metric with appearance options."""


class DatatableLensSumAggregatedMetric(LensSumAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable sum metric with appearance options."""


class DatatableLensOtherAggregatedMetric(LensOtherAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable min/max/median/average metric with appearance options."""


class DatatableLensLastValueAggregatedMetric(LensLastValueAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable last-value metric with appearance options."""


class DatatableLensPercentileRankAggregatedMetric(LensPercentileRankAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable percentile-rank metric with appearance options."""


class DatatableLensPercentileAggregatedMetric(LensPercentileAggregatedMetric, DatatableMetricAppearanceMixin):
    """Datatable percentile metric with appearance options."""


class DatatableLensFormulaMetric(LensFormulaMetric, DatatableMetricAppearanceMixin):
    """Datatable formula metric with appearance options."""


class DatatableESQLMetric(ESQLMetric, DatatableMetricAppearanceMixin):
    """Datatable ES|QL metric with appearance options."""


type LensDatatableMetricTypes = (
    DatatableLensFormulaMetric
    | DatatableLensCountAggregatedMetric
    | DatatableLensSumAggregatedMetric
    | DatatableLensOtherAggregatedMetric
    | DatatableLensLastValueAggregatedMetric
    | DatatableLensPercentileRankAggregatedMetric
    | DatatableLensPercentileAggregatedMetric
)

type ESQLDatatableMetricTypes = DatatableESQLMetric
