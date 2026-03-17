import warnings
from typing import Any, Literal, cast

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLBreakdownTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensFormulaMetric, LensMetricTypes
from kb_dashboard_core.panels.charts.lens.metrics.formula_parser import parse_formula
from kb_dashboard_core.panels.charts.metric.metrics import ESQLMetricChartMetricTypes, LensMetricChartMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class MetricTitlesAndText(BaseCfgModel):
    """Titles and text formatting options for metric charts."""

    subtitle: str | None = Field(default=None)
    """Custom subtitle text displayed below the metric title."""

    alignment: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the metric title and subtitle."""

    weight: Literal['bold', 'normal', 'lighter'] | None = Field(default=None)
    """Font weight for the metric title."""


class MetricBackgroundChart(BaseCfgModel):
    """Background chart options for the primary metric value."""

    type: Literal['line', 'bar', 'none'] = Field(default='line')
    """Background chart mode. `none` hides the background chart."""

    direction: Literal['horizontal', 'vertical'] | None = Field(default=None)
    """Bar direction. Only valid when `type` is `bar`."""

    @model_validator(mode='after')
    def validate_direction(self) -> 'MetricBackgroundChart':
        """Only allow direction when using a bar background chart."""
        if self.type != 'bar' and self.direction is not None:
            raise ValueError
        return self


class MetricPrimaryAppearance(BaseCfgModel):
    """Primary metric appearance options."""

    icon: str | None = Field(default=None)
    """Icon identifier to display alongside the primary metric value."""

    icon_position: Literal['left', 'right'] | None = Field(default=None)
    """Horizontal icon alignment relative to the primary metric value."""

    background_chart: MetricBackgroundChart | None = Field(default=None)
    """Background chart options for the primary metric value."""

    font_size: Literal['default', 'fit', 'custom'] | None = Field(default=None)
    """Font size mode for the primary metric value."""

    position: Literal['top', 'bottom'] | None = Field(default=None)
    """Vertical position of the primary metric value within the panel."""

    alignment: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the primary metric value."""


class MetricSecondaryAppearance(BaseCfgModel):
    """Secondary metric appearance options."""

    alignment: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the secondary metric value."""

    label: 'MetricSecondaryLabelAppearance | None' = Field(default=None)
    """Custom secondary label configuration."""

    @model_validator(mode='before')
    @classmethod
    def _translate_deprecated_label_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        legacy_label_position = cast('object', normalized_data.pop('label_position', None))

        label: object = normalized_data.get('label')
        if isinstance(label, str):
            normalized_data['label'] = {'text': label}
            warnings.warn(
                "Metric field 'appearance.secondary.label' as a string is deprecated, use 'appearance.secondary.label.text' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            label = normalized_data['label']

        if legacy_label_position is not None:
            if label is None:
                normalized_data['label'] = {'position': legacy_label_position}
                warnings.warn(
                    "Metric field 'appearance.secondary.label_position' is deprecated, use 'appearance.secondary.label.position' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            elif isinstance(label, dict) and 'position' not in label:
                merged_label: dict[str, Any] = dict(cast('dict[str, Any]', label))
                merged_label['position'] = legacy_label_position
                normalized_data['label'] = merged_label
                warnings.warn(
                    "Metric field 'appearance.secondary.label_position' is deprecated, use 'appearance.secondary.label.position' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            else:
                warnings.warn(
                    (
                        "Metric field 'appearance.secondary.label_position' is ignored because "
                        "'appearance.secondary.label.position' is already set."
                    ),
                    DeprecationWarning,
                    stacklevel=2,
                )

        return normalized_data


class MetricSecondaryLabelAppearance(BaseCfgModel):
    """Secondary metric label appearance options."""

    text: str | None = Field(default=None)
    """Custom label text for the secondary metric, overriding its default label."""

    position: Literal['before', 'after'] | None = Field(default=None)
    """Position of secondary label relative to the metric value."""


class MetricBreakdownAppearance(BaseCfgModel):
    """Breakdown layout options."""

    column_count: int | None = Field(default=None, ge=1)
    """Maximum number of columns when displaying broken-down metric values."""


class MetricAppearance(BaseCfgModel):
    """Grouped appearance configuration for metric chart visualizations.

    Groups all visual styling options for metric charts including icons, progress bars,
    layout, and font configuration.
    """

    primary: MetricPrimaryAppearance | None = Field(default=None)
    """Primary metric appearance options."""

    secondary: MetricSecondaryAppearance | None = Field(default=None)
    """Secondary metric appearance options."""

    breakdown: MetricBreakdownAppearance | None = Field(default=None)
    """Breakdown layout options."""


class BaseMetricChart(BaseChart):
    """Base model for defining Metric chart objects.

    Contains fields common to both Lens and ESQL metric charts.
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    appearance: MetricAppearance | None = Field(default=None)
    """Visual appearance configuration for the metric."""

    titles_and_text: MetricTitlesAndText | None = Field(default=None)
    """Formatting options for the chart titles and text."""

    @model_validator(mode='before')
    @classmethod
    def _translate_deprecated_color_fields(cls, data: object) -> object:  # noqa: PLR0912
        """Migrate deprecated chart-level color/apply_to to primary metric fields.

        Deprecated locations (mutually exclusive with their canonical replacements):
        - ``color`` (chart level) → ``primary.color``
        - ``apply_to`` (chart level) → ``primary.color.apply_to``
        - ``appearance.color.apply_to`` → ``primary.color.apply_to``
        """
        if not isinstance(data, dict):
            return data

        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))

        chart_color = cast('object', normalized_data.pop('color', None))
        chart_apply_to = cast('object', normalized_data.pop('apply_to', None))

        appearance_color_apply_to: object = None
        appearance_raw = normalized_data.get('appearance')
        if isinstance(appearance_raw, dict):
            appearance = dict(cast('dict[str, Any]', appearance_raw))
            color_raw = cast('object', appearance.pop('color', None))
            if isinstance(color_raw, dict):
                color_dict = dict(cast('dict[str, Any]', color_raw))
                appearance_color_apply_to = color_dict.get('apply_to')
            normalized_data['appearance'] = appearance

        has_deprecated = chart_color is not None or chart_apply_to is not None or appearance_color_apply_to is not None
        primary_raw = normalized_data.get('primary')
        primary: dict[str, Any] = dict(cast('dict[str, Any]', primary_raw)) if isinstance(primary_raw, dict) else {}
        has_primary = isinstance(primary_raw, dict)

        if chart_color is not None:
            if 'color' in primary:
                msg = "Metric chart fields 'color' and 'primary.color' are mutually exclusive. Use 'primary.color' only."
                raise ValueError(msg)
            warnings.warn(
                "Metric chart field 'color' is deprecated, use 'primary.color' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            primary['color'] = chart_color

        resolved_apply_to: object = None
        if appearance_color_apply_to is not None:
            warnings.warn(
                "Metric field 'appearance.color.apply_to' is deprecated, use 'primary.color.apply_to' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            resolved_apply_to = appearance_color_apply_to
        if chart_apply_to is not None:
            warnings.warn(
                "Metric field 'apply_to' is deprecated, use 'primary.color.apply_to' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if resolved_apply_to is None:
                resolved_apply_to = chart_apply_to

        if resolved_apply_to is not None:
            primary_color = primary.get('color')
            if isinstance(primary_color, dict) and 'apply_to' in primary_color:
                msg = (
                    "Deprecated metric color fields ('apply_to' or 'appearance.color.apply_to') "
                    "and 'primary.color.apply_to' are mutually exclusive. Use 'primary.color.apply_to' only."
                )
                raise ValueError(msg)
            if isinstance(primary_color, dict):
                primary_color['apply_to'] = resolved_apply_to
            else:
                migrated_color: dict[str, object] = {'apply_to': resolved_apply_to}
                if primary_color is not None:
                    migrated_color['color'] = primary_color
                primary['color'] = migrated_color

        if has_deprecated or has_primary:
            normalized_data['primary'] = primary

        return normalized_data


class LensMetricChart(BaseMetricChart):
    """Represents a Metric chart configuration within a Lens panel.

    Metric charts display a single value or a list of values, often representing
    key performance indicators.

    Examples:
        Minimal count metric:
        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
            label: "Total Requests"
        ```

        Formula-based error rate metric:
        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='status:error') / count() * 100"
            label: "Error Rate %"
            format:
              type: percent
        ```

        Styled metric with progress bar:
        ```yaml
        lens:
          type: metric
          data_view: "metrics-*"
          primary:
            aggregation: average
            field: system.cpu.total.norm.pct
          maximum:
            value: 1
          appearance:
            primary:
              background_chart:
                type: bar
                direction: horizontal
              icon: sortUp
              icon_position: right
            breakdown:
              column_count: 3
            secondary:
              label:
                text: "vs. previous day"
                position: after
          titles_and_text:
            subtitle: "Last 24 hours"
            alignment: center
            weight: bold
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the metric chart."""

    primary: LensMetricChartMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: LensMetricChartMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """An optional breakdown dimension to split metric values by category."""

    @staticmethod
    def _metric_shifts(metric: LensMetricChartMetricTypes | LensMetricTypes) -> set[str | None]:
        """Return all normalized time-shift values referenced by the metric."""
        if not isinstance(metric, LensFormulaMetric):
            return {None}

        parse_result = parse_formula(metric.formula)
        if len(parse_result.aggregations) == 0:
            return {None}

        return {aggregation.shift if aggregation.shift not in (None, '') else None for aggregation in parse_result.aggregations}

    @model_validator(mode='after')
    def validate_shifted_metrics_with_top_values_breakdown(self) -> 'LensMetricChart':
        """Kibana rejects dynamic top values when metrics use mixed time shifts."""
        if self.breakdown is not None and self.breakdown.type == 'values':
            metrics = [metric for metric in [self.primary, self.secondary, self.maximum] if metric is not None]
            distinct_shifts: set[str | None] = set()
            for metric in metrics:
                distinct_shifts.update(self._metric_shifts(metric))

            if len(distinct_shifts) > 1:
                msg = 'Metric charts with `breakdown.type: values` (dynamic top values) cannot combine metrics with different time shifts.'
                raise ValueError(msg)
        return self


class ESQLMetricChart(BaseMetricChart):
    """Represents a Metric chart configuration within an ESQL panel.

    ESQL metric charts reference columns from your ESQL query result.
    The query determines what metrics are available - each column in your
    STATS clause becomes a metric you can reference.

    Examples:
        Multi-metric ESQL example:
        ```yaml
        esql:
          type: metric
          query: |
            FROM logs-*
            | STATS
                total_requests = COUNT(*),
                avg_duration = AVG(event.duration),
                error_rate = COUNT(kql='event.outcome:failure') / COUNT(*) * 100
          primary:
            field: "total_requests"
          secondary:
            field: "avg_duration"
          maximum:
            field: "error_rate"
        ```

        Styled ES|QL metric:
        ```yaml
        esql:
          type: metric
          query: |
            FROM metrics-*
            | STATS avg_cpu = AVG(system.cpu.total.pct)
          primary:
            field: "avg_cpu"
          appearance:
            primary:
              background_chart:
                type: bar
                direction: horizontal
          titles_and_text:
            subtitle: "System Overview"
        ```
    """

    primary: ESQLMetricChartMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: ESQLMetricChartMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: ESQLBreakdownTypes | None = Field(default=None)
    """An optional breakdown dimension to split metric values by category."""
