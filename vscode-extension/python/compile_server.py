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


# Method 1: Using workspace/executeCommand (standard LSP approach)
@server.command('dashboard.compile')
def compile_command(_ls: LanguageServer, args: list) -> dict:
    """Compile a dashboard using the workspace/executeCommand pattern.

    This is the "standard" LSP way - using executeCommand for custom operations.
    The client would call this via: client.sendRequest('workspace/executeCommand',
    {command: 'dashboard.compile', arguments: [path, dashboard_index]})
    """
    if not args or len(args) < 1:
        return {'success': False, 'error': 'Missing path argument'}

    path = args[0]
    dashboard_index = args[1] if len(args) > 1 else 0

    return _compile_dashboard(path, dashboard_index)


# Method 2: Custom request handler (more direct, non-standard LSP)
@server.feature('dashboard/compile')
def compile_custom(params: dict) -> dict:
    """Handle custom compilation request for a dashboard.

    This is a custom LSP method (not in the standard LSP spec).
    The client would call this via: client.sendRequest('dashboard/compile',
    {path: '...', dashboard_index: 0})

    This is cleaner than executeCommand but requires custom protocol extension.
    """
    path = params.get('path', '')
    dashboard_index = params.get('dashboard_index', 0)

    return _compile_dashboard(path, dashboard_index)


@server.feature('dashboard/getDashboards')
def get_dashboards_custom(params: dict) -> dict:
    """Get list of dashboards from a YAML file.

    The client would call this via: client.sendRequest('dashboard/getDashboards',
    {path: '...'})
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


# Optional: File watching support
# LSP servers can watch for file changes and send notifications to the client
@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Handle file save events.

    This can be used to automatically recompile when a YAML file is saved.
    The server can send a custom notification back to the client.
    """
    # Get the file path from the URI
    file_path = params.text_document.uri

    # Send a custom notification to the client that the file was saved
    # The client can then trigger a recompilation
    ls.send_notification('dashboard/fileChanged', {'uri': file_path})


# Optional: Diagnostics support
# LSP can provide real-time error checking
@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
async def did_open(_ls: LanguageServer, params: types.DidOpenTextDocumentParams) -> None:
    """Validate the dashboard when a file is opened.

    This demonstrates how LSP can provide real-time diagnostics.
    """
    # This would be called when a YAML file is opened
    # We could validate it and send diagnostics (errors/warnings) back


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(_ls: LanguageServer, params: types.DidChangeTextDocumentParams) -> None:
    """Validate the dashboard as it changes.

    This could provide real-time validation feedback in the editor.
    """
    # This would be called as the user types
    # We could validate and send diagnostics back


if __name__ == '__main__':
    # Start the server in stdio mode (same transport as current implementation)
    server.start_io()
