"""Command-line interface for the dashboard compiler."""

import asyncio
import logging
import sys
import webbrowser
from pathlib import Path

import click

from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient

logger = logging.getLogger(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Get project root (parent of dashboard_compiler)
project_root = Path(__file__).parent.parent

DEFAULT_INPUT_DIR = project_root / 'inputs'
DEFAULT_SCENARIO_DIR = project_root / 'tests/dashboards/scenarios'
DEFAULT_OUTPUT_DIR = project_root / 'output'


def write_ndjson(output_path: Path, lines: list[str], overwrite: bool = True) -> None:
    """Write a list of JSON strings to an NDJSON file.

    Args:
        output_path: Path to the output NDJSON file.
        lines: List of JSON strings to write.
        overwrite: Whether to overwrite the output file if it exists.

    """
    if overwrite and output_path.exists():
        output_path.unlink()

    with output_path.open('w') as f:
        for line in lines:
            f.write(line + '\n')


def compile_yaml_to_json(yaml_path: Path) -> str | None:
    """Compile a dashboard YAML to a JSON string for NDJSON.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        The JSON string for the NDJSON line, or None if compilation fails.

    """
    try:
        click.echo(f'Compiling: {yaml_path.relative_to(project_root)}')
        dashboard_model = load(str(yaml_path))
        dashboard_kbn_model = render(dashboard_model)
        return dashboard_kbn_model.model_dump_json(by_alias=True)
    except FileNotFoundError:
        click.echo(f'Error: YAML file not found: {yaml_path}', err=True)
        return None
    except (ValueError, TypeError, KeyError) as e:
        click.echo(f'Error compiling {yaml_path}: {e}', err=True)
        return None


def get_yaml_files(directory: Path) -> list[Path]:
    """Get all YAML files from a directory recursively.

    Args:
        directory: Directory to search for YAML files.

    Returns:
        List of Path objects pointing to YAML files.

    """
    if not directory.is_dir():
        click.echo(f'Error: Directory not found: {directory}', err=True)
        sys.exit(1)

    yaml_files = sorted(directory.rglob('*.yaml'))

    if not yaml_files:
        click.echo(f'Warning: No YAML files found in {directory}', err=True)

    return yaml_files


@click.group()
@click.version_option(version='0.1.0')
def cli() -> None:
    """Kibana Dashboard Compiler - Compile YAML dashboards to Kibana format."""


@cli.command('compile')
@click.option(
    '--input-dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=DEFAULT_SCENARIO_DIR,
    help='Directory containing YAML dashboard files',
)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help='Directory to write compiled NDJSON files',
)
@click.option(
    '--output-file',
    type=str,
    default='compiled_dashboards.ndjson',
    help='Name of the combined output NDJSON file',
)
@click.option(
    '--upload',
    is_flag=True,
    help='Upload compiled dashboards to Kibana after compilation',
)
@click.option(
    '--kibana-url',
    type=str,
    envvar='KIBANA_URL',
    default='http://localhost:5601',
    help='Kibana base URL (can also set KIBANA_URL env var)',
)
@click.option(
    '--kibana-username',
    type=str,
    envvar='KIBANA_USERNAME',
    help='Kibana username for basic auth (can also set KIBANA_USERNAME env var)',
)
@click.option(
    '--kibana-password',
    type=str,
    envvar='KIBANA_PASSWORD',
    help='Kibana password for basic auth (can also set KIBANA_PASSWORD env var)',
)
@click.option(
    '--kibana-api-key',
    type=str,
    envvar='KIBANA_API_KEY',
    help='Kibana API key for authentication (can also set KIBANA_API_KEY env var)',
)
@click.option(
    '--no-browser',
    is_flag=True,
    help='Do not open browser after upload',
)
@click.option(
    '--overwrite/--no-overwrite',
    default=True,
    help='Overwrite existing dashboards in Kibana',
)
def compile_dashboards(  # noqa: PLR0913
    input_dir: Path,
    output_dir: Path,
    output_file: str,
    upload: bool,
    kibana_url: str,
    kibana_username: str | None,
    kibana_password: str | None,
    kibana_api_key: str | None,
    no_browser: bool,
    overwrite: bool,
) -> None:
    """Compile YAML dashboard configurations to NDJSON format.

    This command finds all YAML files in the input directory, compiles them
    to Kibana's JSON format, and outputs them as NDJSON files.

    Optionally, you can upload the compiled dashboards directly to Kibana
    using the --upload flag.
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all YAML files
    yaml_files = get_yaml_files(input_dir)
    if not yaml_files:
        click.echo('No YAML files to compile.')
        return

    # Compile all files
    ndjson_lines = []
    for yaml_file in yaml_files:
        compiled_json = compile_yaml_to_json(yaml_file)
        if compiled_json:
            # Write individual file
            filename = yaml_file.parent.stem
            individual_file = output_dir / f'{filename}.ndjson'
            write_ndjson(individual_file, [compiled_json], overwrite=True)
            click.echo(f'  ✓ Wrote: {individual_file.relative_to(project_root)}')
            ndjson_lines.append(compiled_json)

    if not ndjson_lines:
        click.echo('No valid YAML configurations found or compiled.', err=True)
        return

    # Write combined file
    combined_file = output_dir / output_file
    write_ndjson(combined_file, ndjson_lines, overwrite=True)
    click.echo(f'\n✓ Compiled {len(ndjson_lines)} dashboard(s) to: {combined_file.relative_to(project_root)}')

    # Upload to Kibana if requested
    if upload:
        click.echo(f'\n📤 Uploading to Kibana at {kibana_url}...')
        asyncio.run(
            upload_to_kibana(
                combined_file,
                kibana_url,
                kibana_username,
                kibana_password,
                kibana_api_key,
                overwrite,
                not no_browser,
            )
        )


async def upload_to_kibana(
    ndjson_file: Path,
    kibana_url: str,
    username: str | None,
    password: str | None,
    api_key: str | None,
    overwrite: bool,
    open_browser: bool,
) -> None:
    """Upload NDJSON file to Kibana.

    Args:
        ndjson_file: Path to NDJSON file to upload
        kibana_url: Kibana base URL
        username: Basic auth username
        password: Basic auth password
        api_key: API key for authentication
        overwrite: Whether to overwrite existing objects
        open_browser: Whether to open browser after successful upload

    """
    client = KibanaClient(
        url=kibana_url,
        username=username,
        password=password,
        api_key=api_key,
    )

    try:
        result = await client.upload_ndjson(ndjson_file, overwrite=overwrite)

        if result.get('success'):
            success_count = result.get('successCount', 0)
            click.echo(f'✓ Successfully uploaded {success_count} object(s) to Kibana')

            # Extract dashboard IDs
            dashboard_ids = [obj['id'] for obj in result.get('successResults', []) if obj.get('type') == 'dashboard']

            if dashboard_ids and open_browser:
                dashboard_url = client.get_dashboard_url(dashboard_ids[0])
                click.echo(f'🌐 Opening dashboard: {dashboard_url}')
                webbrowser.open_new_tab(dashboard_url)

            # Show errors if any
            if result.get('errors'):
                click.echo(f'\n⚠ Encountered {len(result["errors"])} error(s):', err=True)
                for error in result['errors']:
                    click.echo(f'  - {error.get("error", {}).get("message", error)}', err=True)
        else:
            click.echo('✗ Upload failed', err=True)
            if result.get('errors'):
                for error in result['errors']:
                    click.echo(f'  - {error.get("error", {}).get("message", error)}', err=True)
            sys.exit(1)

    except (OSError, ValueError) as e:
        click.echo(f'✗ Error uploading to Kibana: {e}', err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
