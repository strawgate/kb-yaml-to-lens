import warnings
from enum import StrEnum
from typing import Any, Literal, Self, cast

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart
from kb_dashboard_core.panels.charts.datatable.breakdowns import ESQLDatatableBreakdownTypes, LensDatatableBreakdownTypes
from kb_dashboard_core.panels.charts.datatable.dimensions import ESQLDatatableDimensionTypes, LensDatatableDimensionTypes
from kb_dashboard_core.panels.charts.datatable.metrics import ESQLDatatableMetricTypes, LensDatatableMetricTypes
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


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
        Simple datatable with metrics and breakdowns:
        ```yaml
        lens:
          type: datatable
          data_view: "metrics-*"
          metrics:
            - id: "service-count"
              field: "service.name"
              aggregation: count
          breakdowns:
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
          breakdowns:
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

    metrics: list[LensDatatableMetricTypes | LensMetricTypes] = Field(default_factory=list)
    """List of metrics to display as columns."""

    breakdowns: list[LensDatatableBreakdownTypes | LensBreakdownTypes] = Field(default_factory=list)
    """List of breakdowns to use as row groupings."""

    metrics_split_by: list[LensDatatableDimensionTypes | LensDimensionTypes] | None = Field(default=None)
    """Optional split-metrics-by dimensions (creates separate metric columns for each dimension value)."""

    appearance: DatatableAppearance | None = Field(default=None)
    """Appearance settings for the datatable."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""

    @model_validator(mode='before')
    @classmethod
    def _warn_deprecated_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        if 'dimensions' in normalized_data and 'breakdowns' not in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions' (row groupings) is deprecated, use 'breakdowns' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data['breakdowns'] = normalized_data.pop('dimensions')
        elif 'dimensions' in normalized_data and 'breakdowns' in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions' (row groupings) is ignored because 'breakdowns' is already set.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data.pop('dimensions')
        if 'dimensions_by' in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions_by' is deprecated, use 'metrics_split_by' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if 'metrics_split_by' not in normalized_data:
                normalized_data['metrics_split_by'] = normalized_data.pop('dimensions_by')
            else:
                normalized_data.pop('dimensions_by')
        return normalized_data

    @model_validator(mode='after')
    def validate_has_metrics_or_breakdowns(self) -> Self:
        """Validate that datatable has at least one metric or breakdown.

        Kibana requires datatables to have either metrics or breakdowns (or both).
        An empty datatable with neither will render as a blank panel.
        """
        if len(self.metrics) == 0 and len(self.breakdowns) == 0:
            msg = 'Datatable must have at least one metric or one breakdown'
            raise ValueError(msg)
        return self


class ESQLDatatableChart(BaseChart):
    """Represents a Datatable chart configuration within an ESQL panel.

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
          breakdowns:
            - id: "service"
              field: "service.name"
          sorting:
            column_id: "count"
            direction: desc
        ```
    """

    type: Literal['datatable'] = Field(default='datatable')
    """The type of chart, which is 'datatable' for this visualization."""

    metrics: list[ESQLDatatableMetricTypes | ESQLMetricTypes] = Field(default_factory=list)
    """List of ESQL metrics to display as columns."""

    breakdowns: list[ESQLDatatableBreakdownTypes | ESQLDimensionTypes] = Field(default_factory=list)
    """List of ESQL breakdowns to use as row groupings."""

    metrics_split_by: list[ESQLDatatableDimensionTypes | ESQLDimensionTypes] | None = Field(default=None)
    """Optional split-metrics-by dimensions (creates separate metric columns for each dimension value)."""

    appearance: DatatableAppearance | None = Field(default=None)
    """Appearance settings for the datatable."""

    sorting: DatatableSortingConfig | None = Field(default=None)
    """Optional sorting configuration."""

    paging: DatatablePagingConfig | None = Field(default=None)
    """Optional pagination configuration."""

    @model_validator(mode='before')
    @classmethod
    def _warn_deprecated_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        if 'dimensions' in normalized_data and 'breakdowns' not in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions' (row groupings) is deprecated, use 'breakdowns' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data['breakdowns'] = normalized_data.pop('dimensions')
        elif 'dimensions' in normalized_data and 'breakdowns' in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions' (row groupings) is ignored because 'breakdowns' is already set.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data.pop('dimensions')
        if 'dimensions_by' in normalized_data:
            warnings.warn(
                "Datatable field 'dimensions_by' is deprecated, use 'metrics_split_by' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if 'metrics_split_by' not in normalized_data:
                normalized_data['metrics_split_by'] = normalized_data.pop('dimensions_by')
            else:
                normalized_data.pop('dimensions_by')
        return normalized_data

    @model_validator(mode='after')
    def validate_has_metrics_or_breakdowns(self) -> Self:
        """Validate that datatable has at least one metric or breakdown."""
        if len(self.metrics) == 0 and len(self.breakdowns) == 0:
            msg = 'Datatable must have at least one metric or one breakdown'
            raise ValueError(msg)
        return self
