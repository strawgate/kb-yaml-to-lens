#!/usr/bin/env python3
# pyright: reportUnusedImport=false, reportMissingTypeStubs=false
# Imports are used by pydantic2zod at runtime for schema generation
"""Export Zod schemas for LSP response types using pydantic2zod.

This script generates TypeScript Zod schemas directly from Pydantic models
defined in the LSP server module. The models in lsp/models.py are the
single source of truth for both Python type safety and TypeScript schemas.
"""

# Re-export all models from lsp/models for pydantic2zod to discover
# These imports make the models available for schema generation
from dashboard_compiler.kibana_client import EsqlColumn, EsqlResponse  # noqa: F401
from dashboard_compiler.lsp.models import (  # noqa: F401
    CompileResult,
    DashboardGridInfo,
    DashboardInfo,
    DashboardListResult,
    EsqlExecuteResult,
    Grid,
    GridLayoutResult,
    PanelGridInfo,
    SchemaResult,
    UpdateGridLayoutResult,
    UploadResult,
)


def main() -> None:
    """Generate Zod schemas using pydantic2zod."""
    from pydantic2zod import Compiler

    # Generate Zod schemas from this module
    # pydantic2zod discovers all Pydantic models in the module
    output = Compiler().parse('scripts.export_lsp_schemas').to_zod()
    print(output)


if __name__ == '__main__':
    main()
