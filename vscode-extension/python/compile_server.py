"""Simple stdio-based compilation server for VS Code extension."""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import dashboard_compiler
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from dashboard_compiler.dashboard_compiler import load, render


def compile_dashboard(yaml_path: str) -> dict:
    """Compile dashboard and return result.

    Args:
        yaml_path: Path to the YAML dashboard file.

    Returns:
        dict: Result dictionary with 'success' and either 'data' or 'error'.
    """
    try:
        dashboard = load(yaml_path)
        kbn_dashboard = render(dashboard)
        return {'success': True, 'data': kbn_dashboard.model_dump(by_alias=True, mode='json')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    """Run the main server loop reading JSON requests from stdin and writing responses to stdout."""
    # Ensure stdout is line-buffered
    sys.stdout.reconfigure(line_buffering=True)

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

                result = compile_dashboard(params['path'])
                result['id'] = request_id
                sys.stdout.write(json.dumps(result) + '\n')
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
