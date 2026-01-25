/**
 * Zod schemas for runtime validation of LSP responses.
 *
 * These schemas provide type-safe parsing of responses from the Python
 * LSP server, eliminating unsafe `as any` casts and providing clear
 * error messages when responses don't match expected structure.
 */

import { z } from 'zod';

// Grid position schema
// eslint-disable-next-line @typescript-eslint/naming-convention
export const GridSchema = z.object({
    x: z.number(),
    y: z.number(),
    w: z.number(),
    h: z.number(),
});

export type Grid = z.infer<typeof GridSchema>;

// Panel grid info schema
// eslint-disable-next-line @typescript-eslint/naming-convention
export const PanelGridInfoSchema = z.object({
    id: z.string(),
    title: z.string(),
    type: z.string(),
    grid: GridSchema,
});

export type PanelGridInfo = z.infer<typeof PanelGridInfoSchema>;

// Dashboard grid info schema
// eslint-disable-next-line @typescript-eslint/naming-convention
export const DashboardGridInfoSchema = z.object({
    title: z.string(),
    description: z.string(),
    panels: z.array(PanelGridInfoSchema),
});

export type DashboardGridInfo = z.infer<typeof DashboardGridInfoSchema>;

// Dashboard info schema (for getDashboards response)
// eslint-disable-next-line @typescript-eslint/naming-convention
export const DashboardInfoSchema = z.object({
    index: z.number(),
    title: z.string(),
    description: z.string(),
});

export type DashboardInfo = z.infer<typeof DashboardInfoSchema>;

// ES|QL column schema
// eslint-disable-next-line @typescript-eslint/naming-convention
export const EsqlColumnSchema = z.object({
    name: z.string(),
    type: z.string(),
});

export type EsqlColumn = z.infer<typeof EsqlColumnSchema>;

// ES|QL query result schema
// eslint-disable-next-line @typescript-eslint/naming-convention
export const EsqlQueryResultSchema = z.object({
    columns: z.array(EsqlColumnSchema),
    values: z.array(z.array(z.unknown())),
    took: z.number().optional(),
    // eslint-disable-next-line @typescript-eslint/naming-convention
    is_partial: z.boolean().optional(),
});

export type EsqlQueryResult = z.infer<typeof EsqlQueryResultSchema>;

// Generic LSP result wrapper schemas
// eslint-disable-next-line @typescript-eslint/naming-convention
export const CompileResultSchema = z.object({
    success: z.boolean(),
    data: z.unknown().optional(),
    error: z.string().optional(),
});

export type CompileResult = z.infer<typeof CompileResultSchema>;

// eslint-disable-next-line @typescript-eslint/naming-convention
export const DashboardListResultSchema = z.object({
    success: z.boolean(),
    data: z.array(DashboardInfoSchema).optional(),
    error: z.string().optional(),
});

export type DashboardListResult = z.infer<typeof DashboardListResultSchema>;

// eslint-disable-next-line @typescript-eslint/naming-convention
export const GridLayoutResultSchema = z.object({
    success: z.boolean(),
    data: DashboardGridInfoSchema.optional(),
    error: z.string().optional(),
});

export type GridLayoutResult = z.infer<typeof GridLayoutResultSchema>;

// eslint-disable-next-line @typescript-eslint/naming-convention
export const UploadResultSchema = z.object({
    success: z.boolean(),
    // eslint-disable-next-line @typescript-eslint/naming-convention
    dashboard_url: z.string().optional(),
    // eslint-disable-next-line @typescript-eslint/naming-convention
    dashboard_id: z.string().optional(),
    error: z.string().optional(),
});

export type UploadResult = z.infer<typeof UploadResultSchema>;

// eslint-disable-next-line @typescript-eslint/naming-convention
export const EsqlExecuteResultSchema = z.object({
    success: z.boolean(),
    data: EsqlQueryResultSchema.optional(),
    error: z.string().optional(),
});

export type EsqlExecuteResult = z.infer<typeof EsqlExecuteResultSchema>;

// eslint-disable-next-line @typescript-eslint/naming-convention
export const SchemaResultSchema = z.object({
    success: z.boolean(),
    data: z.unknown().optional(),
    error: z.string().optional(),
});

export type SchemaResult = z.infer<typeof SchemaResultSchema>;

// Grid extractor result schema (used by subprocess calls)
// eslint-disable-next-line @typescript-eslint/naming-convention
export const GridExtractorResultSchema = z.union([
    DashboardGridInfoSchema,
    z.object({ error: z.string() }),
]);

export type GridExtractorResult = z.infer<typeof GridExtractorResultSchema>;

/**
 * Parse a grid extractor result with validation.
 * @throws ZodError if the result doesn't match the expected schema
 */
export function parseGridExtractorResult(data: unknown): DashboardGridInfo {
    const result = GridExtractorResultSchema.parse(data);
    if ('error' in result) {
        throw new Error(result.error);
    }
    return result;
}

/**
 * Parse an LSP compile result with validation.
 * @throws Error if the result indicates failure or has invalid structure
 */
export function parseCompileResult(result: unknown): unknown {
    const parsed = CompileResultSchema.parse(result);
    if (!parsed.success) {
        throw new Error(parsed.error || 'Compilation failed');
    }
    if (parsed.data === undefined) {
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
        throw new Error(parsed.error || 'Failed to get dashboards');
    }
    if (parsed.data === undefined) {
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
        throw new Error(parsed.error || 'Failed to get grid layout');
    }
    if (parsed.data === undefined) {
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
        throw new Error(parsed.error || 'Upload failed');
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
        throw new Error(parsed.error || 'ES|QL query execution failed');
    }
    if (parsed.data === undefined) {
        throw new Error('ES|QL query returned no data');
    }
    return parsed.data;
}
