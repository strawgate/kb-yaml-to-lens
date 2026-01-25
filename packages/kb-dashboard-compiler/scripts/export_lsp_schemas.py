#!/usr/bin/env python3
"""Export Zod schemas for LSP response types using pydantic2zod.

This script generates TypeScript Zod schemas directly from Pydantic models,
without requiring an intermediate JSON Schema step.

The models here define the shapes of LSP responses - they're simple data
transfer structures used only for TypeScript type generation.
"""

from typing import Any

from pydantic import BaseModel

# ============================================================================
# Grid Layout Models (for getGridLayout response)
# ============================================================================


class Grid(BaseModel):
    """Grid position and size for a panel."""

    x: int
    y: int
    w: int
    h: int


class PanelGridInfo(BaseModel):
    """Panel information including grid position."""

    id: str
    title: str
    type: str
    grid: Grid


class DashboardGridInfo(BaseModel):
    """Dashboard grid layout information."""

    title: str
    description: str
    panels: list[PanelGridInfo]


class DashboardInfo(BaseModel):
    """Basic dashboard information for getDashboards response."""

    index: int
    title: str
    description: str


# ============================================================================
# ES|QL Models
# ============================================================================


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    name: str
    type: str


class EsqlQueryResult(BaseModel):
    """ES|QL query result data."""

    columns: list[EsqlColumn]
    values: list[list[Any]]
    took: int | None = None
    is_partial: bool | None = None


# ============================================================================
# LSP Response Wrapper Models
# ============================================================================


class CompileResult(BaseModel):
    """Response from dashboard/compile endpoint."""

    success: bool
    data: Any | None = None
    error: str | None = None


class DashboardListResult(BaseModel):
    """Response from dashboard/getDashboards endpoint."""

    success: bool
    data: list[DashboardInfo] | None = None
    error: str | None = None


class GridLayoutResult(BaseModel):
    """Response from dashboard/getGridLayout endpoint."""

    success: bool
    data: DashboardGridInfo | None = None
    error: str | None = None


class UpdateGridLayoutResult(BaseModel):
    """Response from dashboard/updateGridLayout endpoint."""

    success: bool
    message: str | None = None
    error: str | None = None


class UploadResult(BaseModel):
    """Response from dashboard/uploadToKibana endpoint."""

    success: bool
    dashboard_url: str | None = None
    dashboard_id: str | None = None
    error: str | None = None


class EsqlExecuteResult(BaseModel):
    """Response from esql/execute endpoint."""

    success: bool
    data: EsqlQueryResult | None = None
    error: str | None = None


class SchemaResult(BaseModel):
    """Response from dashboard/getSchema endpoint."""

    success: bool
    data: Any | None = None
    error: str | None = None


def main() -> None:
    """Generate Zod schemas using pydantic2zod."""
    from pydantic2zod import Compiler

    # Generate Zod schemas from this module
    output = Compiler().parse('scripts.export_lsp_schemas').to_zod()
    print(output)


if __name__ == '__main__':
    main()
