#!/usr/bin/env python3
# pyright: reportUnusedImport=false, reportMissingTypeStubs=false
# Imports are used by pydantic2zod at runtime for schema generation
"""Export Zod schemas for LSP request and response types using pydantic2zod.

This script re-exports all LSP models from the canonical source (lsp/models.py)
so pydantic2zod can generate TypeScript Zod schemas from them.

The models in lsp/models.py are the single source of truth for both:
1. Python LSP server type safety
2. TypeScript schema generation via pydantic2zod
"""

# Re-export all LSP models from the canonical source
# pydantic2zod will parse this file and follow the imports
from dashboard_compiler.lsp.models import (
    BaseLSPModel,
    CompileRequest,
    CompileResult,
    DashboardGridInfo,
    DashboardInfo,
    DashboardListResult,
    EsqlColumn,
    EsqlExecuteRequest,
    EsqlExecuteResult,
    EsqlResponse,
    GetDashboardsRequest,
    GetGridLayoutRequest,
    Grid,
    GridLayoutResult,
    PanelGridInfo,
    SchemaResult,
    UpdateGridLayoutRequest,
    UpdateGridLayoutResult,
    UploadResult,
    UploadToKibanaRequest,
)

# Make all imports available for pydantic2zod
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


def main() -> None:
    """Generate Zod schemas using pydantic2zod."""
    from pydantic2zod import Compiler

    output = Compiler().parse('dashboard_compiler.lsp.models').to_zod()
    print(output)


if __name__ == '__main__':
    main()
