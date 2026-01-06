"""Command-line interface for the dashboard compiler."""

import asyncio
import logging
import webbrowser
from pathlib import Path

import aiohttp
import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient, SavedObjectError
from dashboard_compiler.tools.disassemble import disassemble_dashboard, parse_ndjson

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(message)s')

console = Console()
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / 'inputs'
DEFAULT_SCENARIO_DIR = PROJECT_ROOT / 'tests/dashboards/scenarios'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'output'

ICON_SUCCESS = '✓'
ICON_ERROR = '✗'
ICON_WARNING = '⚠'
ICON_UPLOAD = '📤'
ICON_BROWSER = '🌐'


def create_error_table(errors: list[SavedObjectError]) -> Table:
    """Create a Rich table to display errors.

    Args:
        errors: List of SavedObjectError models from Kibana API.

    Returns:
        A formatted Rich table with error messages.

    """
    error_table = Table(show_header=True, header_style='bold red')
    error_table.add_column('Error', style='red')

    for error in errors:
        error_msg = _extract_error_message(error)
        error_table.add_row(error_msg)

    return error_table


def _extract_error_message(error: SavedObjectError) -> str:
    if error.error:
        message: str | None = error.error.get('message')
        if message:
            return message
    if error.message:
        return error.message
    return str(error)


def write_ndjson(output_path: Path, lines: list[str], overwrite: bool = True) -> None:
    """Write a list of JSON strings to an NDJSON file.

    Args:
        output_path: Path to the output NDJSON file.
        lines: List of JSON strings to write.
        overwrite: Whether to overwrite the output file if it exists.

    """
    if overwrite is True and output_path.exists():
        output_path.unlink()

    with output_path.open('w') as f:
        for line in lines:
            _ = f.write(line + '\n')


def compile_yaml_to_json(yaml_path: Path) -> tuple[list[str], str | None]:
    """Compile dashboard YAML to JSON strings for NDJSON.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        Tuple of (list of JSON strings for NDJSON lines, error message or None).

    """
    try:
        dashboards = load(str(yaml_path))
        json_lines: list[str] = []
        for dashboard in dashboards:
            dashboard_kbn_model = render(dashboard)
            json_lines.append(dashboard_kbn_model.model_dump_json(by_alias=True))
    except FileNotFoundError:
        return [], f'YAML file not found: {yaml_path}'
    except (ValueError, TypeError, KeyError) as e:
        return [], f'Error compiling {yaml_path}: {e}'
    else:
        return json_lines, None


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
        console.print(f'[yellow]{ICON_WARNING}[/yellow] Warning: No YAML files found in {directory}', style='yellow')

    return yaml_files


@click.group()
@click.version_option(version='0.1.0')
def cli() -> None:
    r"""Kibana Dashboard Compiler - Compile YAML dashboards to Kibana format.

    This tool helps you manage Kibana dashboards as code by compiling YAML
    configurations into Kibana's NDJSON format and optionally uploading them
    to your Kibana instance.

    \b
    Common workflows:
        1. Compile dashboards:     kb-dashboard compile
        2. Compile and upload:     kb-dashboard compile --upload
        3. Take a screenshot:      kb-dashboard screenshot --dashboard-id ID --output file.png
        4. Disassemble dashboard:  kb-dashboard disassemble dashboard.ndjson -o output_dir

    \b
    Authentication:
        Use either username/password OR API key (not both):
        - Basic auth: --kibana-username USER --kibana-password PASS
        - API key:    --kibana-api-key KEY (recommended for production)

    Use environment variables (KIBANA_URL, KIBANA_USERNAME, KIBANA_PASSWORD,
    KIBANA_API_KEY) to avoid passing credentials on the command line.
    """


@cli.command('compile')
@click.option(
    '--input-dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=DEFAULT_INPUT_DIR,
    help='Directory containing YAML dashboard files to compile.',
)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help='Directory where compiled NDJSON files will be written.',
)
@click.option(
    '--output-file',
    type=str,
    default='compiled_dashboards.ndjson',
    help='Filename for the combined output NDJSON file containing all dashboards.',
)
@click.option(
    '--upload',
    is_flag=True,
    help='Upload compiled dashboards to Kibana immediately after compilation.',
)
@click.option(
    '--kibana-url',
    type=str,
    envvar='KIBANA_URL',
    default='http://localhost:5601',
    help='Kibana base URL. Example: https://kibana.example.com (env: KIBANA_URL)',
)
@click.option(
    '--kibana-username',
    type=str,
    envvar='KIBANA_USERNAME',
    help=(
        'Kibana username for basic authentication. Must be used with --kibana-password. '
        'Mutually exclusive with --kibana-api-key. (env: KIBANA_USERNAME)'
    ),
)
@click.option(
    '--kibana-password',
    type=str,
    envvar='KIBANA_PASSWORD',
    help=(
        'Kibana password for basic authentication. Must be used with --kibana-username. '
        'Mutually exclusive with --kibana-api-key. (env: KIBANA_PASSWORD)'
    ),
)
@click.option(
    '--kibana-api-key',
    type=str,
    envvar='KIBANA_API_KEY',
    help=(
        'Kibana API key for authentication (recommended for production). '
        'Mutually exclusive with --kibana-username/--kibana-password. (env: KIBANA_API_KEY)'
    ),
)
@click.option(
    '--no-browser',
    is_flag=True,
    help='Prevent browser from opening automatically after successful upload.',
)
@click.option(
    '--overwrite/--no-overwrite',
    default=True,
    help='Whether to overwrite existing dashboards in Kibana (default: overwrite).',
)
@click.option(
    '--kibana-no-ssl-verify',
    is_flag=True,
    help='Disable SSL certificate verification (useful for self-signed certificates in local development).',
)
def compile_dashboards(  # noqa: PLR0913, PLR0912
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
    kibana_no_ssl_verify: bool,
) -> None:
    r"""Compile YAML dashboard configurations to NDJSON format.

    This command finds all YAML files in the input directory, compiles them
    to Kibana's JSON format, and outputs them as NDJSON files.

    Optionally, you can upload the compiled dashboards directly to Kibana
    using the --upload flag.

    \b
    Examples:
        # Compile dashboards from default directory
        kb-dashboard compile

        # Compile with custom input and output directories
        kb-dashboard compile --input-dir ./dashboards --output-dir ./output

        # Compile and upload to Kibana using basic auth
        kb-dashboard compile --upload --kibana-url https://kibana.example.com \
            --kibana-username admin --kibana-password secret

        # Compile and upload using API key (recommended)
        kb-dashboard compile --upload --kibana-url https://kibana.example.com \
            --kibana-api-key "your-api-key-here"

        # Use environment variables for credentials
        export KIBANA_URL=https://kibana.example.com
        export KIBANA_API_KEY=your-api-key
        kb-dashboard compile --upload
    """
    if kibana_api_key is not None and (kibana_username is not None or kibana_password is not None):
        msg = 'Cannot use --kibana-api-key together with --kibana-username or --kibana-password. Choose one authentication method.'
        raise click.UsageError(msg)

    if (kibana_username is not None and kibana_password is None) or (kibana_password is not None and kibana_username is None):
        msg = '--kibana-username and --kibana-password must be used together for basic authentication.'
        raise click.UsageError(msg)

    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = get_yaml_files(input_dir)
    if len(yaml_files) == 0:
        console.print('[yellow]No YAML files to compile.[/yellow]')
        return

    ndjson_lines: list[str] = []
    errors: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task('Compiling dashboards...', total=len(yaml_files))

        for yaml_file in yaml_files:
            try:
                display_path = yaml_file.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = yaml_file
            progress.update(task, description=f'Compiling: {display_path}')
            compiled_jsons, error = compile_yaml_to_json(yaml_file)

            if len(compiled_jsons) > 0:
                filename = yaml_file.parent.stem
                individual_file = output_dir / f'{filename}.ndjson'
                write_ndjson(individual_file, compiled_jsons, overwrite=True)
                ndjson_lines.extend(compiled_jsons)
            elif error is not None:
                errors.append(error)

            progress.advance(task)

    if len(ndjson_lines) > 0:
        console.print(f'[green]{ICON_SUCCESS}[/green] Successfully compiled {len(ndjson_lines)} dashboard(s)')

    if len(errors) > 0:
        console.print(f'\n[yellow]{ICON_WARNING}[/yellow] Encountered {len(errors)} error(s):', style='yellow')
        for error in errors:
            console.print(f'  [red]•[/red] {error}', style='red')

    if len(ndjson_lines) == 0:
        console.print(f'[red]{ICON_ERROR}[/red] No valid YAML configurations found or compiled.', style='red')
        return

    combined_file = output_dir / output_file
    write_ndjson(combined_file, ndjson_lines, overwrite=True)
    try:
        display_path = combined_file.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = combined_file
    console.print(f'[green]{ICON_SUCCESS}[/green] Wrote combined file: {display_path}')

    if upload is True:
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
                ssl_verify=not kibana_no_ssl_verify,
            )
        )


async def upload_to_kibana(  # noqa: PLR0913
    ndjson_file: Path,
    kibana_url: str,
    username: str | None,
    password: str | None,
    api_key: str | None,
    overwrite: bool,
    open_browser: bool,
    ssl_verify: bool = True,
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
        ssl_verify: Whether to verify SSL certificates (default: True)

    Raises:
        click.ClickException: If upload fails.

    """
    client = KibanaClient(
        url=kibana_url,
        username=username,
        password=password,
        api_key=api_key,
        ssl_verify=ssl_verify,
    )

    try:
        result = await client.upload_ndjson(ndjson_file, overwrite=overwrite)

        if result.success is True:
            console.print(f'[green]{ICON_SUCCESS}[/green] Successfully uploaded {result.success_count} object(s) to Kibana')

            dashboard_ids = [obj.destination_id or obj.id for obj in result.success_results if obj.type == 'dashboard']

            if len(dashboard_ids) > 0 and open_browser is True:
                dashboard_url = client.get_dashboard_url(dashboard_ids[0])
                console.print(f'[blue]{ICON_BROWSER}[/blue] Opening dashboard: {dashboard_url}')
                _ = webbrowser.open_new_tab(dashboard_url)

            if len(result.errors) > 0:
                console.print(f'\n[yellow]{ICON_WARNING}[/yellow] Encountered {len(result.errors)} error(s):')
                console.print(create_error_table(result.errors))
        else:
            console.print(f'[red]{ICON_ERROR}[/red] Upload failed', style='red')
            if len(result.errors) > 0:
                console.print(create_error_table(result.errors))
            msg = 'Upload to Kibana failed'
            raise click.ClickException(msg)

    except (OSError, ValueError) as e:
        msg = f'Error uploading to Kibana: {e}'
        raise click.ClickException(msg) from e


@cli.command('screenshot')
@click.option(
    '--dashboard-id',
    required=True,
    help='Kibana dashboard ID to capture. Find this in the dashboard URL.',
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    required=True,
    help='Path where the PNG screenshot will be saved. Example: ./dashboard.png',
)
@click.option(
    '--time-from',
    type=str,
    help=(
        'Start time for dashboard data range. Accepts ISO 8601 format ("2024-01-01T00:00:00Z") '
        'or relative time ("now-7d", "now-24h", "now-1M"). If omitted, uses dashboard default.'
    ),
)
@click.option(
    '--time-to',
    type=str,
    help=(
        'End time for dashboard data range. Accepts ISO 8601 format ("2024-12-31T23:59:59Z") '
        'or relative time ("now", "now-1h"). If omitted, uses dashboard default.'
    ),
)
@click.option(
    '--width',
    type=click.IntRange(min=1),
    default=1920,
    help='Screenshot width in pixels. Standard resolutions: 1920 (Full HD), 3840 (4K). Default: 1920',
)
@click.option(
    '--height',
    type=click.IntRange(min=1),
    default=1080,
    help='Screenshot height in pixels. Standard resolutions: 1080 (Full HD), 2160 (4K). Default: 1080',
)
@click.option(
    '--browser-timezone',
    type=str,
    default='UTC',
    help='Browser timezone for rendering time-based data. Examples: "UTC", "America/New_York", "Europe/London". Default: UTC',
)
@click.option(
    '--timeout',
    type=click.IntRange(min=1),
    default=300,
    help='Maximum time in seconds to wait for screenshot generation. Increase for complex dashboards. Default: 300',
)
@click.option(
    '--kibana-url',
    type=str,
    envvar='KIBANA_URL',
    default='http://localhost:5601',
    help='Kibana base URL. Example: https://kibana.example.com (env: KIBANA_URL)',
)
@click.option(
    '--kibana-username',
    type=str,
    envvar='KIBANA_USERNAME',
    help=(
        'Kibana username for basic authentication. Must be used with --kibana-password. '
        'Mutually exclusive with --kibana-api-key. (env: KIBANA_USERNAME)'
    ),
)
@click.option(
    '--kibana-password',
    type=str,
    envvar='KIBANA_PASSWORD',
    help=(
        'Kibana password for basic authentication. Must be used with --kibana-username. '
        'Mutually exclusive with --kibana-api-key. (env: KIBANA_PASSWORD)'
    ),
)
@click.option(
    '--kibana-api-key',
    type=str,
    envvar='KIBANA_API_KEY',
    help=(
        'Kibana API key for authentication (recommended for production). '
        'Mutually exclusive with --kibana-username/--kibana-password. (env: KIBANA_API_KEY)'
    ),
)
@click.option(
    '--kibana-no-ssl-verify',
    is_flag=True,
    help='Disable SSL certificate verification (useful for self-signed certificates in local development).',
)
def screenshot_dashboard(  # noqa: PLR0913
    dashboard_id: str,
    output: Path,
    time_from: str | None,
    time_to: str | None,
    width: int,
    height: int,
    browser_timezone: str,
    timeout: int,
    kibana_url: str,
    kibana_username: str | None,
    kibana_password: str | None,
    kibana_api_key: str | None,
    kibana_no_ssl_verify: bool,
) -> None:
    r"""Generate a PNG screenshot of a Kibana dashboard.

    This command uses Kibana's Reporting API to generate a screenshot of
    the specified dashboard. You can optionally specify a time range for
    the dashboard data.

    Examples:
        # Screenshot with default settings
        kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png

        # Screenshot with custom time range
        kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
            --time-from "2024-01-01T00:00:00Z" --time-to "2024-12-31T23:59:59Z"

        # Screenshot with relative time range
        kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
            --time-from "now-7d" --time-to "now"

        # Screenshot with custom dimensions
        kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
            --width 3840 --height 2160
    """
    if kibana_api_key is not None and (kibana_username is not None or kibana_password is not None):
        msg = 'Cannot use --kibana-api-key together with --kibana-username or --kibana-password. Choose one authentication method.'
        raise click.UsageError(msg)

    if (kibana_username is not None and kibana_password is None) or (kibana_password is not None and kibana_username is None):
        msg = '--kibana-username and --kibana-password must be used together for basic authentication.'
        raise click.UsageError(msg)

    asyncio.run(
        generate_screenshot(
            dashboard_id=dashboard_id,
            output_path=output,
            time_from=time_from,
            time_to=time_to,
            width=width,
            height=height,
            browser_timezone=browser_timezone,
            timeout_seconds=timeout,
            kibana_url=kibana_url,
            kibana_username=kibana_username,
            kibana_password=kibana_password,
            kibana_api_key=kibana_api_key,
            ssl_verify=not kibana_no_ssl_verify,
        )
    )


async def generate_screenshot(  # noqa: PLR0913
    dashboard_id: str,
    output_path: Path,
    time_from: str | None,
    time_to: str | None,
    width: int,
    height: int,
    browser_timezone: str,
    timeout_seconds: int,
    kibana_url: str,
    kibana_username: str | None,
    kibana_password: str | None,
    kibana_api_key: str | None,
    ssl_verify: bool = True,
) -> None:
    """Generate a screenshot of a Kibana dashboard.

    Args:
        dashboard_id: The dashboard ID to screenshot
        output_path: Path to save the PNG file
        time_from: Start time for dashboard time range
        time_to: End time for dashboard time range
        width: Screenshot width in pixels
        height: Screenshot height in pixels
        browser_timezone: Timezone for the screenshot
        timeout_seconds: Maximum seconds to wait for screenshot generation
        kibana_url: Kibana base URL
        kibana_username: Basic auth username
        kibana_password: Basic auth password
        kibana_api_key: API key for authentication
        ssl_verify: Whether to verify SSL certificates (default: True)

    Raises:
        click.ClickException: If screenshot generation fails.

    """
    client = KibanaClient(
        url=kibana_url,
        username=kibana_username,
        password=kibana_password,
        api_key=kibana_api_key,
        ssl_verify=ssl_verify,
    )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            console=console,
        ) as progress:
            task = progress.add_task(f'Generating screenshot for dashboard: {dashboard_id}...', total=None)

            await client.download_screenshot(
                dashboard_id=dashboard_id,
                output_path=output_path,
                time_from=time_from,
                time_to=time_to,
                width=width,
                height=height,
                browser_timezone=browser_timezone,
                timeout_seconds=timeout_seconds,
            )

            progress.update(task, description='Screenshot generated successfully')

        try:
            display_path = output_path.relative_to(PROJECT_ROOT)
        except ValueError:
            display_path = output_path

        console.print(f'[green]{ICON_SUCCESS}[/green] Screenshot saved to: {display_path}')
        console.print(f'  Dashboard: {dashboard_id}')
        console.print(f'  Size: {width}x{height}')
        if time_from is not None or time_to is not None:
            console.print(f'  Time range: {time_from or "now-15m"} to {time_to or "now"}')

    except aiohttp.ClientError as e:
        msg = f'Error communicating with Kibana: {e}'
        raise click.ClickException(msg) from e
    except TimeoutError as e:
        msg = f'Screenshot generation timed out: {e}'
        raise click.ClickException(msg) from e
    except (OSError, ValueError) as e:
        msg = f'Error generating screenshot: {e}'
        raise click.ClickException(msg) from e


@cli.command('disassemble')
@click.argument('input_file', type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    '-o',
    '--output',
    type=click.Path(path_type=Path),
    required=True,
    help='Output directory for component files.',
)
def disassemble(input_file: Path | None, output: Path) -> None:
    r"""Disassemble a Kibana dashboard NDJSON file into components.

    This command breaks down a Kibana dashboard JSON file (in NDJSON format)
    into separate files for easier processing by LLMs. This enables incremental
    conversion of large dashboards to YAML format.

    The dashboard is split into:
    - metadata.json: Dashboard metadata
    - options.json: Dashboard display options
    - controls.json: Dashboard control group configuration
    - filters.json: Dashboard-level filters
    - references.json: Data view and index pattern references
    - panels/: Directory containing individual panel JSON files

    \b
    Examples:
        # Disassemble a dashboard NDJSON file
        kb-dashboard disassemble dashboard.ndjson -o output_dir

        # Read from stdin
        cat dashboard.ndjson | kb-dashboard disassemble -o output_dir

        # Download and disassemble directly
        curl -u user:pass http://localhost:5601/api/saved_objects/dashboard/my-id | \
            kb-dashboard disassemble -o output_dir
    """
    try:
        if input_file is None:
            import sys

            content = sys.stdin.read()
        else:
            content = input_file.read_text(encoding='utf-8')

        dashboard = parse_ndjson(content)
        components = disassemble_dashboard(dashboard, output)

        console.print(f'[green]{ICON_SUCCESS}[/green] Dashboard disassembled to: {output}')
        console.print('  [dim]•[/dim] metadata.json: Dashboard metadata')

        if components.get('options') is True:
            console.print('  [dim]•[/dim] options.json: Dashboard options')

        if components.get('controls') is True:
            console.print('  [dim]•[/dim] controls.json: Control group configuration')

        if components.get('filters') is True:
            console.print('  [dim]•[/dim] filters.json: Dashboard-level filters')

        if components.get('references') is True:
            console.print('  [dim]•[/dim] references.json: Data view references')

        panel_count = components.get('panels')
        if panel_count is not None and isinstance(panel_count, int):
            console.print(f'  [dim]•[/dim] panels/: {panel_count} panel files')

    except (ValueError, OSError) as e:
        msg = f'Error disassembling dashboard: {e}'
        raise click.ClickException(msg) from e


if __name__ == '__main__':
    cli()
