from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensGaugeChart(BaseChart):
    """Represents a Gauge chart configuration within a Lens panel.

    Gauge charts display progress toward goals or thresholds with various visual shapes
    including horizontal/vertical bullets and arc/circular gauges.
    """

    type: Literal['gauge'] = Field(default='gauge')
    """The type of chart, which is 'gauge' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the gauge chart."""

    metric: LensMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: LensMetricTypes | None = Field(default=None)
    """An optional minimum value for the gauge range."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum value for the gauge range."""

    goal: LensMetricTypes | None = Field(default=None)
    """An optional goal/target value to display on the gauge."""

    shape: Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] | None = Field(default=None)
    """The visual shape of the gauge. Options: horizontalBullet, verticalBullet, arc (semicircle), circle (full circle)."""

    ticks_position: Literal['auto', 'bands', 'hidden'] | None = Field(default=None)
    """Position of ticks on the gauge. Options: auto, bands, hidden."""

    label_major: str | None = Field(default=None)
    """The major label text to display on the gauge."""

    label_minor: str | None = Field(default=None)
    """The minor label text to display on the gauge."""

    color_mode: Literal['none', 'palette'] | None = Field(default=None)
    """Color mode for the gauge. Options: none, palette."""

    respect_ranges: bool | None = Field(default=None)
    """Whether to respect the defined min/max ranges for coloring."""


class ESQLGaugeChart(BaseChart):
    """Represents a Gauge chart configuration within an ESQL panel."""

    type: Literal['gauge'] = Field(default='gauge')
    """The type of chart, which is 'gauge' for this visualization."""

    metric: ESQLMetricTypes = Field(...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: ESQLMetricTypes | None = Field(default=None)
    """An optional minimum value for the gauge range."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum value for the gauge range."""

    goal: ESQLMetricTypes | None = Field(default=None)
    """An optional goal/target value to display on the gauge."""

    shape: Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] | None = Field(default=None)
    """The visual shape of the gauge. Options: horizontalBullet, verticalBullet, arc (semicircle), circle (full circle)."""

    ticks_position: Literal['auto', 'bands', 'hidden'] | None = Field(default=None)
    """Position of ticks on the gauge. Options: auto, bands, hidden."""

    label_major: str | None = Field(default=None)
    """The major label text to display on the gauge."""

    label_minor: str | None = Field(default=None)
    """The minor label text to display on the gauge."""

    color_mode: Literal['none', 'palette'] | None = Field(default=None)
    """Color mode for the gauge. Options: none, palette."""

    respect_ranges: bool | None = Field(default=None)
    """Whether to respect the defined min/max ranges for coloring."""
