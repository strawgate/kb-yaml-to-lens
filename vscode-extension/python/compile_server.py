"""Simple stdio-based compilation server for VS Code extension."""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import dashboard_compiler
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from dashboard_compiler.dashboard_compiler import load, render


def compile_dashboard(yaml_path: str, dashboard_index: int = 0) -> dict:
    """Compile dashboard and return result.

    Args:
        yaml_path: Path to the YAML dashboard file.
        dashboard_index: Index of the dashboard to compile (default: 0).

    Returns:
        dict: Result dictionary with 'success' and either 'data' or 'error'.
    """
    try:
        dashboards = load(yaml_path)
        if not dashboards:
            return {'success': False, 'error': 'No dashboards found in YAML file'}

        # Validate dashboard index
        if dashboard_index < 0 or dashboard_index >= len(dashboards):
            return {'success': False, 'error': f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'}

        dashboard = dashboards[dashboard_index]
        kbn_dashboard = render(dashboard)
        return {'success': True, 'data': kbn_dashboard.model_dump(by_alias=True, mode='json')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    """Run the main server loop reading JSON requests from stdin and writing responses to stdout."""
    # Ensure stdout is line-buffered
    sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]

    for line in sys.stdin:
        request_id = 0  # Initialize request_id before parsing
        try:
            request = json.loads(line)
            request_id = request.get('id', 0)
            method = request.get('method')
            params = request.get('params', {})

            if method == 'compile':
                # Validate required parameters
                if 'path' not in params:
                    error_response = {'id': request_id, 'success': False, 'error': 'Missing required parameter: path'}
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    continue

                dashboard_index = params.get('dashboard_index', 0)
                result = compile_dashboard(params['path'], dashboard_index)
                result['id'] = request_id
                sys.stdout.write(json.dumps(result) + '\n')
                sys.stdout.flush()
            elif method == 'get_dashboards':
                # New method to get list of dashboards
                if 'path' not in params:
                    error_response = {'id': request_id, 'success': False, 'error': 'Missing required parameter: path'}
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    continue

                try:
                    dashboards = load(params['path'])
                    dashboard_list = [
                        {'index': i, 'title': dashboard.name or f'Dashboard {i + 1}', 'description': dashboard.description or ''}
                        for i, dashboard in enumerate(dashboards)
                    ]
                    result = {'id': request_id, 'success': True, 'data': dashboard_list}
                    sys.stdout.write(json.dumps(result) + '\n')
                    sys.stdout.flush()
                except Exception as e:
                    error_response = {'id': request_id, 'success': False, 'error': str(e)}
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
            else:
                error_response = {'id': request_id, 'success': False, 'error': f'Unknown method: {method}'}
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
        except Exception as e:
            # Use the parsed request_id instead of 0
            error_response = {'id': request_id, 'success': False, 'error': f'Server error: {e!s}'}
            sys.stdout.write(json.dumps(error_response) + '\n')
            sys.stdout.flush()


if __name__ == '__main__':
    main()
