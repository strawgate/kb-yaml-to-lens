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
    """Text orientation options for tagcloud."""

    SINGLE = 'single'
    """Single horizontal orientation."""

    RIGHT_ANGLED = 'right angled'
    """Mix of horizontal and vertical."""

    MULTIPLE = 'multiple'
    """Multiple angles."""


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
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the tagcloud chart."""

    tags: LensDimensionTypes = Field(default=...)
    """The dimension for grouping (terms). This determines the tags shown in the cloud."""

    metrics: LensMetricTypes = Field(default=...)
    """The metric for sizing. This determines the size of each tag."""


class ESQLTagcloudChart(BaseTagcloudChart):
    """Represents a Tagcloud chart configuration within an ES|QL panel."""

    tags: ESQLDimensionTypes = Field(default=...)
    """The dimension for grouping (terms). This determines the tags shown in the cloud."""

    metrics: ESQLMetricTypes = Field(default=...)
    """The metric for sizing. This determines the size of each tag."""
