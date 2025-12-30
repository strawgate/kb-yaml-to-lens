"""Configuration models for gauge chart visualizations."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class BaseGaugeChart(BaseCfgModel):
    """Base configuration for gauge chart visualizations.

    Provides common fields shared between Lens and ESQL gauge chart configurations.
    Gauge charts display a single metric value with optional min/max ranges and goal indicators.
    """

    type: Literal['gauge'] = Field(default='gauge')
    """The type of chart, which is 'gauge' for this visualization."""

    shape: Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] | None = Field(default=None)
    """The shape of the gauge visualization."""

    ticks_position: Literal['auto', 'bands', 'hidden'] | None = Field(default=None)
    """Position of tick marks on the gauge."""

    label_major: str | None = Field(default=None)
    """Major label text to display on the gauge."""

    label_minor: str | None = Field(default=None)
    """Minor label text to display on the gauge."""

    color_mode: Literal['none', 'palette'] | None = Field(default=None)
    """Color mode for the gauge visualization."""


class LensGaugeChart(BaseChart, BaseGaugeChart):
    """Represents a Gauge chart configuration within a Lens panel.

    Gauge charts display a single metric value with optional min/max ranges and goal indicators,
    typically used to show progress toward a target or threshold.
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the gauge chart."""

    metric: LensMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: LensMetricTypes | None = Field(default=None)
    """An optional minimum value metric for the gauge range."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum value metric for the gauge range."""

    goal: LensMetricTypes | None = Field(default=None)
    """An optional goal/target metric to display as a reference line."""


class ESQLGaugeChart(BaseChart, BaseGaugeChart):
    """Represents a Gauge chart configuration within an ESQL panel.

    Gauge charts display a single metric value with optional min/max ranges and goal indicators,
    typically used to show progress toward a target or threshold.
    """

    metric: ESQLMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: ESQLMetricTypes | None = Field(default=None)
    """An optional minimum value metric for the gauge range."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum value metric for the gauge range."""

    goal: ESQLMetricTypes | None = Field(default=None)
    """An optional goal/target metric to display as a reference line."""
