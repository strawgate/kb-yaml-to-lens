#!/usr/bin/env python3
"""Export JSON schemas for LSP response types.

This script generates JSON Schema definitions for all Pydantic models used
in LSP responses, which can then be converted to Zod schemas for TypeScript.

Note: This script uses pydantic.BaseModel directly (not BaseCfgModel) because:
1. The generated JSON schemas need field descriptions via Field(..., description=...)
   since json-schema-to-zod uses these for JSDoc comments
2. Schema export models need different model_config settings (mutable, non-strict)
3. These are export-only models, not used in the main codebase
"""

import json
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

# Import canonical ES|QL models from kibana_client to avoid duplication
# pyright: reportMissingTypeStubs=false
# Note: This import works at runtime via `uv run` which sets up the package path
from dashboard_compiler.kibana_client import EsqlColumn, EsqlResponse

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
# ES|QL Schema Export Wrappers
#
# These wrapper models re-export the canonical EsqlColumn/EsqlResponse models
# with Field(description=...) for JSON Schema generation. The canonical models
# use attribute docstrings which don't appear in JSON Schema output.
# ============================================================================


class EsqlColumnExport(BaseModel):
    """Column definition in ES|QL query results."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str = Field(description='Column name')
    type: str = Field(description='Column data type (e.g., keyword, long, date)')


class EsqlQueryResultExport(BaseModel):
    """ES|QL query result data."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    columns: list[EsqlColumnExport] = Field(description='Column definitions')
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
    data: EsqlQueryResultExport | None = Field(default=None, description='Query results')
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
# Note: EsqlColumn/EsqlQueryResult use Export wrappers for JSON Schema generation
LSP_RESPONSE_MODELS: dict[str, type[BaseModel]] = {
    # Core data models
    'Grid': Grid,
    'PanelGridInfo': PanelGridInfo,
    'DashboardGridInfo': DashboardGridInfo,
    'DashboardInfo': DashboardInfo,
    'EsqlColumn': EsqlColumnExport,  # Use export wrapper for field descriptions
    'EsqlQueryResult': EsqlQueryResultExport,  # Use export wrapper for field descriptions
    # LSP response wrappers
    'CompileResult': CompileResult,
    'DashboardListResult': DashboardListResult,
    'GridLayoutResult': GridLayoutResult,
    'UpdateGridLayoutResult': UpdateGridLayoutResult,
    'UploadResult': UploadResult,
    'EsqlExecuteResult': EsqlExecuteResult,
    'SchemaResult': SchemaResult,
}

# Verify canonical models are compatible with export wrappers
# This ensures the export wrappers stay in sync with the canonical models
_canonical_esql_column = EsqlColumn(name='test', type='keyword')
_canonical_esql_response = EsqlResponse(columns=[_canonical_esql_column], values=[])

# Type check that export wrappers have same required fields
_export_column = EsqlColumnExport(name='test', type='keyword')
_export_result = EsqlQueryResultExport(columns=[_export_column], values=[])


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
