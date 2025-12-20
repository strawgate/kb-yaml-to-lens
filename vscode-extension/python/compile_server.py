"""Simple stdio-based compilation server for VS Code extension."""

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import dashboard_compiler
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
        return {
            "success": True,
            "data": kbn_dashboard.model_dump(by_alias=True, mode='json')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main server loop - reads JSON requests from stdin, writes responses to stdout."""
    # Ensure stdout is line-buffered
    sys.stdout.reconfigure(line_buffering=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            request_id = request.get("id", 0)
            method = request.get("method")
            params = request.get("params", {})

            if method == "compile":
                result = compile_dashboard(params["path"])
                result["id"] = request_id
                sys.stdout.write(json.dumps(result) + "\n")
                sys.stdout.flush()
            else:
                error_response = {
                    "id": request_id,
                    "success": False,
                    "error": f"Unknown method: {method}"
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            error_response = {
                "id": 0,
                "success": False,
                "error": f"Server error: {str(e)}"
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
