"""Metric chart-specific metric configurations with color options."""

from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import ColorRangeMapping, ColorThreshold
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric
from kb_dashboard_core.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
    LensFormulaMetric,
    LensLastValueAggregatedMetric,
    LensOtherAggregatedMetric,
    LensPercentileAggregatedMetric,
    LensPercentileRankAggregatedMetric,
    LensStaticValue,
    LensSumAggregatedMetric,
)
from kb_dashboard_core.shared.config import BaseCfgModel


class MetricChartColor(BaseCfgModel):
    """Color settings for metric chart metrics, including thresholds and application mode."""

    apply_to: Literal['value', 'background'] | None = Field(default=None)
    """Controls where metric colors are applied: value text or background."""

    range_type: Literal['number', 'percent'] = Field(default='number')
    """How threshold values are interpreted by Kibana."""

    range_min: float | None = Field(default=0)
    """Optional lower bound for the palette domain."""

    range_max: float | None = Field(default=None)
    """Optional upper bound for the palette domain."""

    thresholds: list[ColorThreshold] | None = Field(default=None, min_length=1)
    """Ordered threshold bands used to build color palettes."""

    def to_range_mapping(self) -> ColorRangeMapping | None:
        """Convert to ColorRangeMapping when thresholds are provided."""
        if self.thresholds is None:
            return None
        return ColorRangeMapping(
            range_type=self.range_type,
            range_min=self.range_min,
            range_max=self.range_max,
            thresholds=self.thresholds,
        )


class MetricChartColorMixin(BaseCfgModel):
    """Threshold-based color settings for metrics in metric charts."""

    color: MetricChartColor | None = Field(default=None)
    """Color range mapping and application mode for this metric."""


class MetricLensCountAggregatedMetric(LensCountAggregatedMetric, MetricChartColorMixin):
    """Metric chart count metric with color options."""


class MetricLensSumAggregatedMetric(LensSumAggregatedMetric, MetricChartColorMixin):
    """Metric chart sum metric with color options."""


class MetricLensOtherAggregatedMetric(LensOtherAggregatedMetric, MetricChartColorMixin):
    """Metric chart aggregated metric with color options."""


class MetricLensLastValueAggregatedMetric(LensLastValueAggregatedMetric, MetricChartColorMixin):
    """Metric chart last value metric with color options."""


class MetricLensPercentileRankAggregatedMetric(LensPercentileRankAggregatedMetric, MetricChartColorMixin):
    """Metric chart percentile rank metric with color options."""


class MetricLensPercentileAggregatedMetric(LensPercentileAggregatedMetric, MetricChartColorMixin):
    """Metric chart percentile metric with color options."""


class MetricLensFormulaMetric(LensFormulaMetric, MetricChartColorMixin):
    """Metric chart formula metric with color options."""


class MetricLensStaticValue(LensStaticValue, MetricChartColorMixin):
    """Metric chart static value with color options."""


class MetricESQLMetric(ESQLMetric, MetricChartColorMixin):
    """Metric chart ES|QL metric with color options."""


type LensMetricChartMetricTypes = (
    MetricLensFormulaMetric
    | MetricLensCountAggregatedMetric
    | MetricLensSumAggregatedMetric
    | MetricLensOtherAggregatedMetric
    | MetricLensLastValueAggregatedMetric
    | MetricLensPercentileRankAggregatedMetric
    | MetricLensPercentileAggregatedMetric
    | MetricLensStaticValue
)

type ESQLMetricChartMetricTypes = MetricESQLMetric
