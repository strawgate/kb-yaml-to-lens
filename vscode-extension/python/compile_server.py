"""LSP-based compilation server using pygls for VS Code extension.

This implementation uses the Language Server Protocol with pygls v2 to provide
dashboard compilation services to the VS Code extension.
"""

import sys
from pathlib import Path
from typing import Any

import cattrs
from lsprotocol import types
from pygls.lsp.server import LanguageServer

# Add the project source directory to the path
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / 'src'
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from dashboard_compiler.dashboard_compiler import load, render
except ImportError as e:
    msg = (
        f'Failed to import dashboard_compiler. Make sure the dashboard_compiler '
        f'package is installed or the src directory exists at {src_path}'
    )
    raise ImportError(msg) from e

# Initialize the language server
server = LanguageServer('dashboard-compiler', 'v0.1')


def _params_to_dict(params: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
    """Convert pygls params object to dict.

    In pygls v2, params can be passed as:
    - Plain dicts (from internal requests)
    - namedtuples (from pygls.protocol.Object)
    - LSPObject instances (from external LSP clients like vscode-languageclient)
    - cattrs-structured objects (from some LSP requests)

    Args:
        params: The params object

    Returns:
        Dictionary representation of the params
    """
    # Already a dict - fast path
    if isinstance(params, dict):
        if not all(isinstance(key, str) for key in params):  # pyright: ignore[reportUnknownVariableType]
            msg = 'Params dictionary keys must be strings'
            raise TypeError(msg)
        return params  # pyright: ignore[reportUnknownVariableType]

    # Check if it's a namedtuple (has _asdict method)
    # This handles pygls.protocol.Object and other namedtuples
    if hasattr(params, '_asdict') and callable(params._asdict):  # pyright: ignore[reportAny]
        return params._asdict()  # pyright: ignore[reportAny]

    # Try cattrs.unstructure (handles attrs classes and some LSP types)
    unstructured = cattrs.unstructure(params)  # pyright: ignore[reportAny]
    if isinstance(unstructured, dict):
        return unstructured  # pyright: ignore[reportUnknownVariableType]

    # Try vars() to extract instance variables (works for plain objects with __dict__)
    try:
        params_dict = vars(params)  # pyright: ignore[reportAny]
        if isinstance(params_dict, dict):
            return params_dict  # pyright: ignore[reportAny]
    except TypeError:
        # vars() failed, object doesn't have __dict__
        pass

    # Last resort: try to convert to dict if it has dict-like methods
    if hasattr(params, 'keys') and hasattr(params, 'values'):
        try:
            return dict(params)  # pyright: ignore[reportAny]
        except Exception:
            pass

    # If all else fails, raise an informative error
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
            {'index': i, 'title': dashboard.name or f'Dashboard {i + 1}', 'description': dashboard.description or ''}
            for i, dashboard in enumerate(dashboards)
        ]
    except Exception as e:
        return {'success': False, 'error': str(e)}
    else:
        return {'success': True, 'data': dashboard_list}


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Handle file save events and notify client of changes.

    Args:
        ls: Language server instance
        params: Save event parameters
    """
    file_path = params.text_document.uri
    ls.protocol.notify('dashboard/fileChanged', {'uri': file_path})


if __name__ == '__main__':
    server.start_io()
