"""View models for datatable visualizations in Kibana Lens format.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/datatable-esql.json
    - Data View: output/<version>/datatable-dataview.json
"""

from typing import Annotated, Literal

from pydantic import Field

from kb_dashboard_core.shared.view import BaseVwModel, OmitIfNone


class KbnDatatableColumnState(BaseVwModel):
    """Represents a column configuration in a datatable visualization.

    Maps to Kibana's ColumnState interface.
    """

    columnId: str = Field(...)
    """The ID of the column (references a metric or dimension)."""

    width: Annotated[int | None, OmitIfNone()] = Field(default=None)
    """Column width in pixels."""

    hidden: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether the column is hidden."""

    isTransposed: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether the column is transposed."""

    isMetric: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether this column represents a metric (true) or dimension (false)."""

    oneClickFilter: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Enable one-click filtering for this column."""

    alignment: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Text alignment for the column."""

    colorMode: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """How to apply colors to the column."""

    summaryRow: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Summary function to display at the bottom of the column."""

    summaryLabel: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Custom label for the summary row."""


class KbnDatatableSortingState(BaseVwModel):
    """Represents the sorting configuration for a datatable visualization.

    Maps to Kibana's SortingState interface.
    """

    columnId: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The ID of the column to sort by."""

    direction: Literal['asc', 'desc', 'none'] = Field(default='none')
    """Sort direction."""


class KbnDatatablePagingState(BaseVwModel):
    """Represents the pagination configuration for a datatable visualization.

    Maps to Kibana's PagingState interface.
    """

    size: int = Field(...)
    """Number of rows per page."""

    enabled: bool = Field(...)
    """Whether pagination is enabled."""


class KbnDatatableVisualizationState(BaseVwModel):
    """Represents the visualization state for a datatable chart.

    Maps to Kibana's DatatableVisualizationState interface.
    Note: Datatable does not use the layers structure like other visualizations.
    """

    columns: list[KbnDatatableColumnState] = Field(...)
    """List of column configurations."""

    layerId: str = Field(...)
    """The ID of the layer."""

    layerType: Literal['data'] = Field(default='data')
    """The type of layer (always 'data' for datatables)."""

    sorting: Annotated[KbnDatatableSortingState | None, OmitIfNone()] = Field(default=None)
    """Optional sorting configuration."""

    rowHeight: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Row height mode."""

    headerRowHeight: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Header row height mode."""

    rowHeightLines: Annotated[int | None, OmitIfNone()] = Field(default=None)
    """Number of lines for custom row height."""

    headerRowHeightLines: Annotated[int | None, OmitIfNone()] = Field(default=None)
    """Number of lines for custom header row height."""

    paging: Annotated[KbnDatatablePagingState | None, OmitIfNone()] = Field(default=None)
    """Optional pagination configuration."""

    density: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Grid density setting."""
