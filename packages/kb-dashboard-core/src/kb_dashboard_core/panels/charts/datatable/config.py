from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


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

    The column_id must reference the ID of a metric or row column.
    """

    column_id: str = Field(...)
    """The ID of the column (must match a metric or row ID)."""

    width: int | None = Field(default=None)
    """Column width in pixels."""

    hidden: bool = Field(default=False)
    """Whether to hide this column."""

    alignment: DatatableAlignmentEnum | None = Field(default=None, strict=False)
    """Text alignment for the column."""

    color_mode: DatatableColorModeEnum | None = Field(default=None, strict=False)
    """How to apply colors to the column."""


class DatatableMetricColumnConfig(DatatableColumnConfig):
    """Configuration for a metric column in a datatable.

    Extends DatatableColumnConfig with metric-specific options like summary rows.
    """

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


class DatatableAppearance(BaseCfgModel):
    """Appearance settings for datatable visualization."""

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


class LensDatatableChart(BaseChart):
    """Represents a Datatable chart configuration within a Lens panel.

    Datatable charts display tabular data with customizable columns, sorting,
    pagination, and formatting options.

    Examples:
        Simple datatable with metrics and dimensions:
        ```yaml
        lens:
          type: datatable
          data_view: "metrics-*"
          metrics:
            - id: "service-count"
              field: "service.name"
              aggregation: count
          dimensions:
            - id: "service-breakdown"
              type: values
              field: "service.name"
        ```

        Datatable with sorting and pagination:
        ```yaml
        lens:
          type: datatable
          data_view: "logs-*"
          metrics:
            - id: "error-count"
              aggregation: count
              filter:
                kql: "log.level:error"
          dimensions:
            - id: "service"
              type: values
              field: "service.name"
          sorting:
            column_id: "error-count"
            direction: desc
          paging:
            enabled: true
            page_size: 25
        ```
    """

    type: Literal['datatable'] = Field(default='datatable')
    """The type of chart, which is 'datatable' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the datatable chart."""

    metrics: list[LensMetricTypes] = Field(default_factory=list)
    """List of metrics to display as columns."""

    dimensions: list[LensDimensionTypes] = Field(default_factory=list)
    """List of dimensions to use as row groupings."""

    dimensions_by: list[LensDimensionTypes] | None = Field(default=None)
    """Optional split metrics by dimensions (creates separate metric columns for each dimension value)."""

    columns: list[DatatableColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing individual columns (for rows)."""

    metric_columns: list[DatatableMetricColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing metric columns."""

    appearance: DatatableAppearance | None = Field(default=None)
    """Appearance settings for the datatable."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""

    @model_validator(mode='after')
    def validate_has_metrics_or_dimensions(self) -> Self:
        """Validate that datatable has at least one metric or dimension.

        Kibana requires datatables to have either metrics or dimensions (or both).
        An empty datatable with neither will render as a blank panel.
        """
        if len(self.metrics) == 0 and len(self.dimensions) == 0:
            msg = 'Datatable must have at least one metric or one dimension'
            raise ValueError(msg)
        return self


class ESQLDatatableChart(BaseChart):
    """Represents a Datatable chart configuration within an ESQL panel.

    Note: ESQL datatables can have empty metrics and rows lists if they rely on
    the ESQL query to define columns (e.g., STATS or KEEP commands).

    Examples:
        ES|QL datatable with STATS query:
        ```yaml
        esql:
          type: datatable
          query: |
            FROM metrics-*
            | STATS count = COUNT(*), avg_cpu = AVG(system.cpu.total.norm.pct) BY service.name
          metrics:
            - id: "count"
              field: "count"
            - id: "avg-cpu"
              field: "avg_cpu"
          dimensions:
            - id: "service"
              field: "service.name"
          sorting:
            column_id: "count"
            direction: desc
        ```
    """

    type: Literal['datatable'] = Field(default='datatable')
    """The type of chart, which is 'datatable' for this visualization."""

    metrics: list[ESQLMetricTypes] = Field(default_factory=list)
    """List of ESQL metrics to display as columns."""

    dimensions: list[ESQLDimensionTypes] = Field(default_factory=list)
    """List of ESQL dimensions to use as row groupings."""

    dimensions_by: list[ESQLDimensionTypes] | None = Field(default=None)
    """Optional split metrics by dimensions (creates separate metric columns for each dimension value)."""

    columns: list[DatatableColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing individual columns (for rows)."""

    metric_columns: list[DatatableMetricColumnConfig] | None = Field(default=None)
    """Optional column configurations for customizing metric columns."""

    appearance: DatatableAppearance | None = Field(default=None)
    """Appearance settings for the datatable."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""
