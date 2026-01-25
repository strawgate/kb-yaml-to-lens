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

/**
 * Grid position and size for a panel.
 */
export const Grid = z.object({
  x: z.number().int(),
  y: z.number().int(),
  w: z.number().int(),
  h: z.number().int(),
}).strict();
export type GridType = z.infer<typeof Grid>;

/**
 * Panel information including grid position.
 */
export const PanelGridInfo = z.object({
  id: z.string(),
  title: z.string(),
  type: z.string(),
  grid: Grid,
}).strict();
export type PanelGridInfoType = z.infer<typeof PanelGridInfo>;

/**
 * Dashboard grid layout information.
 */
export const DashboardGridInfo = z.object({
  title: z.string(),
  description: z.string(),
  panels: z.array(PanelGridInfo),
}).strict();
export type DashboardGridInfoType = z.infer<typeof DashboardGridInfo>;

/**
 * Basic dashboard information.
 */
export const DashboardInfo = z.object({
  index: z.number().int(),
  title: z.string(),
  description: z.string(),
}).strict();
export type DashboardInfoType = z.infer<typeof DashboardInfo>;

/**
 * Column definition in ES|QL query results.
 */
export const EsqlColumn = z.object({
  name: z.string(),
  type: z.string(),
}).strict();
export type EsqlColumnType = z.infer<typeof EsqlColumn>;

/**
 * ES|QL query result containing columns and values.
 */
export const EsqlQueryResult = z.object({
  columns: z.array(EsqlColumn),
  values: z.array(z.array(z.unknown())),
  took: z.union([
    z.number().int(),
    z.null(),
  ]).default(null),
  is_partial: z.union([
    z.boolean(),
    z.null(),
  ]).default(null),
}).strict();
export type EsqlQueryResultType = z.infer<typeof EsqlQueryResult>;

/**
 * Request parameters for dashboard/compile endpoint.
 */
export const CompileRequest = z.object({
  path: z.string(),
  dashboard_index: z.number().int().default(0),
}).strict();
export type CompileRequestType = z.infer<typeof CompileRequest>;

/**
 * Request parameters for dashboard/getDashboards endpoint.
 */
export const GetDashboardsRequest = z.object({
  path: z.string(),
}).strict();
export type GetDashboardsRequestType = z.infer<typeof GetDashboardsRequest>;

/**
 * Request parameters for dashboard/getGridLayout endpoint.
 */
export const GetGridLayoutRequest = z.object({
  path: z.string(),
  dashboard_index: z.number().int().default(0),
}).strict();
export type GetGridLayoutRequestType = z.infer<typeof GetGridLayoutRequest>;

/**
 * Request parameters for dashboard/updateGridLayout endpoint.
 */
export const UpdateGridLayoutRequest = z.object({
  path: z.string(),
  panel_id: z.string(),
  grid: Grid,
  dashboard_index: z.number().int().default(0),
}).strict();
export type UpdateGridLayoutRequestType = z.infer<typeof UpdateGridLayoutRequest>;

/**
 * Request parameters for dashboard/uploadToKibana endpoint.
 */
export const UploadToKibanaRequest = z.object({
  path: z.string(),
  dashboard_index: z.number().int().default(0),
  kibana_url: z.string(),
  username: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  password: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  api_key: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  ssl_verify: z.boolean().default(true),
}).strict();
export type UploadToKibanaRequestType = z.infer<typeof UploadToKibanaRequest>;

/**
 * Request parameters for esql/execute endpoint.
 */
export const EsqlExecuteRequest = z.object({
  query: z.string(),
  kibana_url: z.string(),
  username: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  password: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  api_key: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  ssl_verify: z.boolean().default(true),
}).strict();
export type EsqlExecuteRequestType = z.infer<typeof EsqlExecuteRequest>;

/**
 * Response from dashboard/compile endpoint.
 */
export const CompileResult = z.object({
  success: z.boolean(),
  data: z.union([
    z.unknown(),
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type CompileResultType = z.infer<typeof CompileResult>;

/**
 * Response from dashboard/getDashboards endpoint.
 */
export const DashboardListResult = z.object({
  success: z.boolean(),
  data: z.union([
    z.array(DashboardInfo),
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type DashboardListResultType = z.infer<typeof DashboardListResult>;

/**
 * Response from dashboard/getGridLayout endpoint.
 */
export const GridLayoutResult = z.object({
  success: z.boolean(),
  data: z.union([
    DashboardGridInfo,
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type GridLayoutResultType = z.infer<typeof GridLayoutResult>;

/**
 * Response from dashboard/updateGridLayout endpoint.
 */
export const UpdateGridLayoutResult = z.object({
  success: z.boolean(),
  message: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type UpdateGridLayoutResultType = z.infer<typeof UpdateGridLayoutResult>;

/**
 * Response from dashboard/uploadToKibana endpoint.
 */
export const UploadResult = z.object({
  success: z.boolean(),
  dashboard_url: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  dashboard_id: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type UploadResultType = z.infer<typeof UploadResult>;

/**
 * Response from esql/execute endpoint.
 */
export const EsqlExecuteResult = z.object({
  success: z.boolean(),
  data: z.union([
    EsqlQueryResult,
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type EsqlExecuteResultType = z.infer<typeof EsqlExecuteResult>;

/**
 * Response from dashboard/getSchema endpoint.
 */
export const SchemaResult = z.object({
  success: z.boolean(),
  data: z.union([
    z.unknown(),
    z.null(),
  ]).default(null),
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type SchemaResultType = z.infer<typeof SchemaResult>;


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
