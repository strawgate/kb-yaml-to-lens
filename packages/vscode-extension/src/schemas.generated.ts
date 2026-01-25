/**
 * AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
 *
 * This file is generated from Pydantic models using pydantic2zod.
 * Run `make generate-schemas` to regenerate.
 *
 * Source: packages/kb-dashboard-compiler/scripts/export_lsp_schemas.py
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { z } from "zod";


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
export function parseEsqlExecuteResult(result: unknown): EsqlQueryResultType {
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
