/**
 * Zod schemas for runtime validation of LSP requests and responses.
 *
 * This file re-exports all schemas from the auto-generated file.
 * The schemas are generated from Pydantic models using pydantic2zod
 * to ensure type safety across the TypeScript/Python boundary.
 *
 * To regenerate: `make generate-schemas` in packages/vscode-extension/
 */

export {
    // Core data models (schemas)
    Grid,
    PanelGridInfo,
    DashboardGridInfo,
    DashboardInfo,
    EsqlColumn,
    EsqlResponse,
    // LSP request schemas
    CompileRequest,
    GetDashboardsRequest,
    GetGridLayoutRequest,
    UpdateGridLayoutRequest,
    UploadToKibanaRequest,
    EsqlExecuteRequest,
    // LSP response wrappers (schemas)
    CompileResult,
    DashboardListResult,
    GridLayoutResult,
    UpdateGridLayoutResult,
    UploadResult,
    EsqlExecuteResult,
    SchemaResult,
    // Inferred types - core data
    type GridType,
    type PanelGridInfoType,
    type DashboardGridInfoType,
    type DashboardInfoType,
    type EsqlColumnType,
    type EsqlResponseType,
    // Inferred types - requests
    type CompileRequestType,
    type GetDashboardsRequestType,
    type GetGridLayoutRequestType,
    type UpdateGridLayoutRequestType,
    type UploadToKibanaRequestType,
    type EsqlExecuteRequestType,
    // Inferred types - responses
    type CompileResultType,
    type DashboardListResultType,
    type GridLayoutResultType,
    type UpdateGridLayoutResultType,
    type UploadResultType,
    type EsqlExecuteResultType,
    type SchemaResultType,
    // Parse helper functions
    parseCompileResult,
    parseDashboardListResult,
    parseGridLayoutResult,
    parseUploadResult,
    parseEsqlExecuteResult,
    parseUpdateGridLayoutResult,
} from './schemas.generated';
