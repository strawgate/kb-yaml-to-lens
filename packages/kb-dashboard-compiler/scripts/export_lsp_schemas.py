#!/usr/bin/env python3
"""Export JSON schemas for LSP response types.

This script generates JSON Schema definitions for all Pydantic models used
in LSP responses, which can then be converted to Zod schemas for TypeScript.
"""

import json
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Grid Layout Models (for getGridLayout response)
# ============================================================================


class Grid(BaseModel):
    """Grid position and size for a panel."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    x: int = Field(description='X position in the grid')
    y: int = Field(description='Y position in the grid')
    w: int = Field(description='Width in grid units')
    h: int = Field(description='Height in grid units')


class PanelGridInfo(BaseModel):
    """Panel information including grid position."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    id: str = Field(description='Panel identifier')
    title: str = Field(description='Panel title')
    type: str = Field(description='Panel type (e.g., lens, visualization)')
    grid: Grid = Field(description='Grid position and size')


class DashboardGridInfo(BaseModel):
    """Dashboard grid layout information."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    title: str = Field(description='Dashboard title')
    description: str = Field(description='Dashboard description')
    panels: list[PanelGridInfo] = Field(description='List of panels with grid info')


class DashboardInfo(BaseModel):
    """Basic dashboard information for getDashboards response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    index: int = Field(description='Dashboard index in the file')
    title: str = Field(description='Dashboard title')
    description: str = Field(description='Dashboard description')


# ============================================================================
# ES|QL Models (already defined in kibana_client.py, duplicated here for export)
# ============================================================================


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str = Field(description='Column name')
    type: str = Field(description='Column data type (e.g., keyword, long, date)')


class EsqlQueryResult(BaseModel):
    """ES|QL query result data."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    columns: list[EsqlColumn] = Field(description='Column definitions')
    values: list[list[Any]] = Field(description='Row values as nested arrays')
    took: int | None = Field(default=None, description='Query execution time in milliseconds')
    is_partial: bool = Field(default=False, description='Whether results are partial')


# ============================================================================
# LSP Response Wrapper Models
# ============================================================================


class CompileResult(BaseModel):
    """Response from dashboard/compile endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the operation succeeded')
    data: Any | None = Field(default=None, description='Compiled dashboard data')
    error: str | None = Field(default=None, description='Error message if failed')


class DashboardListResult(BaseModel):
    """Response from dashboard/getDashboards endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the operation succeeded')
    data: list[DashboardInfo] | None = Field(default=None, description='List of dashboards')
    error: str | None = Field(default=None, description='Error message if failed')


class GridLayoutResult(BaseModel):
    """Response from dashboard/getGridLayout endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the operation succeeded')
    data: DashboardGridInfo | None = Field(default=None, description='Grid layout information')
    error: str | None = Field(default=None, description='Error message if failed')


class UpdateGridLayoutResult(BaseModel):
    """Response from dashboard/updateGridLayout endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the operation succeeded')
    message: str | None = Field(default=None, description='Success message')
    error: str | None = Field(default=None, description='Error message if failed')


class UploadResult(BaseModel):
    """Response from dashboard/uploadToKibana endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the upload succeeded')
    dashboard_url: str | None = Field(default=None, description='URL of the uploaded dashboard')
    dashboard_id: str | None = Field(default=None, description='ID of the uploaded dashboard')
    error: str | None = Field(default=None, description='Error message if failed')


class EsqlExecuteResult(BaseModel):
    """Response from esql/execute endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the query succeeded')
    data: EsqlQueryResult | None = Field(default=None, description='Query results')
    error: str | None = Field(default=None, description='Error message if failed')


class SchemaResult(BaseModel):
    """Response from dashboard/getSchema endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    success: bool = Field(description='Whether the operation succeeded')
    data: Any | None = Field(default=None, description='JSON Schema data')
    error: str | None = Field(default=None, description='Error message if failed')


# ============================================================================
# Schema Export
# ============================================================================

# All models to export for TypeScript consumption
LSP_RESPONSE_MODELS: dict[str, type[BaseModel]] = {
    # Core data models
    'Grid': Grid,
    'PanelGridInfo': PanelGridInfo,
    'DashboardGridInfo': DashboardGridInfo,
    'DashboardInfo': DashboardInfo,
    'EsqlColumn': EsqlColumn,
    'EsqlQueryResult': EsqlQueryResult,
    # LSP response wrappers
    'CompileResult': CompileResult,
    'DashboardListResult': DashboardListResult,
    'GridLayoutResult': GridLayoutResult,
    'UpdateGridLayoutResult': UpdateGridLayoutResult,
    'UploadResult': UploadResult,
    'EsqlExecuteResult': EsqlExecuteResult,
    'SchemaResult': SchemaResult,
}


def export_schemas() -> dict[str, Any]:
    """Export JSON schemas for all LSP response models.

    Returns:
        Dictionary mapping model names to their JSON Schema definitions.
    """
    schemas: dict[str, Any] = {}
    for name, model in LSP_RESPONSE_MODELS.items():
        schemas[name] = model.model_json_schema()
    return schemas


def main() -> None:
    """Export schemas to stdout as JSON."""
    schemas = export_schemas()
    # Use indent=2 for readable output
    print(json.dumps(schemas, indent=2))


if __name__ == '__main__':
    main()
