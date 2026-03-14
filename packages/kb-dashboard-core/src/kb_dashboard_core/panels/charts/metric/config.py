from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import BaseChart, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricChart(BaseChart):
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
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the metric chart."""

    primary: LensMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: LensMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""

    color_mode: Literal['none', 'labels', 'background'] | None = Field(default=None)
    """Color mode for metric value rendering."""

    subtitle: str | None = Field(default=None)
    """Custom subtitle text displayed below the metric title."""

    secondary_label: str | None = Field(default=None)
    """Custom label for the secondary metric, overriding its default label."""

    icon: str | None = Field(default=None)
    """Icon identifier to display alongside the metric value."""

    max_cols: int | None = Field(default=None)
    """Maximum number of columns when displaying broken-down metric values."""

    show_bar: bool | None = Field(default=None)
    """Whether to display a progress bar below the metric value."""

    progress_direction: Literal['horizontal', 'vertical'] | None = Field(default=None)
    """Direction of the progress bar when show_bar is enabled."""

    titles_text_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the metric title and subtitle."""

    value_font_mode: Literal['default', 'fit', 'custom'] | None = Field(default=None)
    """Font size mode for the primary metric value."""

    icon_align: Literal['left', 'right'] | None = Field(default=None)
    """Horizontal alignment of the icon relative to the metric value."""

    primary_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the primary metric value."""

    secondary_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the secondary metric value."""

    title_weight: Literal['bold', 'normal', 'lighter'] | None = Field(default=None)
    """Font weight for the metric title."""

    primary_position: Literal['top', 'bottom'] | None = Field(default=None)
    """Vertical position of the primary metric value within the panel."""


class ESQLMetricChart(BaseChart):
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
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    primary: ESQLMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: ESQLMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""

    color_mode: Literal['none', 'labels', 'background'] | None = Field(default=None)
    """Color mode for metric value rendering."""

    subtitle: str | None = Field(default=None)
    """Custom subtitle text displayed below the metric title."""

    secondary_label: str | None = Field(default=None)
    """Custom label for the secondary metric, overriding its default label."""

    icon: str | None = Field(default=None)
    """Icon identifier to display alongside the metric value."""

    max_cols: int | None = Field(default=None)
    """Maximum number of columns when displaying broken-down metric values."""

    show_bar: bool | None = Field(default=None)
    """Whether to display a progress bar below the metric value."""

    progress_direction: Literal['horizontal', 'vertical'] | None = Field(default=None)
    """Direction of the progress bar when show_bar is enabled."""

    titles_text_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the metric title and subtitle."""

    value_font_mode: Literal['default', 'fit', 'custom'] | None = Field(default=None)
    """Font size mode for the primary metric value."""

    icon_align: Literal['left', 'right'] | None = Field(default=None)
    """Horizontal alignment of the icon relative to the metric value."""

    primary_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the primary metric value."""

    secondary_align: Literal['left', 'center', 'right'] | None = Field(default=None)
    """Text alignment for the secondary metric value."""

    title_weight: Literal['bold', 'normal', 'lighter'] | None = Field(default=None)
    """Font weight for the metric title."""

    primary_position: Literal['top', 'bottom'] | None = Field(default=None)
    """Vertical position of the primary metric value within the panel."""
