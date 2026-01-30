"""XY chart-specific metric configurations with appearance options."""

from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric, ESQLStaticValue
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


class XYMetricAppearance(BaseCfgModel):
    """Visual appearance configuration mixin for XY chart metrics.

    Provides axis assignment and color customization for metrics in XY charts.
    These properties were previously configured in the appearance.series section
    but are now directly attached to metric definitions for a more intuitive API.
    """

    axis: Literal['left', 'right'] | None = Field(
        default=None,
        description="Which Y-axis to assign this metric to ('left' or 'right').",
    )
    color: str | None = Field(
        default=None,
        description="Custom color for this metric series (hex color code, e.g., '#2196F3').",
    )


class XYLensCountAggregatedMetric(LensCountAggregatedMetric, XYMetricAppearance):
    """XY chart count metric with appearance options.

    Extends LensCountAggregatedMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensSumAggregatedMetric(LensSumAggregatedMetric, XYMetricAppearance):
    """XY chart sum metric with appearance options.

    Extends LensSumAggregatedMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensOtherAggregatedMetric(LensOtherAggregatedMetric, XYMetricAppearance):
    """XY chart aggregated metric with appearance options.

    Extends LensOtherAggregatedMetric to include axis and color configuration
    for use in XY charts. Supports min, max, median, and average aggregations.
    """


class XYLensLastValueAggregatedMetric(LensLastValueAggregatedMetric, XYMetricAppearance):
    """XY chart last value metric with appearance options.

    Extends LensLastValueAggregatedMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensPercentileRankAggregatedMetric(LensPercentileRankAggregatedMetric, XYMetricAppearance):
    """XY chart percentile rank metric with appearance options.

    Extends LensPercentileRankAggregatedMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensPercentileAggregatedMetric(LensPercentileAggregatedMetric, XYMetricAppearance):
    """XY chart percentile metric with appearance options.

    Extends LensPercentileAggregatedMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensFormulaMetric(LensFormulaMetric, XYMetricAppearance):
    """XY chart formula metric with appearance options.

    Extends LensFormulaMetric to include axis and color configuration
    for use in XY charts.
    """


class XYLensStaticValue(LensStaticValue, XYMetricAppearance):
    """XY chart static value with appearance options.

    Extends LensStaticValue to include axis and color configuration
    for use in XY charts.
    """


class XYESQLMetric(ESQLMetric, XYMetricAppearance):
    """XY chart ESQL metric with appearance options.

    Extends ESQLMetric to include axis and color configuration
    for use in XY charts.
    """


class XYESQLStaticValue(ESQLStaticValue, XYMetricAppearance):
    """XY chart ESQL static value with appearance options.

    Extends ESQLStaticValue to include axis and color configuration
    for use in XY charts.
    """


type LensXYMetricTypes = (
    XYLensFormulaMetric
    | XYLensCountAggregatedMetric
    | XYLensSumAggregatedMetric
    | XYLensOtherAggregatedMetric
    | XYLensLastValueAggregatedMetric
    | XYLensPercentileRankAggregatedMetric
    | XYLensPercentileAggregatedMetric
    | XYLensStaticValue
)

type ESQLXYMetricTypes = XYESQLMetric | XYESQLStaticValue
