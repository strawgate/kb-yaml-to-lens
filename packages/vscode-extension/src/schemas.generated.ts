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
 * Base class for all LSP request and response models.
 *
 * Provides shared configuration:
 * - extra='forbid': Reject unknown fields for strict validation
 * - No frozen=True: These are mutable API objects, not config models
 *
 */
export const BaseLSPModel = z.object({
}).strict();
export type BaseLSPModelType = z.infer<typeof BaseLSPModel>;

/**
 * Grid position and size for a panel.
 */
export const Grid = BaseLSPModel.extend({
  /**
   * X position in the grid (column).
   */
  x: z.number().int(),
  /**
   * Y position in the grid (row).
   */
  y: z.number().int(),
  /**
   * Width in grid units.
   */
  w: z.number().int(),
  /**
   * Height in grid units.
   */
  h: z.number().int(),
}).strict();
export type GridType = z.infer<typeof Grid>;

/**
 * Column definition in ES|QL query results.
 */
export const EsqlColumn = z.object({
  /**
   * Column name.
   */
  name: z.string(),
  /**
   * Column data type (e.g., keyword, long, date).
   */
  type: z.string(),
}).strict();
export type EsqlColumnType = z.infer<typeof EsqlColumn>;

/**
 * Response from ES|QL query execution via Kibana.
 *
 * This model represents the structured result of an ES|QL query,
 * containing column definitions and row values.
 *
 */
export const EsqlResponse = z.object({
  /**
   * Column definitions with name and type.
   */
  columns: z.array(EsqlColumn),
  /**
   * Row values as nested arrays.
   */
  values: z.array(z.array(z.unknown())),
  /**
   * Query execution time in milliseconds.
   */
  took: z.union([
    z.number().int(),
    z.null(),
  ]).default(null),
  /**
   * Whether results are partial.
   */
  is_partial: z.union([
    z.boolean(),
    z.null(),
  ]).default(null),
}).strict();
export type EsqlResponseType = z.infer<typeof EsqlResponse>;

/**
 * Request parameters for dashboard/compile endpoint.
 */
export const CompileRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
  /**
   * Index of the dashboard to compile (default: 0).
   */
  dashboard_index: z.number().int().default(0),
}).strict();
export type CompileRequestType = z.infer<typeof CompileRequest>;

/**
 * Request parameters for dashboard/getDashboards endpoint.
 */
export const GetDashboardsRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
}).strict();
export type GetDashboardsRequestType = z.infer<typeof GetDashboardsRequest>;

/**
 * Request parameters for dashboard/getGridLayout endpoint.
 */
export const GetGridLayoutRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
  /**
   * Index of the dashboard to extract (default: 0).
   */
  dashboard_index: z.number().int().default(0),
}).strict();
export type GetGridLayoutRequestType = z.infer<typeof GetGridLayoutRequest>;

/**
 * Request parameters for dashboard/updateGridLayout endpoint.
 */
export const UpdateGridLayoutRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
  /**
   * ID of the panel to update.
   */
  panel_id: z.string(),
  /**
   * New grid coordinates with x, y, w, h.
   */
  grid: Grid,
  /**
   * Index of the dashboard (default: 0).
   */
  dashboard_index: z.number().int().default(0),
}).strict();
export type UpdateGridLayoutRequestType = z.infer<typeof UpdateGridLayoutRequest>;

/**
 * Request parameters for dashboard/unpinPanel endpoint.
 */
export const UnpinPanelRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
  /**
   * ID of the panel to unpin.
   */
  panel_id: z.string(),
  /**
   * Index of the dashboard (default: 0).
   */
  dashboard_index: z.number().int().default(0),
}).strict();
export type UnpinPanelRequestType = z.infer<typeof UnpinPanelRequest>;

/**
 * Request parameters for dashboard/uploadToKibana endpoint.
 */
export const UploadToKibanaRequest = BaseLSPModel.extend({
  /**
   * Path to the YAML file containing dashboards.
   */
  path: z.string(),
  /**
   * Index of the dashboard to upload.
   */
  dashboard_index: z.number().int().default(0),
  /**
   * Kibana base URL.
   */
  kibana_url: z.string(),
  /**
   * Optional username for basic auth.
   */
  username: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Optional password for basic auth.
   */
  password: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Optional API key for auth.
   */
  api_key: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Whether to verify SSL certificates.
   */
  ssl_verify: z.boolean().default(true),
}).strict();
export type UploadToKibanaRequestType = z.infer<typeof UploadToKibanaRequest>;

/**
 * Request parameters for esql/execute endpoint.
 */
export const EsqlExecuteRequest = BaseLSPModel.extend({
  /**
   * ES|QL query string to execute.
   */
  query: z.string(),
  /**
   * Kibana base URL.
   */
  kibana_url: z.string(),
  /**
   * Optional username for basic auth.
   */
  username: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Optional password for basic auth.
   */
  password: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Optional API key for auth.
   */
  api_key: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Whether to verify SSL certificates.
   */
  ssl_verify: z.boolean().default(true),
}).strict();
export type EsqlExecuteRequestType = z.infer<typeof EsqlExecuteRequest>;

/**
 * Panel information including grid position.
 */
export const PanelGridInfo = BaseLSPModel.extend({
  /**
   * Panel identifier.
   */
  id: z.string(),
  /**
   * Panel title.
   */
  title: z.string(),
  /**
   * Panel type (e.g., 'esql', 'markdown').
   */
  type: z.string(),
  /**
   * Grid position and size.
   */
  grid: Grid,
  /**
   * Whether the panel has an explicit position (not auto-positioned).
   */
  is_pinned: z.boolean(),
}).strict();
export type PanelGridInfoType = z.infer<typeof PanelGridInfo>;

/**
 * Dashboard grid layout information returned by getGridLayout.
 */
export const DashboardGridInfo = BaseLSPModel.extend({
  /**
   * Dashboard title.
   */
  title: z.string(),
  /**
   * Dashboard description.
   */
  description: z.string(),
  /**
   * List of panels with grid information.
   */
  panels: z.array(PanelGridInfo),
}).strict();
export type DashboardGridInfoType = z.infer<typeof DashboardGridInfo>;

/**
 * Basic dashboard information for getDashboards response.
 */
export const DashboardInfo = BaseLSPModel.extend({
  /**
   * Dashboard index in the YAML file.
   */
  index: z.number().int(),
  /**
   * Dashboard title.
   */
  title: z.string(),
  /**
   * Dashboard description.
   */
  description: z.string(),
}).strict();
export type DashboardInfoType = z.infer<typeof DashboardInfo>;

/**
 * Response from dashboard/compile endpoint.
 */
export const CompileResult = BaseLSPModel.extend({
  /**
   * Whether compilation succeeded.
   */
  success: z.boolean(),
  /**
   * Compiled dashboard JSON on success.
   */
  data: z.union([
    z.unknown(),
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type CompileResultType = z.infer<typeof CompileResult>;

/**
 * Response from dashboard/getDashboards endpoint.
 */
export const DashboardListResult = BaseLSPModel.extend({
  /**
   * Whether the request succeeded.
   */
  success: z.boolean(),
  /**
   * List of dashboards on success.
   */
  data: z.union([
    z.array(DashboardInfo),
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type DashboardListResultType = z.infer<typeof DashboardListResult>;

/**
 * Response from dashboard/getGridLayout endpoint.
 */
export const GridLayoutResult = BaseLSPModel.extend({
  /**
   * Whether the request succeeded.
   */
  success: z.boolean(),
  /**
   * Grid layout information on success.
   */
  data: z.union([
    DashboardGridInfo,
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type GridLayoutResultType = z.infer<typeof GridLayoutResult>;

/**
 * Response from dashboard/updateGridLayout endpoint.
 */
export const UpdateGridLayoutResult = BaseLSPModel.extend({
  /**
   * Whether the update succeeded.
   */
  success: z.boolean(),
  /**
   * Success message.
   */
  message: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type UpdateGridLayoutResultType = z.infer<typeof UpdateGridLayoutResult>;

/**
 * Response from dashboard/uploadToKibana endpoint.
 */
export const UploadResult = BaseLSPModel.extend({
  /**
   * Whether the upload succeeded.
   */
  success: z.boolean(),
  /**
   * URL to the uploaded dashboard on success.
   */
  dashboard_url: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * ID of the uploaded dashboard on success.
   */
  dashboard_id: z.union([
    z.string(),
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type UploadResultType = z.infer<typeof UploadResult>;

/**
 * Response from esql/execute endpoint.
 */
export const EsqlExecuteResult = BaseLSPModel.extend({
  /**
   * Whether the query succeeded.
   */
  success: z.boolean(),
  /**
   * Query results on success.
   */
  data: z.union([
    EsqlResponse,
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
  error: z.union([
    z.string(),
    z.null(),
  ]).default(null),
}).strict();
export type EsqlExecuteResultType = z.infer<typeof EsqlExecuteResult>;

/**
 * Response from dashboard/getSchema endpoint.
 */
export const SchemaResult = BaseLSPModel.extend({
  /**
   * Whether the request succeeded.
   */
  success: z.boolean(),
  /**
   * JSON Schema on success.
   */
  data: z.union([
    z.unknown(),
    z.null(),
  ]).default(null),
  /**
   * Error message on failure.
   */
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
