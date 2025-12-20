"""Command-line interface for the dashboard compiler."""

import asyncio
import logging
import webbrowser
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

logger = logging.getLogger(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Create a Rich console for output
console = Console()

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / 'inputs'
DEFAULT_SCENARIO_DIR = PROJECT_ROOT / 'tests/dashboards/scenarios'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'output'

# Icons for consistent output
ICON_SUCCESS = '✓'
ICON_ERROR = '✗'
ICON_WARNING = '⚠'
ICON_UPLOAD = '📤'
ICON_BROWSER = '🌐'


def create_error_table(errors: list[dict | str]) -> Table:
    """Create a Rich table to display errors.

    Args:
        errors: List of error messages or error dicts.

    Returns:
        A formatted Rich table with error messages.

    """
    error_table = Table(show_header=True, header_style='bold red')
    error_table.add_column('Error', style='red')

    for error in errors:
        error_msg = error.get('error', {}).get('message', str(error)) if isinstance(error, dict) else str(error)
        error_table.add_row(error_msg)

    return error_table


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


def compile_yaml_to_json(yaml_path: Path) -> tuple[list[str], str | None]:
    """Compile dashboard YAML to JSON strings for NDJSON.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        Tuple of (list of JSON strings for NDJSON lines, error message or None).

    """
    try:
        dashboards = load(str(yaml_path))
        json_lines = []
        for dashboard in dashboards:
            dashboard_kbn_model = render(dashboard)
            json_lines.append(dashboard_kbn_model.model_dump_json(by_alias=True))
        return json_lines, None
    except FileNotFoundError:
        return [], f'YAML file not found: {yaml_path}'
    except (ValueError, TypeError, KeyError) as e:
        return [], f'Error compiling {yaml_path}: {e}'


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

    if not yaml_files:
        console.print(f'[yellow]{ICON_WARNING}[/yellow] Warning: No YAML files found in {directory}', style='yellow')

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
        console.print('[yellow]No YAML files to compile.[/yellow]')
        return

    # Compile all files with progress bar
    ndjson_lines = []
    errors = []

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task('Compiling dashboards...', total=len(yaml_files))

        for yaml_file in yaml_files:
            # Show relative path if within project, otherwise show full path
            try:
                display_path = yaml_file.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = yaml_file
            progress.update(task, description=f'Compiling: {display_path}')
            compiled_jsons, error = compile_yaml_to_json(yaml_file)

            if compiled_jsons:
                # Write individual file
                filename = yaml_file.parent.stem
                individual_file = output_dir / f'{filename}.ndjson'
                write_ndjson(individual_file, compiled_jsons, overwrite=True)
                ndjson_lines.extend(compiled_jsons)
            elif error:
                errors.append(error)

            progress.advance(task)

    # Show results
    if ndjson_lines:
        console.print(f'[green]{ICON_SUCCESS}[/green] Successfully compiled {len(ndjson_lines)} dashboard(s)')

    if errors:
        console.print(f'\n[yellow]{ICON_WARNING}[/yellow] Encountered {len(errors)} error(s):', style='yellow')
        for error in errors:
            console.print(f'  [red]•[/red] {error}', style='red')

    if not ndjson_lines:
        console.print(f'[red]{ICON_ERROR}[/red] No valid YAML configurations found or compiled.', style='red')
        return

    # Write combined file
    combined_file = output_dir / output_file
    write_ndjson(combined_file, ndjson_lines, overwrite=True)
    # Show relative path if within project, otherwise show full path
    try:
        display_path = combined_file.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = combined_file
    console.print(f'[green]{ICON_SUCCESS}[/green] Wrote combined file: {display_path}')

    # Upload to Kibana if requested
    if upload:
        console.print(f'\n[blue]{ICON_UPLOAD}[/blue] Uploading to Kibana at {kibana_url}...')
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

    Raises:
        click.ClickException: If upload fails.

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
            console.print(f'[green]{ICON_SUCCESS}[/green] Successfully uploaded {success_count} object(s) to Kibana')

            # Extract dashboard IDs
            dashboard_ids = [obj['id'] for obj in result.get('successResults', []) if obj.get('type') == 'dashboard']

            if dashboard_ids and open_browser:
                dashboard_url = client.get_dashboard_url(dashboard_ids[0])
                console.print(f'[blue]{ICON_BROWSER}[/blue] Opening dashboard: {dashboard_url}')
                webbrowser.open_new_tab(dashboard_url)

            # Show errors if any using a table
            if result.get('errors'):
                console.print(f'\n[yellow]{ICON_WARNING}[/yellow] Encountered {len(result["errors"])} error(s):')
                console.print(create_error_table(result['errors']))
        else:
            console.print(f'[red]{ICON_ERROR}[/red] Upload failed', style='red')
            if result.get('errors'):
                console.print(create_error_table(result['errors']))
            msg = 'Upload to Kibana failed'
            raise click.ClickException(msg)

    except (OSError, ValueError) as e:
        msg = f'Error uploading to Kibana: {e}'
        raise click.ClickException(msg) from e


if __name__ == '__main__':
    cli()
