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

    Examples:
        Minimal gauge with static values:
        ```yaml
        lens:
          type: gauge
          data_view: "metrics-*"
          metric:
            aggregation: average
            field: system.cpu.total.pct
          minimum: 0
          maximum: 100
          goal: 80
        ```

        Gauge with custom appearance:
        ```yaml
        lens:
          type: gauge
          data_view: "logs-*"
          metric:
            aggregation: average
            field: response_time_ms
          minimum: 0
          maximum: 1000
          goal: 500
          appearance:
            shape: arc
            color_mode: palette
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the gauge chart."""

    metric: LensMetricTypes = Field(default=...)
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

    Examples:
        ES|QL gauge with STATS query:
        ```yaml
        esql:
          type: gauge
          query: |
            FROM metrics-*
            | STATS avg_cpu = AVG(system.cpu.total.pct)
          metric:
            field: "avg_cpu"
          minimum: 0
          maximum: 100
          goal: 80
          appearance:
            shape: arc
        ```
    """

    metric: ESQLMetricTypes = Field(default=...)
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
