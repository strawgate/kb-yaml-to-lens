# pyright: reportAny=false
# Uses Any for dynamic data fields like compiled dashboards and JSON schemas
"""Pydantic models for LSP request parameters and response types.

These models define the shapes of LSP request/response objects. They serve as:
1. Type safety for the Python LSP server
2. Single source of truth for TypeScript schema generation via pydantic2zod

Note: These are mutable view models for API responses, not frozen config models.
The BaseLSPModel class provides shared configuration (extra='forbid') without
using ClassVar which is not supported by pydantic2zod.
"""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

# Re-export for schema generation
__all__ = [
    'BaseLSPModel',
    'CompileRequest',
    'CompileResult',
    'DashboardGridInfo',
    'DashboardInfo',
    'DashboardListResult',
    'EsqlColumn',
    'EsqlExecuteRequest',
    'EsqlExecuteResult',
    'EsqlResponse',
    'GetDashboardsRequest',
    'GetGridLayoutRequest',
    'Grid',
    'GridLayoutResult',
    'PanelGridInfo',
    'SchemaResult',
    'UpdateGridLayoutRequest',
    'UpdateGridLayoutResult',
    'UploadResult',
    'UploadToKibanaRequest',
]


# ============================================================================
# Base Model for LSP Types
# ============================================================================


class BaseLSPModel(BaseModel):
    """Base class for all LSP request and response models.

    Provides shared configuration:
    - extra='forbid': Reject unknown fields for strict validation
    - No frozen=True: These are mutable API objects, not config models
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')


# ============================================================================
# Grid Model (must be defined before request models that reference it)
# ============================================================================


class Grid(BaseLSPModel):
    """Grid position and size for a panel."""

    x: int
    """X position in the grid (column)."""
    y: int
    """Y position in the grid (row)."""
    w: int
    """Width in grid units."""
    h: int
    """Height in grid units."""


# ============================================================================
# ES|QL Models (extra='allow' for flexible API responses)
# Note: Using inline model_config (not ClassVar) for pydantic2zod compatibility
# ============================================================================


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    # Using inline model_config (not ClassVar) for pydantic2zod compatibility
    model_config = ConfigDict(extra='allow')  # pyright: ignore[reportUnannotatedClassAttribute]
    name: str
    """Column name."""
    type: str
    """Column data type (e.g., keyword, long, date)."""


class EsqlResponse(BaseModel):
    """Response from ES|QL query execution via Kibana.

    This model represents the structured result of an ES|QL query,
    containing column definitions and row values.
    """

    # Using inline model_config (not ClassVar) for pydantic2zod compatibility
    model_config = ConfigDict(extra='allow')  # pyright: ignore[reportUnannotatedClassAttribute]
    columns: list[EsqlColumn]
    """Column definitions with name and type."""
    values: list[list[Any]]
    """Row values as nested arrays."""
    took: int | None = None
    """Query execution time in milliseconds."""
    is_partial: bool | None = None
    """Whether results are partial."""

    @property
    def row_count(self) -> int:
        """Return the number of rows in the result."""
        return len(self.values)

    @property
    def column_count(self) -> int:
        """Return the number of columns in the result."""
        return len(self.columns)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert results to a list of dictionaries with column names as keys.

        Returns:
            List of dictionaries, each representing a row with column names as keys.
        """
        # Values are dynamic JSON types from Elasticsearch
        return [{col.name: val for col, val in zip(self.columns, row, strict=False)} for row in self.values]


# ============================================================================
# LSP Request Models
# ============================================================================


class CompileRequest(BaseLSPModel):
    """Request parameters for dashboard/compile endpoint."""

    path: str
    """Path to the YAML file containing dashboards."""
    dashboard_index: int = 0
    """Index of the dashboard to compile (default: 0)."""


class GetDashboardsRequest(BaseLSPModel):
    """Request parameters for dashboard/getDashboards endpoint."""

    path: str
    """Path to the YAML file containing dashboards."""


class GetGridLayoutRequest(BaseLSPModel):
    """Request parameters for dashboard/getGridLayout endpoint."""

    path: str
    """Path to the YAML file containing dashboards."""
    dashboard_index: int = 0
    """Index of the dashboard to extract (default: 0)."""


class UpdateGridLayoutRequest(BaseLSPModel):
    """Request parameters for dashboard/updateGridLayout endpoint."""

    path: str
    """Path to the YAML file containing dashboards."""
    panel_id: str
    """ID of the panel to update."""
    grid: Grid
    """New grid coordinates with x, y, w, h."""
    dashboard_index: int = 0
    """Index of the dashboard (default: 0)."""


class UploadToKibanaRequest(BaseLSPModel):
    """Request parameters for dashboard/uploadToKibana endpoint."""

    path: str
    """Path to the YAML file containing dashboards."""
    dashboard_index: int = 0
    """Index of the dashboard to upload."""
    kibana_url: str
    """Kibana base URL."""
    username: str | None = None
    """Optional username for basic auth."""
    password: str | None = None
    """Optional password for basic auth."""
    api_key: str | None = None
    """Optional API key for auth."""
    ssl_verify: bool = True
    """Whether to verify SSL certificates."""


class EsqlExecuteRequest(BaseLSPModel):
    """Request parameters for esql/execute endpoint."""

    query: str
    """ES|QL query string to execute."""
    kibana_url: str
    """Kibana base URL."""
    username: str | None = None
    """Optional username for basic auth."""
    password: str | None = None
    """Optional password for basic auth."""
    api_key: str | None = None
    """Optional API key for auth."""
    ssl_verify: bool = True
    """Whether to verify SSL certificates."""


# ============================================================================
# Grid Layout Models
# ============================================================================


class PanelGridInfo(BaseLSPModel):
    """Panel information including grid position."""

    id: str
    """Panel identifier."""
    title: str
    """Panel title."""
    type: str
    """Panel type (e.g., 'esql', 'markdown')."""
    grid: Grid
    """Grid position and size."""


class DashboardGridInfo(BaseLSPModel):
    """Dashboard grid layout information returned by getGridLayout."""

    title: str
    """Dashboard title."""
    description: str
    """Dashboard description."""
    panels: list[PanelGridInfo]
    """List of panels with grid information."""


class DashboardInfo(BaseLSPModel):
    """Basic dashboard information for getDashboards response."""

    index: int
    """Dashboard index in the YAML file."""
    title: str
    """Dashboard title."""
    description: str
    """Dashboard description."""


# ============================================================================
# LSP Response Models
# ============================================================================


class CompileResult(BaseLSPModel):
    """Response from dashboard/compile endpoint."""

    success: bool
    """Whether compilation succeeded."""
    data: Any | None = None
    """Compiled dashboard JSON on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, data: Any) -> 'CompileResult':
        """Create a successful compile result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'CompileResult':
        """Create a failed compile result."""
        return cls(success=False, error=error)


class DashboardListResult(BaseLSPModel):
    """Response from dashboard/getDashboards endpoint."""

    success: bool
    """Whether the request succeeded."""
    data: list[DashboardInfo] | None = None
    """List of dashboards on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, data: list[DashboardInfo]) -> 'DashboardListResult':
        """Create a successful dashboard list result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'DashboardListResult':
        """Create a failed dashboard list result."""
        return cls(success=False, error=error)


class GridLayoutResult(BaseLSPModel):
    """Response from dashboard/getGridLayout endpoint."""

    success: bool
    """Whether the request succeeded."""
    data: DashboardGridInfo | None = None
    """Grid layout information on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, data: DashboardGridInfo) -> 'GridLayoutResult':
        """Create a successful grid layout result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'GridLayoutResult':
        """Create a failed grid layout result."""
        return cls(success=False, error=error)


class UpdateGridLayoutResult(BaseLSPModel):
    """Response from dashboard/updateGridLayout endpoint."""

    success: bool
    """Whether the update succeeded."""
    message: str | None = None
    """Success message."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, message: str) -> 'UpdateGridLayoutResult':
        """Create a successful update result."""
        return cls(success=True, message=message)

    @classmethod
    def fail(cls, error: str) -> 'UpdateGridLayoutResult':
        """Create a failed update result."""
        return cls(success=False, error=error)


class UploadResult(BaseLSPModel):
    """Response from dashboard/uploadToKibana endpoint."""

    success: bool
    """Whether the upload succeeded."""
    dashboard_url: str | None = None
    """URL to the uploaded dashboard on success."""
    dashboard_id: str | None = None
    """ID of the uploaded dashboard on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, dashboard_url: str, dashboard_id: str) -> 'UploadResult':
        """Create a successful upload result."""
        return cls(success=True, dashboard_url=dashboard_url, dashboard_id=dashboard_id)

    @classmethod
    def fail(cls, error: str) -> 'UploadResult':
        """Create a failed upload result."""
        return cls(success=False, error=error)


class EsqlExecuteResult(BaseLSPModel):
    """Response from esql/execute endpoint."""

    success: bool
    """Whether the query succeeded."""
    data: EsqlResponse | None = None
    """Query results on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, data: EsqlResponse) -> 'EsqlExecuteResult':
        """Create a successful ES|QL result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'EsqlExecuteResult':
        """Create a failed ES|QL result."""
        return cls(success=False, error=error)


class SchemaResult(BaseLSPModel):
    """Response from dashboard/getSchema endpoint."""

    success: bool
    """Whether the request succeeded."""
    data: Any | None = None
    """JSON Schema on success."""
    error: str | None = None
    """Error message on failure."""

    @classmethod
    def ok(cls, data: Any) -> 'SchemaResult':
        """Create a successful schema result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'SchemaResult':
        """Create a failed schema result."""
        return cls(success=False, error=error)
