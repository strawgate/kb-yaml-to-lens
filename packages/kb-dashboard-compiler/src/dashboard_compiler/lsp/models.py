# pyright: reportAny=false
# Uses Any for dynamic data fields like compiled dashboards and JSON schemas
"""Pydantic models for LSP request parameters and response types.

These models define the shapes of LSP request/response objects. They serve as:
1. Type safety for the Python LSP server
2. Single source of truth for TypeScript schema generation via pydantic2zod

Note: These are mutable view models for API responses, not frozen config models.
They use pydantic.BaseModel directly with extra='forbid' for strict validation.
"""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

# Import the canonical ES|QL models from kibana_client
# These are the single source of truth for ES|QL response shapes
from dashboard_compiler.kibana_client import EsqlColumn, EsqlResponse

# Re-export for schema generation
__all__ = [
    'CompileResult',
    'DashboardGridInfo',
    'DashboardInfo',
    'DashboardListResult',
    'EsqlColumn',
    'EsqlExecuteResult',
    'EsqlResponse',
    'Grid',
    'GridLayoutResult',
    'PanelGridInfo',
    'SchemaResult',
    'UpdateGridLayoutResult',
    'UploadResult',
]

# ============================================================================
# Grid Layout Models
# ============================================================================


class Grid(BaseModel):
    """Grid position and size for a panel."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    x: int
    """X position in the grid (column)."""
    y: int
    """Y position in the grid (row)."""
    w: int
    """Width in grid units."""
    h: int
    """Height in grid units."""


class PanelGridInfo(BaseModel):
    """Panel information including grid position."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    id: str
    """Panel identifier."""
    title: str
    """Panel title."""
    type: str
    """Panel type (e.g., 'esql', 'markdown')."""
    grid: Grid
    """Grid position and size."""


class DashboardGridInfo(BaseModel):
    """Dashboard grid layout information returned by getGridLayout."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    title: str
    """Dashboard title."""
    description: str
    """Dashboard description."""
    panels: list[PanelGridInfo]
    """List of panels with grid information."""


class DashboardInfo(BaseModel):
    """Basic dashboard information for getDashboards response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    index: int
    """Dashboard index in the YAML file."""
    title: str
    """Dashboard title."""
    description: str
    """Dashboard description."""


# ============================================================================
# LSP Response Models
# ============================================================================


class CompileResult(BaseModel):
    """Response from dashboard/compile endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class DashboardListResult(BaseModel):
    """Response from dashboard/getDashboards endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class GridLayoutResult(BaseModel):
    """Response from dashboard/getGridLayout endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class UpdateGridLayoutResult(BaseModel):
    """Response from dashboard/updateGridLayout endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class UploadResult(BaseModel):
    """Response from dashboard/uploadToKibana endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class EsqlExecuteResult(BaseModel):
    """Response from esql/execute endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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


class SchemaResult(BaseModel):
    """Response from dashboard/getSchema endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

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
