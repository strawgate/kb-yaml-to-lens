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


/**Grid position and size for a panel.*/
export const GridSchema = z.object({ 
/**X position in the grid*/
"x": z.number().int().describe("X position in the grid"), 
/**Y position in the grid*/
"y": z.number().int().describe("Y position in the grid"), 
/**Width in grid units*/
"w": z.number().int().describe("Width in grid units"), 
/**Height in grid units*/
"h": z.number().int().describe("Height in grid units") }).strict().describe("Grid position and size for a panel.")
export type Grid = z.infer<typeof GridSchema>


/**Panel information including grid position.*/
export const PanelGridInfoSchema = z.object({ 
/**Panel identifier*/
"id": z.string().describe("Panel identifier"), 
/**Panel title*/
"title": z.string().describe("Panel title"), 
/**Panel type (e.g., lens, visualization)*/
"type": z.string().describe("Panel type (e.g., lens, visualization)"), 
/**Grid position and size*/
"grid": GridSchema }).strict().describe("Panel information including grid position.")
export type PanelGridInfo = z.infer<typeof PanelGridInfoSchema>


/**Dashboard grid layout information.*/
export const DashboardGridInfoSchema = z.object({ 
/**Dashboard title*/
"title": z.string().describe("Dashboard title"), 
/**Dashboard description*/
"description": z.string().describe("Dashboard description"), 
/**List of panels with grid info*/
"panels": z.array(PanelGridInfoSchema).describe("List of panels with grid info") }).strict().describe("Dashboard grid layout information.")
export type DashboardGridInfo = z.infer<typeof DashboardGridInfoSchema>


/**Basic dashboard information for getDashboards response.*/
export const DashboardInfoSchema = z.object({ 
/**Dashboard index in the file*/
"index": z.number().int().describe("Dashboard index in the file"), 
/**Dashboard title*/
"title": z.string().describe("Dashboard title"), 
/**Dashboard description*/
"description": z.string().describe("Dashboard description") }).strict().describe("Basic dashboard information for getDashboards response.")
export type DashboardInfo = z.infer<typeof DashboardInfoSchema>


/**Column definition in ES|QL query results.*/
export const EsqlColumnSchema = z.object({ 
/**Column name*/
"name": z.string().describe("Column name"), 
/**Column data type (e.g., keyword, long, date)*/
"type": z.string().describe("Column data type (e.g., keyword, long, date)") }).catchall(z.any()).describe("Column definition in ES|QL query results.")
export type EsqlColumn = z.infer<typeof EsqlColumnSchema>


/**ES|QL query result data.*/
export const EsqlQueryResultSchema = z.object({ 
/**Column definitions*/
"columns": z.array(EsqlColumnSchema).describe("Column definitions"), 
/**Row values as nested arrays*/
"values": z.array(z.array(z.any())).describe("Row values as nested arrays"), 
/**Query execution time in milliseconds*/
"took": z.union([z.number().int(), z.null()]).describe("Query execution time in milliseconds").default(null), 
/**Whether results are partial*/
"is_partial": z.boolean().describe("Whether results are partial").default(false) }).catchall(z.any()).describe("ES|QL query result data.")
export type EsqlQueryResult = z.infer<typeof EsqlQueryResultSchema>


/**Response from dashboard/compile endpoint.*/
export const CompileResultSchema = z.object({ 
/**Whether the operation succeeded*/
"success": z.boolean().describe("Whether the operation succeeded"), 
/**Compiled dashboard data*/
"data": z.union([z.any(), z.null()]).describe("Compiled dashboard data").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/compile endpoint.")
export type CompileResult = z.infer<typeof CompileResultSchema>


/**Response from dashboard/getDashboards endpoint.*/
export const DashboardListResultSchema = z.object({ 
/**Whether the operation succeeded*/
"success": z.boolean().describe("Whether the operation succeeded"), 
/**List of dashboards*/
"data": z.union([z.array(DashboardInfoSchema), z.null()]).describe("List of dashboards").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/getDashboards endpoint.")
export type DashboardListResult = z.infer<typeof DashboardListResultSchema>


/**Response from dashboard/getGridLayout endpoint.*/
export const GridLayoutResultSchema = z.object({ 
/**Whether the operation succeeded*/
"success": z.boolean().describe("Whether the operation succeeded"), 
/**Grid layout information*/
"data": z.union([DashboardGridInfoSchema, z.null()]).describe("Grid layout information").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/getGridLayout endpoint.")
export type GridLayoutResult = z.infer<typeof GridLayoutResultSchema>


/**Response from dashboard/updateGridLayout endpoint.*/
export const UpdateGridLayoutResultSchema = z.object({ 
/**Whether the operation succeeded*/
"success": z.boolean().describe("Whether the operation succeeded"), 
/**Success message*/
"message": z.union([z.string(), z.null()]).describe("Success message").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/updateGridLayout endpoint.")
export type UpdateGridLayoutResult = z.infer<typeof UpdateGridLayoutResultSchema>


/**Response from dashboard/uploadToKibana endpoint.*/
export const UploadResultSchema = z.object({ 
/**Whether the upload succeeded*/
"success": z.boolean().describe("Whether the upload succeeded"), 
/**URL of the uploaded dashboard*/
"dashboard_url": z.union([z.string(), z.null()]).describe("URL of the uploaded dashboard").default(null), 
/**ID of the uploaded dashboard*/
"dashboard_id": z.union([z.string(), z.null()]).describe("ID of the uploaded dashboard").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/uploadToKibana endpoint.")
export type UploadResult = z.infer<typeof UploadResultSchema>


/**Response from esql/execute endpoint.*/
export const EsqlExecuteResultSchema = z.object({ 
/**Whether the query succeeded*/
"success": z.boolean().describe("Whether the query succeeded"), 
/**Query results*/
"data": z.union([EsqlQueryResultSchema, z.null()]).describe("Query results").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from esql/execute endpoint.")
export type EsqlExecuteResult = z.infer<typeof EsqlExecuteResultSchema>


/**Response from dashboard/getSchema endpoint.*/
export const SchemaResultSchema = z.object({ 
/**Whether the operation succeeded*/
"success": z.boolean().describe("Whether the operation succeeded"), 
/**JSON Schema data*/
"data": z.union([z.any(), z.null()]).describe("JSON Schema data").default(null), 
/**Error message if failed*/
"error": z.union([z.string(), z.null()]).describe("Error message if failed").default(null) }).strict().describe("Response from dashboard/getSchema endpoint.")
export type SchemaResult = z.infer<typeof SchemaResultSchema>


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
