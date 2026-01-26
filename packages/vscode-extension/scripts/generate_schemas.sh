#!/bin/bash
# Generate Zod schemas from Pydantic models using pydantic2zod
#
# This script uses pydantic2zod for direct Pydantic → Zod conversion,
# avoiding the JSON Schema intermediate step and its $ref issues.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VSCODE_DIR="$(dirname "$SCRIPT_DIR")"
COMPILER_DIR="$(dirname "$VSCODE_DIR")/kb-dashboard-cli"
OUTPUT_FILE="$VSCODE_DIR/src/schemas.generated.ts"

echo "Generating Zod schemas from Pydantic models..."

# Generate schemas using pydantic2zod
# Parse directly from the canonical lsp/models.py (single source of truth)
cd "$COMPILER_DIR"
PYTHONPATH="src:${PYTHONPATH:-}" uv run python -c "
from pydantic2zod import Compiler
output = Compiler().parse('dashboard_compiler.lsp.models').to_zod()
print(output)
" > "$OUTPUT_FILE.tmp" 2>/dev/null

# Post-process the generated schemas:
# 1. Replace standalone 'object' with 'z.unknown()' for dynamic types
#    - In arrays: z.array(object) -> z.array(z.unknown())
#    - In unions: object, -> z.unknown(),
#    - Standalone on line: object, -> z.unknown(),
# 2. Replace '.default(null)' for booleans (ssl_verify) with '.default(true)'
#    since pydantic2zod doesn't correctly handle True as a default value
# 3. Replace 'Any' with 'z.unknown()' for type safety
sed -i 's/z\.array(object)/z.array(z.unknown())/g' "$OUTPUT_FILE.tmp"
sed -i 's/^\(\s*\)object,$/\1z.unknown(),/g' "$OUTPUT_FILE.tmp"
sed -i 's/\bAny\b/z.unknown()/g' "$OUTPUT_FILE.tmp"
# Fix the ssl_verify boolean default (pydantic2zod outputs .default(null) for True)
sed -i 's/ssl_verify: z\.boolean()\.default(null)/ssl_verify: z.boolean().default(true)/g' "$OUTPUT_FILE.tmp"

# Add file header
cat > "$OUTPUT_FILE" << 'EOF'
/**
 * AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
 *
 * This file is generated from Pydantic models using pydantic2zod.
 * Run `make generate-schemas` to regenerate.
 *
 * Source: packages/kb-dashboard-cli/scripts/export_lsp_schemas.py
 */

/* eslint-disable @typescript-eslint/naming-convention */

EOF

# Append the generated schemas (skip pydantic2zod header)
tail -n +6 "$OUTPUT_FILE.tmp" >> "$OUTPUT_FILE"

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
    const parsed = CompileResult.parse(result);
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
export function parseDashboardListResult(result: unknown): DashboardInfoType[] {
    const parsed = DashboardListResult.parse(result);
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
export function parseGridLayoutResult(result: unknown): DashboardGridInfoType {
    const parsed = GridLayoutResult.parse(result);
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
    const parsed = UploadResult.parse(result);
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
export function parseEsqlExecuteResult(result: unknown): EsqlResponseType {
    const parsed = EsqlExecuteResult.parse(result);
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
    const parsed = UpdateGridLayoutResult.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error ?? 'Failed to update grid layout');
    }
}
EOF

# Clean up
rm -f "$OUTPUT_FILE.tmp"

echo "Generated $OUTPUT_FILE"
echo "Done!"
