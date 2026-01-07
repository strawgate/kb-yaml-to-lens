"""Configuration models for gauge chart visualizations."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class GaugeAppearance(BaseCfgModel):
    """Appearance configuration for gauge visualizations.

    Groups all visual styling options for gauge charts including shape, tick positioning,
    labels, and color mode.
    """

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


class BaseGaugeChart(BaseCfgModel):
    """Base configuration for gauge chart visualizations.

    Provides common fields shared between Lens and ESQL gauge chart configurations.
    Gauge charts display a single metric value with optional min/max ranges and goal indicators.
    """

    type: Literal['gauge'] = Field(default='gauge')
    """The type of chart, which is 'gauge' for this visualization."""

    appearance: GaugeAppearance | None = Field(default=None)
    """Visual appearance configuration for the gauge."""


class LensGaugeChart(BaseChart, BaseGaugeChart):
    """Represents a Gauge chart configuration within a Lens panel.

    Gauge charts display a single metric value with optional min/max ranges and goal indicators,
    typically used to show progress toward a target or threshold.
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the gauge chart."""

    metric: LensMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: LensMetricTypes | int | float | None = Field(default=None)
    """An optional minimum value for the gauge range. Can be a metric (field-based) or a static numeric value."""

    maximum: LensMetricTypes | int | float | None = Field(default=None)
    """An optional maximum value for the gauge range. Can be a metric (field-based) or a static numeric value."""

    goal: LensMetricTypes | int | float | None = Field(default=None)
    """An optional goal/target value to display as a reference. Can be a metric (field-based) or a static numeric value."""

    @property
    def metrics(self) -> list[LensMetricTypes]:
        """Provide metrics accessor for consistency with other chart types."""
        return [self.metric]


class ESQLGaugeChart(BaseChart, BaseGaugeChart):
    """Represents a Gauge chart configuration within an ESQL panel.

    Gauge charts display a single metric value with optional min/max ranges and goal indicators,
    typically used to show progress toward a target or threshold.
    """

    metric: ESQLMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: ESQLMetricTypes | int | float | None = Field(default=None)
    """An optional minimum value for the gauge range. Can be a metric (field-based) or a static numeric value."""

    maximum: ESQLMetricTypes | int | float | None = Field(default=None)
    """An optional maximum value for the gauge range. Can be a metric (field-based) or a static numeric value."""

    goal: ESQLMetricTypes | int | float | None = Field(default=None)
    """An optional goal/target value to display as a reference. Can be a metric (field-based) or a static numeric value."""

    @property
    def metrics(self) -> list[ESQLMetricTypes]:
        """Provide metrics accessor for consistency with other chart types."""
        return [self.metric]
