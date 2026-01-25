#!/bin/bash
# Generate Zod schemas from Pydantic models
#
# This script:
# 1. Runs the Python export_lsp_schemas.py script to generate JSON schemas
# 2. Converts each schema to Zod using json-schema-to-zod
# 3. Combines them into a single TypeScript file

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VSCODE_DIR="$(dirname "$SCRIPT_DIR")"
COMPILER_DIR="$(dirname "$VSCODE_DIR")/kb-dashboard-compiler"
OUTPUT_FILE="$VSCODE_DIR/src/schemas.generated.ts"

echo "Generating Zod schemas from Pydantic models..."

# Create temporary directory for intermediate files
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Export JSON schemas from Python
cd "$COMPILER_DIR"
uv run python scripts/export_lsp_schemas.py > "$TMP_DIR/schemas.json"

# Generate the TypeScript header
cat > "$OUTPUT_FILE" << 'EOF'
/**
 * AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
 *
 * This file is generated from Pydantic models in the Python compiler.
 * Run `make generate-schemas` to regenerate.
 *
 * Source: packages/kb-dashboard-compiler/scripts/export_lsp_schemas.py
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { z } from 'zod';

EOF

cd "$VSCODE_DIR"

# Extract schema names and generate Zod code for each
SCHEMA_NAMES=$(node -e "const s=require('$TMP_DIR/schemas.json'); console.log(Object.keys(s).join(' '))")

for SCHEMA_NAME in $SCHEMA_NAMES; do
    echo "  Processing $SCHEMA_NAME..."

    # Extract individual schema to temp file
    node -e "
const schemas = require('$TMP_DIR/schemas.json');
console.log(JSON.stringify(schemas['$SCHEMA_NAME']));
" > "$TMP_DIR/${SCHEMA_NAME}.json"

    # Convert to Zod (ESM module for type export support)
    ZOD_OUTPUT=$(npx json-schema-to-zod \
        --input "$TMP_DIR/${SCHEMA_NAME}.json" \
        --name "${SCHEMA_NAME}Schema" \
        --type "$SCHEMA_NAME" \
        --module esm \
        --withJsdocs)

    # Strip the import statement and keep everything else
    echo "$ZOD_OUTPUT" | grep -v '^import { z }' >> "$OUTPUT_FILE"

    echo "" >> "$OUTPUT_FILE"
done

# Post-process to fix nested type references
echo "  Post-processing nested type references..."
node -e "
const fs = require('fs');
const content = fs.readFileSync('$OUTPUT_FILE', 'utf-8');

// Fix known nested type references
// PanelGridInfo.grid should reference GridSchema
// DashboardGridInfo.panels should be array of PanelGridInfoSchema
// DashboardListResult.data should be array of DashboardInfoSchema
// GridLayoutResult.data should be DashboardGridInfoSchema
// EsqlQueryResult.columns should be array of EsqlColumnSchema
// EsqlExecuteResult.data should be EsqlQueryResultSchema

let fixed = content
    // Fix PanelGridInfo.grid: z.any() -> GridSchema
    .replace(
        /(\"grid\": )z\.any\(\)\.describe\(\"Grid position and size\"\)/g,
        '\$1GridSchema'
    )
    // Fix DashboardGridInfo.panels: z.array(z.any()) -> z.array(PanelGridInfoSchema)
    .replace(
        /(\"panels\": )z\.array\(z\.any\(\)\)\.describe\(\"List of panels with grid info\"\)/g,
        '\$1z.array(PanelGridInfoSchema).describe(\"List of panels with grid info\")'
    )
    // Fix DashboardListResult.data: z.array(z.any()) -> z.array(DashboardInfoSchema)
    .replace(
        /(DashboardListResultSchema[\s\S]*?\"data\": )z\.union\(\[z\.array\(z\.any\(\)\), z\.null\(\)\]\)\.describe\(\"List of dashboards\"\)/g,
        '\$1z.union([z.array(DashboardInfoSchema), z.null()]).describe(\"List of dashboards\")'
    )
    // Fix GridLayoutResult.data: z.any() -> DashboardGridInfoSchema
    .replace(
        /(GridLayoutResultSchema[\s\S]*?\"data\": )z\.union\(\[z\.any\(\), z\.null\(\)\]\)\.describe\(\"Grid layout information\"\)/g,
        '\$1z.union([DashboardGridInfoSchema, z.null()]).describe(\"Grid layout information\")'
    )
    // Fix EsqlQueryResult.columns: z.array(z.any()) -> z.array(EsqlColumnSchema)
    .replace(
        /(EsqlQueryResultSchema[\s\S]*?\"columns\": )z\.array\(z\.any\(\)\)\.describe\(\"Column definitions\"\)/g,
        '\$1z.array(EsqlColumnSchema).describe(\"Column definitions\")'
    )
    // Fix EsqlExecuteResult.data: z.any() -> EsqlQueryResultSchema
    .replace(
        /(EsqlExecuteResultSchema[\s\S]*?\"data\": )z\.union\(\[z\.any\(\), z\.null\(\)\]\)\.describe\(\"Query results\"\)/g,
        '\$1z.union([EsqlQueryResultSchema, z.null()]).describe(\"Query results\")'
    );

fs.writeFileSync('$OUTPUT_FILE', fixed);
console.log('  Fixed nested type references');
"

# Add parse helper functions
cat >> "$OUTPUT_FILE" << 'EOF'

// ============================================================================
// Parse Helper Functions
// ============================================================================

/**
 * Parse an LSP compile result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseCompileResult(result: unknown): unknown {
    const parsed = CompileResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Compilation failed');
    }
    if (parsed.data === undefined || parsed.data === null) {
        throw new Error('Compilation returned no data');
    }
    return parsed.data;
}

/**
 * Parse an LSP dashboard list result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseDashboardListResult(result: unknown): DashboardInfo[] {
    const parsed = DashboardListResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Failed to get dashboards');
    }
    if (parsed.data === undefined || parsed.data === null) {
        throw new Error('getDashboards returned no data');
    }
    return parsed.data;
}

/**
 * Parse an LSP grid layout result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseGridLayoutResult(result: unknown): DashboardGridInfo {
    const parsed = GridLayoutResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Failed to get grid layout');
    }
    if (parsed.data === undefined || parsed.data === null) {
        throw new Error('getGridLayout returned no data');
    }
    return parsed.data;
}

/**
 * Parse an LSP upload result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseUploadResult(result: unknown): { dashboardUrl: string; dashboardId: string } {
    const parsed = UploadResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Upload failed');
    }
    if (!parsed.dashboard_url || !parsed.dashboard_id) {
        throw new Error('Upload succeeded but dashboard URL/ID not returned');
    }
    return {
        dashboardUrl: parsed.dashboard_url,
        dashboardId: parsed.dashboard_id,
    };
}

/**
 * Parse an ES|QL execute result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseEsqlExecuteResult(result: unknown): EsqlQueryResult {
    const parsed = EsqlExecuteResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'ES|QL query execution failed');
    }
    if (parsed.data === undefined || parsed.data === null) {
        throw new Error('ES|QL query returned no data');
    }
    return parsed.data;
}

/**
 * Parse an LSP update grid layout result with validation.
 * @throws Error if the result indicates failure
 */
export function parseUpdateGridLayoutResult(result: unknown): void {
    const parsed = UpdateGridLayoutResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Failed to update grid layout');
    }
}
EOF

echo "Generated $OUTPUT_FILE"
echo "Done!"
