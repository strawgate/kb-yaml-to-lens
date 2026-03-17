"""Shared constants and helpers used by both local and remote CLI commands."""

from pathlib import Path

import rich_click as click

from dashboard_compiler.cli_output import print_warning

# Path constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / 'inputs'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'output'


def get_yaml_files(directory: Path) -> list[Path]:
    """Get all YAML files from a directory recursively.

    Args:
        directory: Directory to search for YAML files.

    Returns:
        List of Path objects pointing to YAML files.

    Raises:
        click.ClickException: If directory is not found.

    """
    if not directory.is_dir():
        msg = f'Directory not found: {directory}'
        raise click.ClickException(msg)

    yaml_files = sorted(directory.rglob('*.yaml'))

    if len(yaml_files) == 0:
        print_warning(f'No YAML files found in {directory}')

    return yaml_files
