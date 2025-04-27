import json
import sys
from pathlib import Path

from dashboard_compiler.compile.compile import compile_yaml_dashboard

project_root = Path(__file__).parent.parent


SCENARIO_DIR = project_root / "tests/scenarios"
OUTPUT_DIR = project_root / "output"


def write_ndjson(output_path: Path, lines: list[str], overwrite: bool = True) -> None:
    """
    Writes a list of JSON strings to an NDJSON file.

    Args:
        lines: List of JSON strings to write.
        output_path: Path to the output NDJSON file.
    """
    if overwrite and output_path.exists():
        output_path.unlink()

    with open(output_path, "w") as f:
        for line in lines:
            f.write(line + "\n")


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
        dashboard_dict = compile_yaml_dashboard(str(yaml_path))

        compressed_json = json.dumps(dashboard_dict.model_dump(serialize_as_any=True, exclude_none=True), separators=(",", ":"))

        return compressed_json

    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error compiling {yaml_path}: {e}", file=sys.stderr)
        # print(traceback.format_exc(), file=sys.stderr) # Uncomment for full traceback
        return None


def get_scenarios() -> list[Path]:
    """
    Retrieves a list of scenario YAML files from the SCENARIO_DIR.

    Returns:
        A list of Path objects pointing to the scenario YAML files.
    """
    if not SCENARIO_DIR.is_dir():
        print(f"Error: Scenario directory not found: {SCENARIO_DIR}", file=sys.stderr)
        sys.exit(1)

    # Use rglob to find YAML files recursively
    yaml_files = sorted(SCENARIO_DIR.rglob("*.yaml"))

    if not yaml_files:
        print(f"Warning: No YAML files found in {SCENARIO_DIR}", file=sys.stderr)

    return yaml_files


def main():
    """
    Main function to find config YAMLs, compile them, and write the NDJSON file.
    """

    # Create the output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = get_scenarios()

    ndjson_lines = []

    for scenario in scenarios:
        yaml_file = scenario.resolve()
        try:
            compressed_line = compile_and_format(yaml_file)
        except Exception:
            continue
        if compressed_line:
            # write a standalone ndjson file for each scenario
            filename = scenario.parent.stem
            file_path = OUTPUT_DIR / f"{filename}.ndjson"
            print(f"Writing compiled dashboard to: {file_path.relative_to(project_root)}")
            write_ndjson(file_path, [compressed_line], overwrite=True)
            ndjson_lines.append(compressed_line)

    if ndjson_lines:
        # Write a joined NDJSON lines to the output file
        file_path = OUTPUT_DIR / "compiled_dashboards.ndjson"
        write_ndjson(file_path, ndjson_lines, overwrite=True)
    else:
        print("\nNo valid YAML configurations found or compiled.")


if __name__ == "__main__":
    main()
