# pyright: reportAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false, reportUnnecessaryComparison=false
# pyright: reportUnusedCallResult=false
# LSP server code deals with dynamic pygls types that lack full type annotations
"""LSP-based compilation server using pygls for VS Code extension.

This implementation uses the Language Server Protocol with pygls v2 to provide
dashboard compilation services to the VS Code extension.

All LSP handler methods use typed Pydantic request models (validated via TypeAdapter)
and return typed Pydantic response models, which are automatically serialized to JSON
by pygls. This provides type safety on both the request and response sides, and
enables automatic TypeScript schema generation via pydantic2zod.
"""

import json
import logging
from typing import Any

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import load, render
from kb_dashboard_tools import KibanaClient, normalize_credentials, redact_url
from lsprotocol import types
from pydantic import BaseModel, TypeAdapter, ValidationError
from pygls.lsp.server import LanguageServer

from dashboard_compiler.lsp.grid_extractor import extract_grid_layout
from dashboard_compiler.lsp.grid_updater import unpin_panel, update_panel_grid
from dashboard_compiler.lsp.models import (
    CompileRequest,
    CompileResult,
    DashboardInfo,
    DashboardListResult,
    EsqlExecuteRequest,
    EsqlExecuteResult,
    GetDashboardsRequest,
    GetGridLayoutRequest,
    GridLayoutResult,
    SchemaResult,
    UnpinPanelRequest,
    UpdateGridLayoutRequest,
    UpdateGridLayoutResult,
    UploadResult,
    UploadToKibanaRequest,
)

logger = logging.getLogger(__name__)

# Initialize the language server
server = LanguageServer('dashboard-compiler', 'v0.1')

# TypeAdapters for request validation - created once at module level for performance
_compile_request_adapter = TypeAdapter(CompileRequest)
_get_dashboards_request_adapter = TypeAdapter(GetDashboardsRequest)
_get_grid_layout_request_adapter = TypeAdapter(GetGridLayoutRequest)
_update_grid_layout_request_adapter = TypeAdapter(UpdateGridLayoutRequest)
_unpin_panel_request_adapter = TypeAdapter(UnpinPanelRequest)
_upload_to_kibana_request_adapter = TypeAdapter(UploadToKibanaRequest)
_esql_execute_request_adapter = TypeAdapter(EsqlExecuteRequest)


def _convert_value(value: Any) -> Any:
    """Recursively convert namedtuples to dicts within a value.

    Handles nested namedtuples (pygls.protocol.Object) that appear in LSP request params.

    Args:
        value: Any value that may contain namedtuples

    Returns:
        The value with all namedtuples converted to dicts
    """
    # Handle namedtuples (they have _asdict method)
    if hasattr(value, '_asdict') and callable(value._asdict):
        as_dict: dict[str, Any] = value._asdict()  # pyright: ignore[reportAssignmentType]
        return {k: _convert_value(v) for k, v in as_dict.items()}

    # Handle lists - recursively convert elements
    if isinstance(value, list):
        return [_convert_value(item) for item in value]

    # Handle dicts - recursively convert values
    if isinstance(value, dict):
        return {k: _convert_value(v) for k, v in value.items()}

    # Primitive values pass through unchanged
    return value


def _params_to_dict(params: Any) -> dict[str, Any]:
    """Convert pygls params object to dict, recursively handling nested objects.

    In pygls v2, custom LSP requests receive params as pygls.protocol.Object (a namedtuple).
    Nested objects (like the 'grid' field in UpdateGridLayoutRequest) also arrive as namedtuples.
    This function recursively converts the entire structure to plain dicts for Pydantic validation.

    Args:
        params: The params object (dict, namedtuple, or None)

    Returns:
        Dictionary representation of the params with all nested namedtuples converted (empty dict for None)
    """
    # None is treated as empty dict so downstream validation returns structured errors
    if params is None:
        return {}

    # Use recursive conversion for all cases
    converted = _convert_value(params)

    # Ensure we return a dict
    if isinstance(converted, dict):
        return converted

    # If we get here, we received an unexpected type at the top level
    msg = f'Unable to convert params of type {type(params).__name__} to dict'
    raise TypeError(msg)


def _compile_dashboard(path: str, dashboard_index: int = 0) -> CompileResult:
    """Compile a dashboard at the given path and index.

    Args:
        path: Path to the YAML file containing dashboards
        dashboard_index: Index of the dashboard to compile (default: 0)

    Returns:
        CompileResult with success status and either data or error message
    """
    if path is None or len(path) == 0:
        return CompileResult(success=False, error='Missing path parameter')

    try:
        dashboards = load(path)
        if len(dashboards) == 0:
            return CompileResult(success=False, error='No dashboards found in YAML file')

        if dashboard_index < 0 or dashboard_index >= len(dashboards):
            return CompileResult(success=False, error=f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})')

        dashboard = dashboards[dashboard_index]
        kbn_dashboard = render(dashboard)
        return CompileResult(success=True, data=kbn_dashboard.model_dump(by_alias=True, mode='json'))
    except Exception as e:
        return CompileResult(success=False, error=str(e))


@server.command('dashboard.compile')
def compile_command(_ls: LanguageServer, args: list[Any]) -> CompileResult:
    """Compile a dashboard using the workspace/executeCommand pattern.

    Args:
        args: List containing [path, dashboard_index (optional)]

    Returns:
        CompileResult with compilation result
    """
    if args is None or len(args) < 1:
        return CompileResult(success=False, error='Missing path argument')

    path = args[0]
    if not isinstance(path, str) or len(path) == 0:
        return CompileResult(success=False, error='Invalid path argument: expected non-empty string')
    try:
        dashboard_index: int = int(args[1]) if len(args) > 1 else 0
    except (TypeError, ValueError) as e:
        return CompileResult(success=False, error=f'Invalid dashboard_index: {e}')

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/compile')
def compile_custom(params: Any) -> CompileResult:
    """Handle custom compilation request for a dashboard.

    Args:
        params: Object containing path and dashboard_index (validated as CompileRequest)

    Returns:
        CompileResult with compilation result
    """
    params_dict = _params_to_dict(params)

    try:
        request = _compile_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return CompileResult(success=False, error=f'Invalid request parameters: {e}')

    return _compile_dashboard(request.path, request.dashboard_index)


@server.feature('dashboard/getDashboards')
def get_dashboards_custom(params: Any) -> DashboardListResult:
    """Get list of dashboards from a YAML file.

    Args:
        params: Object containing path to YAML file (validated as GetDashboardsRequest)

    Returns:
        DashboardListResult with list of dashboards or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _get_dashboards_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return DashboardListResult(success=False, error=f'Invalid request parameters: {e}')

    try:
        dashboards = load(request.path)
        dashboard_list = [
            DashboardInfo(
                index=i,
                title=dashboard.name if (dashboard.name is not None and len(dashboard.name) > 0) else f'Dashboard {i + 1}',
                description=dashboard.description if (dashboard.description is not None and len(dashboard.description) > 0) else '',
            )
            for i, dashboard in enumerate(dashboards)
        ]
    except Exception as e:
        return DashboardListResult(success=False, error=str(e))
    else:
        return DashboardListResult(success=True, data=dashboard_list)


@server.feature('dashboard/getGridLayout')
def get_grid_layout_custom(params: Any) -> GridLayoutResult:
    """Get grid layout information from a YAML dashboard file.

    Args:
        params: Object containing path and dashboard_index (validated as GetGridLayoutRequest)

    Returns:
        GridLayoutResult with grid layout information or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _get_grid_layout_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return GridLayoutResult(success=False, error=f'Invalid request parameters: {e}')

    try:
        result = extract_grid_layout(request.path, request.dashboard_index)
    except Exception as e:
        return GridLayoutResult(success=False, error=str(e))
    else:
        return GridLayoutResult(success=True, data=result)


@server.feature('dashboard/updateGridLayout')
def update_grid_layout_custom(params: Any) -> UpdateGridLayoutResult:
    """Update grid coordinates for a specific panel in a YAML dashboard file.

    Args:
        params: Object containing path, panel_id, grid, dashboard_index
            (validated as UpdateGridLayoutRequest)

    Returns:
        UpdateGridLayoutResult with success status and message or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _update_grid_layout_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return UpdateGridLayoutResult(success=False, error=f'Invalid request parameters: {e}')

    # Convert Grid model to dict for grid_updater (which expects dict)
    grid_dict = {'x': request.grid.x, 'y': request.grid.y, 'w': request.grid.w, 'h': request.grid.h}

    try:
        return update_panel_grid(request.path, request.panel_id, grid_dict, request.dashboard_index)
    except Exception as e:
        return UpdateGridLayoutResult(success=False, error=str(e))


@server.feature('dashboard/unpinPanel')
def unpin_panel_custom(params: Any) -> UpdateGridLayoutResult:
    """Unpin a panel, removing its explicit position to allow auto-positioning.

    Args:
        params: Object containing path, panel_id, dashboard_index
            (validated as UnpinPanelRequest)

    Returns:
        UpdateGridLayoutResult with success status and message or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _unpin_panel_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return UpdateGridLayoutResult(success=False, error=f'Invalid request parameters: {e}')

    try:
        return unpin_panel(request.path, request.panel_id, request.dashboard_index)
    except Exception as e:
        return UpdateGridLayoutResult(success=False, error=str(e))


@server.feature('dashboard/getSchema')
def get_schema_custom(_params: Any) -> SchemaResult:
    """Get the JSON schema for the Dashboard configuration model.

    This endpoint returns the JSON schema for the root YAML structure,
    which contains a 'dashboards' array of Dashboard objects. This schema
    can be used by VS Code extensions to provide auto-complete, validation,
    and hover documentation for YAML dashboard files.

    Args:
        _params: Request parameters (unused)

    Returns:
        SchemaResult with success status and schema data or error message
    """
    try:

        class DashboardsRoot(BaseModel):
            """Root structure for dashboard YAML files."""

            dashboards: list[Dashboard]

        schema = DashboardsRoot.model_json_schema()
    except Exception as e:
        return SchemaResult(success=False, error=str(e))
    else:
        return SchemaResult(success=True, data=schema)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Handle file save events and notify client of changes.

    Args:
        ls: Language server instance
        params: Save event parameters
    """
    file_path = params.text_document.uri
    ls.protocol.notify('dashboard/fileChanged', {'uri': file_path})


@server.feature('esql/execute')
async def execute_esql_query(params: Any) -> EsqlExecuteResult:
    """Execute an ES|QL query via Kibana's console proxy API.

    Args:
        params: Object containing query, kibana_url, and optional credentials
            (validated as EsqlExecuteRequest)

    Returns:
        EsqlExecuteResult with success status and query results or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _esql_execute_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return EsqlExecuteResult(success=False, error=f'Invalid request parameters: {e}')

    # Normalize empty strings to None for credentials
    username = normalize_credentials(request.username)
    password = normalize_credentials(request.password)
    api_key = normalize_credentials(request.api_key)

    try:
        logger.info('Executing ES|QL query via Kibana at %s', redact_url(request.kibana_url))
        async with KibanaClient(
            url=request.kibana_url,
            username=username,
            password=password,
            api_key=api_key,
            ssl_verify=request.ssl_verify,
        ) as client:
            result = await client.execute_esql(request.query)
        logger.debug('ES|QL query returned %d rows', result.row_count)
    except Exception as e:
        logger.exception('ES|QL execution error occurred')
        return EsqlExecuteResult(success=False, error=f'ES|QL execution error: {e!s}')
    else:
        return EsqlExecuteResult(success=True, data=result)


@server.feature('dashboard/uploadToKibana')
async def upload_to_kibana_custom(params: Any) -> UploadResult:
    """Upload a compiled dashboard to Kibana.

    Args:
        params: Object containing path, dashboard_index, kibana_url, and optional credentials
            (validated as UploadToKibanaRequest)

    Returns:
        UploadResult with success status and dashboard URL or error
    """
    params_dict = _params_to_dict(params)

    try:
        request = _upload_to_kibana_request_adapter.validate_python(params_dict)
    except ValidationError as e:
        return UploadResult(success=False, error=f'Invalid request parameters: {e}')

    # Normalize empty strings to None for credentials
    username = normalize_credentials(request.username)
    password = normalize_credentials(request.password)
    api_key = normalize_credentials(request.api_key)

    try:
        # Compile the dashboard first
        logger.info('Compiling dashboard from %s (index %d)', request.path, request.dashboard_index)
        compile_result = _compile_dashboard(request.path, request.dashboard_index)
        if compile_result.success is not True:
            logger.error('Compilation failed: %s', compile_result.error)
            return UploadResult(success=False, error=compile_result.error or 'Unknown compilation error')

        # Create NDJSON content
        ndjson_content = json.dumps(compile_result.data)
        logger.debug('Generated NDJSON content: %d bytes', len(ndjson_content))

        # Create Kibana client and upload
        logger.info('Uploading dashboard to Kibana at %s', redact_url(request.kibana_url))
        async with KibanaClient(
            url=request.kibana_url,
            username=username,
            password=password,
            api_key=api_key,
            ssl_verify=request.ssl_verify,
        ) as client:
            # Upload to Kibana
            result = await client.upload_ndjson(ndjson_content, overwrite=True)
            logger.debug(
                'Upload result: success=%s, success_count=%d, error_count=%d',
                result.success,
                len(result.success_results),
                len(result.errors),
            )

            if result.success is True:
                # Extract dashboard ID
                dashboard_ids = [
                    obj.destination_id if (obj.destination_id is not None and len(obj.destination_id) > 0) else obj.id
                    for obj in result.success_results
                    if obj.type == 'dashboard'
                ]

                if len(dashboard_ids) > 0:
                    dashboard_url = client.get_dashboard_url(dashboard_ids[0])
                    logger.info('Dashboard uploaded successfully: %s', dashboard_ids[0])
                    return UploadResult(success=True, dashboard_url=dashboard_url, dashboard_id=dashboard_ids[0])

                logger.error('No dashboard found in upload results')
                return UploadResult(success=False, error='No dashboard found in upload results')

            error_messages = [str(err) for err in result.errors]
            logger.error('Upload failed with errors: %s', '; '.join(error_messages))
            return UploadResult(success=False, error=f'Upload failed: {"; ".join(error_messages)}')

    except Exception as e:
        logger.exception('Upload error occurred')
        return UploadResult(success=False, error=f'Upload error: {e!s}')


def start_server() -> None:
    """Start the LSP server via stdio."""
    server.start_io()


if __name__ == '__main__':
    start_server()
