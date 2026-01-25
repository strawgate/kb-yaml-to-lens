/**
 * Zod schemas for runtime validation of LSP responses.
 *
 * This file re-exports all schemas from the auto-generated file.
 * The schemas are generated from Pydantic models in the Python compiler
 * to ensure type safety across the TypeScript/Python boundary.
 *
 * To regenerate: `make generate-schemas` in packages/vscode-extension/
 */

export {
    // Core data models
    GridSchema,
    PanelGridInfoSchema,
    DashboardGridInfoSchema,
    DashboardInfoSchema,
    EsqlColumnSchema,
    EsqlQueryResultSchema,
    // LSP response wrappers
    CompileResultSchema,
    DashboardListResultSchema,
    GridLayoutResultSchema,
    UpdateGridLayoutResultSchema,
    UploadResultSchema,
    EsqlExecuteResultSchema,
    SchemaResultSchema,
    // Inferred types
    type Grid,
    type PanelGridInfo,
    type DashboardGridInfo,
    type DashboardInfo,
    type EsqlColumn,
    type EsqlQueryResult,
    type CompileResult,
    type DashboardListResult,
    type GridLayoutResult,
    type UpdateGridLayoutResult,
    type UploadResult,
    type EsqlExecuteResult,
    type SchemaResult,
    // Parse helper functions
    parseCompileResult,
    parseDashboardListResult,
    parseGridLayoutResult,
    parseUploadResult,
    parseEsqlExecuteResult,
    parseUpdateGridLayoutResult,
} from './schemas.generated';
