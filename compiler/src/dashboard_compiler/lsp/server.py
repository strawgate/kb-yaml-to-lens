"""LSP-based compilation server using pygls for VS Code extension.

This implementation uses the Language Server Protocol with pygls v2 to provide
dashboard compilation services to the VS Code extension.
"""

import json
import logging
from typing import Any

from lsprotocol import types
from pydantic import BaseModel
from pygls.lsp.server import LanguageServer

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient
from dashboard_compiler.lsp.grid_extractor import extract_grid_layout

logger = logging.getLogger(__name__)

# Initialize the language server
server = LanguageServer('dashboard-compiler', 'v0.1')


def _params_to_dict(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Convert pygls params object to dict.

    In pygls v2, custom LSP requests receive params as pygls.protocol.Object (a namedtuple).
    Internal calls may pass plain dicts directly.

    Args:
        params: The params object (dict or namedtuple)

    Returns:
        Dictionary representation of the params

    Raises:
        TypeError: If params cannot be converted to dict
    """
    # Already a dict - return as-is
    if isinstance(params, dict):
        return params  # pyright: ignore[reportUnknownVariableType]

    # pygls.protocol.Object is a namedtuple with _asdict() method
    if hasattr(params, '_asdict') and callable(params._asdict):  # pyright: ignore[reportAny]
        result: dict[str, Any] = params._asdict()  # pyright: ignore[reportAny,reportAssignmentType]
        return result

    # If we get here, we received an unexpected type
    msg = f'Unable to convert params of type {type(params).__name__} to dict'
    raise TypeError(msg)


def _compile_dashboard(path: str, dashboard_index: int = 0) -> dict[str, Any]:
    """Compile a dashboard at the given path and index.

    Args:
        path: Path to the YAML file containing dashboards
        dashboard_index: Index of the dashboard to compile (default: 0)

    Returns:
        Dictionary with success status and either data or error message
    """
    if path is None or len(path) == 0:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboards = load(path)
        if len(dashboards) == 0:
            return {'success': False, 'error': 'No dashboards found in YAML file'}

        if dashboard_index < 0 or dashboard_index >= len(dashboards):
            return {'success': False, 'error': f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'}

        dashboard = dashboards[dashboard_index]
        kbn_dashboard = render(dashboard)
        return {'success': True, 'data': kbn_dashboard.model_dump(by_alias=True, mode='json')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@server.command('dashboard.compile')
def compile_command(_ls: LanguageServer, args: list[Any]) -> dict[str, Any]:
    """Compile a dashboard using the workspace/executeCommand pattern.

    Args:
        args: List containing [path, dashboard_index (optional)]

    Returns:
        Dictionary with compilation result
    """
    if args is None or len(args) < 1:
        return {'success': False, 'error': 'Missing path argument'}

    path: str = args[0]  # pyright: ignore[reportAny]
    dashboard_index: int = int(args[1]) if len(args) > 1 else 0  # pyright: ignore[reportAny]

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/compile')
def compile_custom(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Handle custom compilation request for a dashboard.

    Args:
        params: Object containing path and dashboard_index

    Returns:
        Dictionary with compilation result
    """
    params_dict = _params_to_dict(params)
    path: str = params_dict.get('path', '')  # pyright: ignore[reportAny]
    dashboard_index = int(params_dict.get('dashboard_index', 0))  # pyright: ignore[reportAny]

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/getDashboards')
def get_dashboards_custom(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Get list of dashboards from a YAML file.

    Args:
        params: Object containing path to YAML file

    Returns:
        Dictionary with list of dashboards or error
    """
    params_dict = _params_to_dict(params)
    path = params_dict.get('path')

    if path is None or len(path) == 0:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboards = load(path)  # pyright: ignore[reportAny]
        dashboard_list = [
            {
                'index': i,
                'title': dashboard.name if (dashboard.name is not None and len(dashboard.name) > 0) else f'Dashboard {i + 1}',
                'description': dashboard.description if (dashboard.description is not None and len(dashboard.description) > 0) else '',
            }
            for i, dashboard in enumerate(dashboards)
        ]
    except Exception as e:
        return {'success': False, 'error': str(e)}
    else:
        return {'success': True, 'data': dashboard_list}


@server.feature('dashboard/getGridLayout')
def get_grid_layout_custom(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Get grid layout information from a YAML dashboard file.

    Args:
        params: Object containing path and dashboard_index

    Returns:
        Dictionary with grid layout information or error
    """
    params_dict = _params_to_dict(params)
    path = params_dict.get('path')
    dashboard_index = int(params_dict.get('dashboard_index', 0))  # pyright: ignore[reportAny]

    if path is None or len(path) == 0:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        result = extract_grid_layout(path, dashboard_index)
    except Exception as e:
        return {'success': False, 'error': str(e)}
    else:
        return {'success': True, 'data': result}


@server.feature('dashboard/getSchema')
def get_schema_custom(_params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Get the JSON schema for the Dashboard configuration model.

    This endpoint returns the JSON schema for the root YAML structure,
    which contains a 'dashboards' array of Dashboard objects. This schema
    can be used by VS Code extensions to provide auto-complete, validation,
    and hover documentation for YAML dashboard files.

    Args:
        _params: Request parameters (unused)

    Returns:
        Dictionary with success status and schema data or error message
    """
    try:

        class DashboardsRoot(BaseModel):
            """Root structure for dashboard YAML files."""

            dashboards: list[Dashboard]

        schema = DashboardsRoot.model_json_schema()
    except Exception as e:
        return {'success': False, 'error': str(e)}
    else:
        return {'success': True, 'data': schema}


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Handle file save events and notify client of changes.

    Args:
        ls: Language server instance
        params: Save event parameters
    """
    file_path = params.text_document.uri
    ls.protocol.notify('dashboard/fileChanged', {'uri': file_path})


@server.feature('dashboard/uploadToKibana')
async def upload_to_kibana_custom(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Upload a compiled dashboard to Kibana.

    Args:
        params: Object containing:
            - path: YAML file path
            - dashboard_index: Dashboard index to upload
            - kibana_url: Kibana base URL
            - username: Optional username
            - password: Optional password
            - api_key: Optional API key
            - ssl_verify: Whether to verify SSL

    Returns:
        Dictionary with success status and dashboard URL or error
    """
    params_dict = _params_to_dict(params)

    path = params_dict.get('path')
    dashboard_index = int(params_dict.get('dashboard_index', 0))  # pyright: ignore[reportAny]
    kibana_url = params_dict.get('kibana_url')
    username = params_dict.get('username')
    password = params_dict.get('password')
    api_key = params_dict.get('api_key')
    ssl_verify = params_dict.get('ssl_verify', True)

    if path is None or len(path) == 0 or kibana_url is None or len(kibana_url) == 0:
        return {'success': False, 'error': 'Missing required parameters (path and kibana_url)'}

    try:
        # Compile the dashboard first
        logger.info(f'Compiling dashboard from {path} (index {dashboard_index})')
        compile_result = _compile_dashboard(path, dashboard_index)
        if compile_result['success'] is not True:
            logger.error(f'Compilation failed: {compile_result.get("error")}')
            return compile_result

        # Create NDJSON content
        ndjson_content = json.dumps(compile_result['data'])
        logger.debug(f'Generated NDJSON content: {len(ndjson_content)} bytes')

        # Create Kibana client and upload
        logger.info(f'Uploading dashboard to Kibana at {kibana_url}')
        async with KibanaClient(
            url=kibana_url,
            username=username if (username is not None and len(username) > 0) else None,
            password=password if (password is not None and len(password) > 0) else None,
            api_key=api_key if (api_key is not None and len(api_key) > 0) else None,
            ssl_verify=ssl_verify,
        ) as client:
            # Upload to Kibana
            result = await client.upload_ndjson(ndjson_content, overwrite=True)
            logger.debug(
                f'Upload result: success={result.success}, success_count={len(result.success_results)}, error_count={len(result.errors)}'
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
                    logger.info(f'Dashboard uploaded successfully: {dashboard_ids[0]}')
                    return {'success': True, 'dashboard_url': dashboard_url, 'dashboard_id': dashboard_ids[0]}

                logger.error('No dashboard found in upload results')
                return {'success': False, 'error': 'No dashboard found in upload results'}

            error_messages = [str(err) for err in result.errors]
            logger.error(f'Upload failed with errors: {"; ".join(error_messages)}')
            return {'success': False, 'error': f'Upload failed: {"; ".join(error_messages)}'}

    except Exception as e:
        logger.exception('Upload error occurred')
        return {'success': False, 'error': f'Upload error: {e!s}'}


def start_server() -> None:
    """Start the LSP server via stdio."""
    server.start_io()


if __name__ == '__main__':
    start_server()
