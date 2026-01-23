# pyright: reportAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false, reportUnnecessaryComparison=false
# pyright: reportUnusedCallResult=false
# LSP server code deals with dynamic pygls types that lack full type annotations
"""LSP-based compilation server using pygls for VS Code extension.

This implementation uses the Language Server Protocol with pygls v2 to provide
dashboard compilation services to the VS Code extension.
"""

import json
import logging
from typing import Any
from urllib.parse import urlsplit, urlunsplit

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


def _params_to_dict(params: Any) -> dict[str, Any]:
    """Convert pygls params object to dict.

    In pygls v2, custom LSP requests receive params as pygls.protocol.Object (a namedtuple).
    Internal calls may pass plain dicts directly.

    Args:
        params: The params object (dict, namedtuple, or None)

    Returns:
        Dictionary representation of the params (empty dict for None)
    """
    # None is treated as empty dict so downstream validation returns structured errors
    if params is None:
        return {}

    # Already a dict - return as-is
    if isinstance(params, dict):
        return params

    # pygls.protocol.Object is a namedtuple with _asdict() method
    if hasattr(params, '_asdict') and callable(params._asdict):
        result: dict[str, Any] = params._asdict()  # pyright: ignore[reportAssignmentType]
        return result

    # If we get here, we received an unexpected type
    msg = f'Unable to convert params of type {type(params).__name__} to dict'
    raise TypeError(msg)


def _get_required_str(params_dict: dict[str, Any], key: str) -> str | None:
    """Extract a required string parameter from params dict.

    Args:
        params_dict: Dictionary of parameters
        key: The key to extract

    Returns:
        The string value if valid, None if missing or empty

    Raises:
        TypeError: If value is present but not a string
    """
    value = params_dict.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value if len(value) > 0 else None
    msg = f'Expected {key} to be str | None, got {type(value).__name__}'
    raise TypeError(msg)


def _normalize_optional_str(value: str | None) -> str | None:
    """Normalize an optional string, converting empty strings to None.

    Args:
        value: The string value or None

    Returns:
        The string if non-empty, None otherwise

    Note:
        Type safety is enforced at compile time via the type annotation.
        Unlike _get_required_str which extracts from dict[str, Any], this function
        has a typed parameter so runtime isinstance checks are unnecessary.
    """
    if value is None:
        return None
    return value if len(value) > 0 else None


def _validate_credentials(
    username: Any, password: Any, api_key: Any, ssl_verify: Any
) -> tuple[str | None, str | None, str | None, bool] | str:
    """Validate and normalize credential parameters.

    Args:
        username: Optional username value
        password: Optional password value
        api_key: Optional API key value
        ssl_verify: SSL verification flag

    Returns:
        Tuple of (username, password, api_key, ssl_verify) if valid,
        or error message string if invalid.
    """
    if (
        (username is not None and not isinstance(username, str))
        or (password is not None and not isinstance(password, str))
        or (api_key is not None and not isinstance(api_key, str))
        or not isinstance(ssl_verify, bool)
    ):
        return 'Invalid credential or ssl_verify parameter type'
    return (
        _normalize_optional_str(username),
        _normalize_optional_str(password),
        _normalize_optional_str(api_key),
        ssl_verify,
    )


def _redact_url(url: str) -> str:
    """Redact credentials from a URL for safe logging.

    Removes any username:password@ portion from the URL to prevent
    credential leakage in log files.

    Args:
        url: The URL to redact

    Returns:
        URL with credentials removed
    """
    parts = urlsplit(url)
    # Reconstruct the netloc without userinfo
    host = parts.hostname if parts.hostname is not None else ''
    if parts.port is not None:
        host = f'{host}:{parts.port}'
    return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))


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

    path = args[0]
    if not isinstance(path, str) or len(path) == 0:
        return {'success': False, 'error': 'Invalid path argument: expected non-empty string'}
    try:
        dashboard_index: int = int(args[1]) if len(args) > 1 else 0
    except (TypeError, ValueError) as e:
        return {'success': False, 'error': f'Invalid dashboard_index: {e}'}

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/compile')
def compile_custom(params: Any) -> dict[str, Any]:
    """Handle custom compilation request for a dashboard.

    Args:
        params: Object containing path and dashboard_index

    Returns:
        Dictionary with compilation result
    """
    params_dict = _params_to_dict(params)

    try:
        path = _get_required_str(params_dict, 'path')
    except TypeError as e:
        return {'success': False, 'error': str(e)}

    if path is None:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboard_index = int(params_dict.get('dashboard_index', 0))
    except (TypeError, ValueError) as e:
        return {'success': False, 'error': f'Invalid dashboard_index: {e}'}

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/getDashboards')
def get_dashboards_custom(params: Any) -> dict[str, Any]:
    """Get list of dashboards from a YAML file.

    Args:
        params: Object containing path to YAML file

    Returns:
        Dictionary with list of dashboards or error
    """
    params_dict = _params_to_dict(params)

    try:
        path = _get_required_str(params_dict, 'path')
    except TypeError as e:
        return {'success': False, 'error': str(e)}

    if path is None:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboards = load(path)
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
def get_grid_layout_custom(params: Any) -> dict[str, Any]:
    """Get grid layout information from a YAML dashboard file.

    Args:
        params: Object containing path and dashboard_index

    Returns:
        Dictionary with grid layout information or error
    """
    params_dict = _params_to_dict(params)

    try:
        path = _get_required_str(params_dict, 'path')
    except TypeError as e:
        return {'success': False, 'error': str(e)}

    if path is None:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboard_index = int(params_dict.get('dashboard_index', 0))
    except (TypeError, ValueError) as e:
        return {'success': False, 'error': f'Invalid dashboard_index: {e}'}

    try:
        result = extract_grid_layout(path, dashboard_index)
    except Exception as e:
        return {'success': False, 'error': str(e)}
    else:
        return {'success': True, 'data': result}


@server.feature('dashboard/getSchema')
def get_schema_custom(_params: Any) -> dict[str, Any]:
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


@server.feature('esql/execute')
async def execute_esql_query(params: Any) -> dict[str, Any]:
    """Execute an ES|QL query via Kibana's console proxy API.

    Args:
        params: Object containing:
            - query: ES|QL query string
            - kibana_url: Kibana base URL
            - username: Optional username
            - password: Optional password
            - api_key: Optional API key
            - ssl_verify: Whether to verify SSL

    Returns:
        Dictionary with success status and query results or error
    """
    params_dict = _params_to_dict(params)

    try:
        query = _get_required_str(params_dict, 'query')
        kibana_url = _get_required_str(params_dict, 'kibana_url')
    except TypeError as e:
        return {'success': False, 'error': str(e)}

    if query is None:
        return {'success': False, 'error': 'Missing or invalid query parameter'}

    if kibana_url is None:
        return {'success': False, 'error': 'Missing or invalid kibana_url parameter'}

    credentials = _validate_credentials(
        params_dict.get('username'),
        params_dict.get('password'),
        params_dict.get('api_key'),
        params_dict.get('ssl_verify', True),
    )
    if isinstance(credentials, str):
        return {'success': False, 'error': credentials}
    validated_username, validated_password, validated_api_key, ssl_verify = credentials

    try:
        logger.info('Executing ES|QL query via Kibana at %s', _redact_url(kibana_url))
        async with KibanaClient(
            url=kibana_url,
            username=validated_username,
            password=validated_password,
            api_key=validated_api_key,
            ssl_verify=ssl_verify,
        ) as client:
            result = await client.execute_esql(query)
        logger.debug('ES|QL query returned %d rows', result.row_count)
    except Exception as e:
        logger.exception('ES|QL execution error occurred')
        return {'success': False, 'error': f'ES|QL execution error: {e!s}'}
    else:
        return {'success': True, 'data': result.model_dump(by_alias=True, mode='json')}


@server.feature('dashboard/uploadToKibana')
async def upload_to_kibana_custom(params: Any) -> dict[str, Any]:  # noqa: PLR0911
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

    try:
        path = _get_required_str(params_dict, 'path')
        kibana_url = _get_required_str(params_dict, 'kibana_url')
    except TypeError as e:
        return {'success': False, 'error': str(e)}

    try:
        dashboard_index = int(params_dict.get('dashboard_index', 0))
    except (TypeError, ValueError) as e:
        return {'success': False, 'error': f'Invalid dashboard_index: {e}'}

    if path is None or kibana_url is None:
        return {'success': False, 'error': 'Missing required parameters (path and kibana_url)'}

    credentials = _validate_credentials(
        params_dict.get('username'),
        params_dict.get('password'),
        params_dict.get('api_key'),
        params_dict.get('ssl_verify', True),
    )
    if isinstance(credentials, str):
        return {'success': False, 'error': credentials}
    validated_username, validated_password, validated_api_key, ssl_verify = credentials

    try:
        # Compile the dashboard first
        logger.info('Compiling dashboard from %s (index %d)', path, dashboard_index)
        compile_result = _compile_dashboard(path, dashboard_index)
        if compile_result['success'] is not True:
            logger.error('Compilation failed: %s', compile_result.get('error'))
            return compile_result

        # Create NDJSON content
        ndjson_content = json.dumps(compile_result['data'])
        logger.debug('Generated NDJSON content: %d bytes', len(ndjson_content))

        # Create Kibana client and upload
        logger.info('Uploading dashboard to Kibana at %s', _redact_url(kibana_url))
        async with KibanaClient(
            url=kibana_url,
            username=validated_username,
            password=validated_password,
            api_key=validated_api_key,
            ssl_verify=ssl_verify,
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
                    return {'success': True, 'dashboard_url': dashboard_url, 'dashboard_id': dashboard_ids[0]}

                logger.error('No dashboard found in upload results')
                return {'success': False, 'error': 'No dashboard found in upload results'}

            error_messages = [str(err) for err in result.errors]
            logger.error('Upload failed with errors: %s', '; '.join(error_messages))
            return {'success': False, 'error': f'Upload failed: {"; ".join(error_messages)}'}

    except Exception as e:
        logger.exception('Upload error occurred')
        return {'success': False, 'error': f'Upload error: {e!s}'}


def start_server() -> None:
    """Start the LSP server via stdio."""
    server.start_io()


if __name__ == '__main__':
    start_server()
