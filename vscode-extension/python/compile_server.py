"""LSP-based compilation server using pygls for VS Code extension.

This implementation uses the Language Server Protocol with pygls to provide
dashboard compilation services to the VS Code extension.
"""

import sys
from pathlib import Path

from lsprotocol import types
from pygls.server import LanguageServer

# Add the src directory to the path so we can import dashboard_compiler
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from dashboard_compiler.dashboard_compiler import load, render

# Create the language server instance
server = LanguageServer('dashboard-compiler', 'v0.1')


def _compile_dashboard(path: str, dashboard_index: int = 0) -> dict:
    """Compile a dashboard at the given path and index.

    Args:
        path: Path to the YAML file containing dashboards
        dashboard_index: Index of the dashboard to compile (default: 0)

    Returns:
        Dictionary with success status and either data or error message
    """
    if not path:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboards = load(path)
        if not dashboards:
            return {'success': False, 'error': 'No dashboards found in YAML file'}

        if dashboard_index < 0 or dashboard_index >= len(dashboards):
            return {'success': False, 'error': f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'}

        dashboard = dashboards[dashboard_index]
        kbn_dashboard = render(dashboard)
        return {'success': True, 'data': kbn_dashboard.model_dump(by_alias=True, mode='json')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@server.command('dashboard.compile')
def compile_command(_ls: LanguageServer, args: list) -> dict:
    """Compile a dashboard using the workspace/executeCommand pattern.

    Args:
        args: List containing [path, dashboard_index (optional)]

    Returns:
        Dictionary with compilation result
    """
    if not args or len(args) < 1:
        return {'success': False, 'error': 'Missing path argument'}

    path = args[0]
    # Ensure dashboard_index is an integer
    dashboard_index = int(args[1]) if len(args) > 1 else 0

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/compile')
def compile_custom(params: dict) -> dict:
    """Handle custom compilation request for a dashboard.

    Args:
        params: Dictionary containing path and dashboard_index

    Returns:
        Dictionary with compilation result
    """
    path = params.get('path', '')
    # Ensure dashboard_index is an integer
    dashboard_index = int(params.get('dashboard_index', 0))

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/getDashboards')
def get_dashboards_custom(params: dict) -> dict:
    """Get list of dashboards from a YAML file.

    Args:
        params: Dictionary containing path to YAML file

    Returns:
        Dictionary with list of dashboards or error
    """
    path = params.get('path')

    if not path:
        return {'success': False, 'error': 'Missing path parameter'}

    try:
        dashboards = load(path)
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
    ls.send_notification('dashboard/fileChanged', {'uri': file_path})


if __name__ == '__main__':
    server.start_io()
