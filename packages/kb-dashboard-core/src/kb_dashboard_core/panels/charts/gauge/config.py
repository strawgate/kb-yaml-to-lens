"""Configuration models for gauge chart visualizations."""

from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import BaseChart, ColorRangeMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class GaugeAppearance(BaseCfgModel):
    """Appearance configuration for gauge visualizations.

    Groups all visual styling options for gauge charts including shape, tick positioning,
    labels, and palette configuration.
    """

    shape: Literal['horizontal_bullet', 'vertical_bullet', 'arc', 'circle', 'semi_circle'] | None = Field(default=None)
    """The shape of the gauge visualization."""

    ticks_position: Literal['auto', 'bands', 'hidden'] | None = Field(default=None)
    """Position of tick marks on the gauge."""

    label_major: str | None = Field(default=None)
    """Major label text to display on the gauge."""

    label_minor: str | None = Field(default=None)
    """Minor label text to display on the gauge."""

    palette: ColorRangeMapping | None = Field(default=None)
    """Range-based palette configuration for gauge thresholds. When set, enables palette color mode."""


class GaugeTitlesAndText(BaseCfgModel):
    """Title and subtitle display options for gauges.

    These fields map to Kibana gauge `labelMajor` (title) and `labelMinor` (subtitle).

    - ``None`` (omit): Kibana default (auto for title, hidden for subtitle)
    - ``False``: explicitly hidden
    - ``str``: custom text
    """

    title: str | Literal[False] | None = Field(default=None)
    """Gauge title. Omit for Kibana default, ``False`` to hide, or a string for custom text."""

    subtitle: str | Literal[False] | None = Field(default=None)
    """Gauge subtitle. Omit for no subtitle, ``False`` to hide, or a string for custom text."""


class BaseGaugeChart(BaseCfgModel):
    """Base configuration for gauge chart visualizations.

    Provides common fields shared between Lens and ESQL gauge chart configurations.
    Gauge charts display a single metric value with optional min/max ranges and goal indicators.
    """

    type: Literal['gauge'] = Field(default='gauge')
    """The type of chart, which is 'gauge' for this visualization."""

    appearance: GaugeAppearance | None = Field(default=None)
    """Visual appearance configuration for the gauge."""

    titles_and_text: GaugeTitlesAndText | None = Field(default=None)
    """Title and subtitle options mapped to gauge `label_major` and `label_minor`."""


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

        Gauge with custom appearance and palette:
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
            palette:
              range_type: percent
              thresholds:
                - up_to: 0
                  color: "#00BF6F"
                - up_to: 80
                  color: "#FFA500"
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
            | STATS avg_cpu = AVG(system.cpu.total.pct),
                    min_cpu = MIN(system.cpu.total.pct),
                    max_cpu = MAX(system.cpu.total.pct)
            | EVAL goal_cpu = 80
          metric:
            field: "avg_cpu"
          minimum:
            field: "min_cpu"
          maximum:
            field: "max_cpu"
          goal:
            field: "goal_cpu"
          appearance:
            shape: arc
        ```
    """

    metric: ESQLMetric = Field(default=...)
    """The primary metric to display in the gauge. This is the main value shown."""

    minimum: ESQLMetric | None = Field(default=None)
    """An optional minimum value for the gauge range, referenced from an ESQL query field."""

    maximum: ESQLMetric | None = Field(default=None)
    """An optional maximum value for the gauge range, referenced from an ESQL query field."""

    goal: ESQLMetric | None = Field(default=None)
    """An optional goal/target value to display as a reference, referenced from an ESQL query field."""

    @property
    def metrics(self) -> list[ESQLMetric]:
        """Provide metrics accessor for consistency with other chart types."""
        return [self.metric]
