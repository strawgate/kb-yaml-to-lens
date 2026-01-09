"""Tagcloud chart configuration models."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class TagcloudOrientationEnum(StrEnum):
    """Text orientation options for tagcloud visualizations.

    Controls how tags are rotated in the word cloud display.
    """

    SINGLE = 'single'
    """All tags horizontal (0°) - cleanest, most readable option."""

    RIGHT_ANGLED = 'right angled'
    """Mix of horizontal (0°) and vertical (90°) orientations - classic word cloud style."""

    MULTIPLE = 'multiple'
    """Multiple angles including diagonal - most artistic but potentially less readable."""


class TagcloudAppearance(BaseCfgModel):
    """Appearance settings for tagcloud."""

    min_font_size: int | None = Field(default=12, ge=1, le=100)
    """Minimum font size for tags. Defaults to 12."""

    max_font_size: int | None = Field(default=72, ge=1, le=200)
    """Maximum font size for tags. Defaults to 72."""

    orientation: TagcloudOrientationEnum | None = Field(default=TagcloudOrientationEnum.SINGLE, strict=False)  # Turn off strict for enums
    """Text orientation configuration. Defaults to 'single'."""

    show_label: bool | None = Field(default=True)
    """Toggle for label visibility. Defaults to True."""


class BaseTagcloudChart(BaseChart):
    """Base model for tagcloud chart objects."""

    type: Literal['tagcloud'] = Field(default='tagcloud')

    appearance: TagcloudAppearance | None = Field(default=None)
    """Formatting options for the chart appearance."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart colors."""


class LensTagcloudChart(BaseTagcloudChart):
    """Represents a Tagcloud chart configuration within a Lens panel.

    Tagcloud charts are used to visualize term frequency as word/tag clouds.

    Examples:
        Minimal tagcloud:
        ```yaml
        dashboards:
        - name: "Log Analysis"
          panels:
            - title: "Top Error Messages"
              grid: { x: 0, y: 0, w: 48, h: 6 }
              lens:
                type: tagcloud
                data_view: "logs-*"
                dimension:
                  type: values
                  field: "error.message"
                metric:
                  aggregation: count
        ```

        Advanced tagcloud with appearance customization:
        ```yaml
        dashboards:
        - name: "Advanced Tag Cloud"
          panels:
            - title: "Service Labels"
              grid: { x: 0, y: 0, w: 48, h: 8 }
              lens:
                type: tagcloud
                data_view: "logs-*"
                dimension:
                  type: values
                  field: "service.name"
                metric:
                  aggregation: count
                appearance:
                  min_font_size: 12
                  max_font_size: 96
                  orientation: "multiple"
                  show_label: false
                color:
                  palette: "kibana_palette"
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the tagcloud chart."""

    dimension: LensDimensionTypes = Field(default=...)
    """The dimension for grouping (terms). This determines the tags shown in the cloud."""

    metric: LensMetricTypes = Field(default=...)
    """The metric for sizing. This determines the size of each tag."""


class ESQLTagcloudChart(BaseTagcloudChart):
    """Represents a Tagcloud chart configuration within an ES|QL panel.

    Examples:
        ES|QL tagcloud:
        ```yaml
        dashboards:
        - name: "Log Analysis"
          panels:
            - title: "Top Error Messages"
              grid: { x: 0, y: 0, w: 48, h: 6 }
              esql:
                type: tagcloud
                query: "FROM logs-* | STATS error_count = count(*) BY error.message"
                dimension:
                  field: "error.message"
                metric:
                  field: "error_count"
        ```
    """

    dimension: ESQLDimensionTypes = Field(default=...)
    """The dimension for grouping (terms). This determines the tags shown in the cloud."""

    metric: ESQLMetricTypes = Field(default=...)
    """The metric for sizing. This determines the size of each tag."""
