/**
 * Zod schemas for runtime validation of LSP responses.
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
    EsqlQueryResult,
    // LSP response wrappers (schemas)
    CompileResult,
    DashboardListResult,
    GridLayoutResult,
    UpdateGridLayoutResult,
    UploadResult,
    EsqlExecuteResult,
    SchemaResult,
    // Inferred types
    type GridType,
    type PanelGridInfoType,
    type DashboardGridInfoType,
    type DashboardInfoType,
    type EsqlColumnType,
    type EsqlQueryResultType,
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
