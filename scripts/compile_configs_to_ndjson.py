import logging
import sys
from pathlib import Path

from dashboard_compiler.dashboard_compiler import load, render

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent

INPUT_DIR = project_root / 'inputs'
SCENARIO_DIR = project_root / 'test/dashboards/scenarios'
OUTPUT_DIR = project_root / 'output'


def write_ndjson(output_path: Path, lines: list[str], overwrite: bool = True) -> None:
    """Write a list of JSON strings to an NDJSON file.

    Args:
        lines: List of JSON strings to write.
        output_path: Path to the output NDJSON file.
        overwrite: Whether to overwrite the output file if it exists.

    """
    if overwrite and output_path.exists():
        output_path.unlink()

    with Path(output_path).open('w') as f:
        f.writelines(line + '\n' for line in lines)


def compile_and_format(yaml_path: Path) -> list[str]:
    """Compile dashboard YAML, formats the output dictionaries for Kibana import, and returns them as compressed JSON strings.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        List of compressed JSON strings for NDJSON lines, or empty list if compilation fails.

    """
    try:
        msg = f'Compiling: {yaml_path.relative_to(project_root)}'
        logger.info(msg)
        dashboards = load(str(yaml_path))
        json_lines = []
        for dashboard in dashboards:
            dashboard_kbn_model = render(dashboard)
            json_lines.append(dashboard_kbn_model.model_dump_json(by_alias=True))
        return json_lines

    except FileNotFoundError:
        msg = f'Error: YAML file not found: {yaml_path}'
        logger.exception(msg)
        return []
    except Exception as e:
        msg = f'Error compiling {yaml_path}: {e}'
        logger.exception(msg)
        return []


def get_scenarios() -> list[Path]:
    """Retrieve a list of scenario YAML files from the SCENARIO_DIR.

    Returns:
        A list of Path objects pointing to the scenario YAML files.

    """
    if not SCENARIO_DIR.is_dir():
        msg = f'Error: Scenario directory not found: {SCENARIO_DIR}'
        logger.error(msg)
        sys.exit(1)

    # Use rglob to find YAML files recursively
    yaml_files = sorted(SCENARIO_DIR.rglob('*.yaml'))

    if not yaml_files:
        msg = f'Warning: No YAML files found in {SCENARIO_DIR}'
        logger.warning(msg)

    return yaml_files


def get_inputs() -> list[Path]:
    """Retrieve a list of input YAML files from the INPUT_DIR.

    Returns:
        A list of Path objects pointing to the input YAML files.

    """
    if not INPUT_DIR.is_dir():
        msg = f'Error: Input directory not found: {INPUT_DIR}'
        logger.error(msg)
        sys.exit(1)

    # Use rglob to find YAML files recursively
    yaml_files = sorted(INPUT_DIR.rglob('*.yaml'))

    if not yaml_files:
        msg = f'Warning: No YAML files found in {INPUT_DIR}'
        logger.warning(msg)

    return yaml_files


def main() -> None:
    """Find config YAMLs, compile them, and write the NDJSON file."""
    # Create the output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = [*get_scenarios()]

    ndjson_lines = []

    for scenario in scenarios:
        yaml_file = scenario.resolve()
        try:
            compressed_lines = compile_and_format(yaml_file)
        except Exception as e:
            msg = f'Error compiling {yaml_file}: {e}'
            logger.exception(msg)
            continue

        if compressed_lines:
            # write a standalone ndjson file for each scenario
            filename = scenario.parent.stem
            file_path = OUTPUT_DIR / f'{filename}.ndjson'
            msg = f'Writing compiled dashboard to: {file_path.relative_to(project_root)}'
            logger.info(msg)
            write_ndjson(file_path, compressed_lines, overwrite=True)
            ndjson_lines.extend(compressed_lines)

    if ndjson_lines:
        # Write a joined NDJSON lines to the output file
        file_path = OUTPUT_DIR / 'compiled_dashboards.ndjson'
        write_ndjson(file_path, ndjson_lines, overwrite=True)
    else:
        msg = '\nNo valid YAML configurations found or compiled.'
        logger.info(msg)


if __name__ == '__main__':
    main()
