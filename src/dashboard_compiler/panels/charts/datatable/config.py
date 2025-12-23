from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class DatatableAlignmentEnum(StrEnum):
    """Alignment options for datatable columns."""

    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'


class DatatableRowHeightEnum(StrEnum):
    """Row height options for datatable."""

    AUTO = 'auto'
    SINGLE = 'single'
    CUSTOM = 'custom'


class DatatableDensityEnum(StrEnum):
    """Density options for datatable."""

    COMPACT = 'compact'
    NORMAL = 'normal'
    EXPANDED = 'expanded'


class DatatableColorModeEnum(StrEnum):
    """Color mode options for datatable columns."""

    NONE = 'none'
    CELL = 'cell'
    TEXT = 'text'


class DatatableSummaryRowEnum(StrEnum):
    """Summary row options for datatable columns."""

    NONE = 'none'
    SUM = 'sum'
    AVG = 'avg'
    COUNT = 'count'
    MIN = 'min'
    MAX = 'max'


class DatatableColumnConfig(BaseCfgModel):
    """Configuration for a single datatable column.

    The column_id must reference the ID of a metric or dimension column.
    """

    column_id: str = Field(...)
    """The ID of the column (must match a metric or dimension ID)."""

    width: int | None = Field(default=None)
    """Column width in pixels."""

    hidden: bool = Field(default=False)
    """Whether to hide this column."""

    alignment: DatatableAlignmentEnum | None = Field(default=None, strict=False)
    """Text alignment for the column."""

    color_mode: DatatableColorModeEnum | None = Field(default=None, strict=False)
    """How to apply colors to the column."""

    summary_row: DatatableSummaryRowEnum | None = Field(default=None, strict=False)
    """Summary function to display at the bottom of the column (only for metrics)."""

    summary_label: str | None = Field(default=None)
    """Custom label for the summary row."""


class DatatableSortingConfig(BaseCfgModel):
    """Sorting configuration for datatable."""

    column_id: str = Field(...)
    """The ID of the column to sort by."""

    direction: Literal['asc', 'desc'] = Field(default='asc')
    """Sort direction."""


class DatatablePagingConfig(BaseCfgModel):
    """Pagination configuration for datatable."""

    enabled: bool = Field(default=True)
    """Whether pagination is enabled."""

    page_size: int = Field(default=10)
    """Number of rows per page."""


class LensDatatableChart(BaseChart):
    """Represents a Datatable chart configuration within a Lens panel.

    Datatable charts display tabular data with customizable columns, sorting,
    pagination, and formatting options.
    """

    type: Literal['datatable'] = Field(default='datatable')
    """The type of chart, which is 'datatable' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the datatable chart."""

    metrics: list[LensMetricTypes] = Field(default_factory=list)
    """List of metrics to display as columns."""

    breakdowns: list[LensDimensionTypes] = Field(default_factory=list)
    """List of dimensions to use as breakdown columns."""

    columns: list[DatatableColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing individual columns."""

    row_height: DatatableRowHeightEnum = Field(default=DatatableRowHeightEnum.AUTO, strict=False)
    """Row height mode."""

    row_height_lines: int | None = Field(default=None)
    """Number of lines for custom row height (only used with row_height='custom')."""

    header_row_height: DatatableRowHeightEnum = Field(default=DatatableRowHeightEnum.AUTO, strict=False)
    """Header row height mode."""

    header_row_height_lines: int | None = Field(default=None)
    """Number of lines for custom header row height (only used with header_row_height='custom')."""

    density: DatatableDensityEnum = Field(default=DatatableDensityEnum.NORMAL, strict=False)
    """Grid density setting."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""


class ESQLDatatableChart(BaseChart):
    """Represents a Datatable chart configuration within an ESQL panel."""

    type: Literal['datatable'] = Field(default='datatable')
    """The type of chart, which is 'datatable' for this visualization."""

    metrics: list[ESQLMetricTypes] = Field(default_factory=list)
    """List of ESQL metrics to display as columns."""

    breakdowns: list[ESQLDimensionTypes] = Field(default_factory=list)
    """List of ESQL dimensions to use as breakdown columns."""

    columns: list[DatatableColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing individual columns."""

    row_height: DatatableRowHeightEnum = Field(default=DatatableRowHeightEnum.AUTO, strict=False)
    """Row height mode."""

    row_height_lines: int | None = Field(default=None)
    """Number of lines for custom row height (only used with row_height='custom')."""

    header_row_height: DatatableRowHeightEnum = Field(default=DatatableRowHeightEnum.AUTO, strict=False)
    """Header row height mode."""

    header_row_height_lines: int | None = Field(default=None)
    """Number of lines for custom header row height (only used with header_row_height='custom')."""

    density: DatatableDensityEnum = Field(default=DatatableDensityEnum.NORMAL, strict=False)
    """Grid density setting."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""
