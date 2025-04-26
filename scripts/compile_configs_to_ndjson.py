import json
from pathlib import Path
import sys
from dashboard_compiler.compile import (
    compile_dashboard,
)

# Add project root to sys.path to allow importing dashboard_compiler
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


CONFIG_DIR = project_root / "configs"
OUTPUT_FILE = project_root / "kibana_import.ndjson"


def compile_and_format(yaml_path: Path) -> str | None:
    """
    Compiles a dashboard YAML, formats the output dictionary for Kibana import,
    and returns it as a compressed JSON string.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        The compressed JSON string for the NDJSON line, or None if compilation fails.
    """
    try:
        print(f"Compiling: {yaml_path.relative_to(project_root)}")
        # compile_dashboard_to_testable_dict returns the dictionary representation
        dashboard_dict = compile_dashboard(str(yaml_path))

        compressed_json = json.dumps(dashboard_dict, separators=(",", ":"))

        return compressed_json

    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error compiling {yaml_path}: {e}", file=sys.stderr)
        # print(traceback.format_exc(), file=sys.stderr) # Uncomment for full traceback
        return None


def main():
    """
    Main function to find config YAMLs, compile them, and write the NDJSON file.
    """
    if not CONFIG_DIR.is_dir():
        print(f"Error: Config directory not found: {CONFIG_DIR}", file=sys.stderr)
        sys.exit(1)

    ndjson_lines = []
    # Use rglob to find YAML files recursively
    yaml_files = sorted(CONFIG_DIR.rglob("*.yaml"))

    if not yaml_files:
        print(f"Warning: No YAML files found in {CONFIG_DIR}", file=sys.stderr)

    for yaml_file in yaml_files:
        compressed_line = compile_and_format(yaml_file)
        if compressed_line:
            ndjson_lines.append(compressed_line)

    if ndjson_lines:
        try:
            # Write each compressed JSON object followed by a newline character

            if OUTPUT_FILE.exists():
                OUTPUT_FILE.unlink()  # Remove the file if it exists

            with open(OUTPUT_FILE, "w") as f:
                for line in ndjson_lines:
                    f.write(line + "\n")  # Use '\n' for actual newline
            print(f"\nSuccessfully wrote compiled dashboards to: {OUTPUT_FILE}")
        except IOError as e:
            print(
                f"Error: Could not write to output file {OUTPUT_FILE}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print("\nNo valid YAML configurations found or compiled.")


if __name__ == "__main__":
    main()
