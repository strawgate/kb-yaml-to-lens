#!/usr/bin/env python3
# pyright: reportUnusedImport=false, reportMissingTypeStubs=false
# Imports are used by pydantic2zod at runtime for schema generation
"""Export Zod schemas for LSP request and response types using pydantic2zod.

This script generates TypeScript Zod schemas directly from Pydantic models.
pydantic2zod requires models to be defined in the source file it parses,
not just imported (it uses libcst to parse Python source code directly).

The models here mirror those in lsp/models.py but without features that
pydantic2zod doesn't support (like ClassVar, attribute docstrings, forward refs).

IMPORTANT: Classes must be ordered so dependencies come before dependents
(pydantic2zod doesn't support forward references).
"""

from pydantic import BaseModel, ConfigDict


# ============================================================================
# Grid Models (must come first - used by other models)
# ============================================================================
class Grid(BaseModel):
    """Grid position and size for a panel."""

    model_config = ConfigDict(extra='forbid')
    x: int
    y: int
    w: int
    h: int


class PanelGridInfo(BaseModel):
    """Panel information including grid position."""

    model_config = ConfigDict(extra='forbid')
    id: str
    title: str
    type: str
    grid: Grid


class DashboardGridInfo(BaseModel):
    """Dashboard grid layout information."""

    model_config = ConfigDict(extra='forbid')
    title: str
    description: str
    panels: list[PanelGridInfo]


class DashboardInfo(BaseModel):
    """Basic dashboard information."""

    model_config = ConfigDict(extra='forbid')
    index: int
    title: str
    description: str


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    model_config = ConfigDict(extra='allow')
    name: str
    type: str


class EsqlQueryResult(BaseModel):
    """ES|QL query result containing columns and values."""

    model_config = ConfigDict(extra='allow')
    columns: list[EsqlColumn]
    values: list[list[object]]
    took: int | None = None
    is_partial: bool | None = None


# ============================================================================
# Request Models
# ============================================================================
class CompileRequest(BaseModel):
    """Request parameters for dashboard/compile endpoint."""

    model_config = ConfigDict(extra='forbid')
    path: str
    dashboard_index: int = 0


class GetDashboardsRequest(BaseModel):
    """Request parameters for dashboard/getDashboards endpoint."""

    model_config = ConfigDict(extra='forbid')
    path: str


class GetGridLayoutRequest(BaseModel):
    """Request parameters for dashboard/getGridLayout endpoint."""

    model_config = ConfigDict(extra='forbid')
    path: str
    dashboard_index: int = 0


class UpdateGridLayoutRequest(BaseModel):
    """Request parameters for dashboard/updateGridLayout endpoint."""

    model_config = ConfigDict(extra='forbid')
    path: str
    panel_id: str
    grid: Grid
    dashboard_index: int = 0


class UploadToKibanaRequest(BaseModel):
    """Request parameters for dashboard/uploadToKibana endpoint."""

    model_config = ConfigDict(extra='forbid')
    path: str
    dashboard_index: int = 0
    kibana_url: str
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    ssl_verify: bool = True


class EsqlExecuteRequest(BaseModel):
    """Request parameters for esql/execute endpoint."""

    model_config = ConfigDict(extra='forbid')
    query: str
    kibana_url: str
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    ssl_verify: bool = True


# ============================================================================
# Response Models
# ============================================================================
class CompileResult(BaseModel):
    """Response from dashboard/compile endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    data: object | None = None
    error: str | None = None


class DashboardListResult(BaseModel):
    """Response from dashboard/getDashboards endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    data: list[DashboardInfo] | None = None
    error: str | None = None


class GridLayoutResult(BaseModel):
    """Response from dashboard/getGridLayout endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    data: DashboardGridInfo | None = None
    error: str | None = None


class UpdateGridLayoutResult(BaseModel):
    """Response from dashboard/updateGridLayout endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    message: str | None = None
    error: str | None = None


class UploadResult(BaseModel):
    """Response from dashboard/uploadToKibana endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    dashboard_url: str | None = None
    dashboard_id: str | None = None
    error: str | None = None


class EsqlExecuteResult(BaseModel):
    """Response from esql/execute endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    data: EsqlQueryResult | None = None
    error: str | None = None


class SchemaResult(BaseModel):
    """Response from dashboard/getSchema endpoint."""

    model_config = ConfigDict(extra='forbid')
    success: bool
    data: object | None = None
    error: str | None = None


def main() -> None:
    """Generate Zod schemas using pydantic2zod."""
    from pydantic2zod import Compiler

    output = Compiler().parse('export_lsp_schemas').to_zod()
    print(output)


if __name__ == '__main__':
    main()
