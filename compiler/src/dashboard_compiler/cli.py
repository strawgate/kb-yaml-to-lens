"""Command-line interface for the dashboard compiler."""

import asyncio
import logging
import urllib.parse
import webbrowser
from pathlib import Path

import aiohttp
import rich_click as click
import yaml
from elastic_transport import TransportError
from elasticsearch import AsyncElasticsearch
from pydantic import ValidationError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from dashboard_compiler.cli_context import CliContext
from dashboard_compiler.cli_options import (
    elasticsearch_options,
    kibana_options,
)
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient, SavedObjectError
from dashboard_compiler.sample_data.loader import load_sample_data
from dashboard_compiler.shared.error_formatter import format_validation_error, format_yaml_error
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
ICON_DOWNLOAD = '📥'
ICON_BROWSER = '🌐'

MAX_GITHUB_ISSUE_URL_LENGTH = 8000


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
    except yaml.YAMLError as e:
        return [], format_yaml_error(e, yaml_path)
    except ValidationError as e:
        return [], format_validation_error(e, yaml_path)
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
@click.pass_context
def cli(ctx: click.Context) -> None:
    r"""Kibana Dashboard Compiler - Compile YAML dashboards to Kibana format.

    This tool helps you manage Kibana dashboards as code by compiling YAML
    configurations into Kibana's NDJSON format and optionally uploading them
    to your Kibana instance.

    \b
    Common workflows:
        1. Compile dashboards:     kb-dashboard compile
        2. Compile and upload:     kb-dashboard compile --upload
        3. Take a screenshot:      kb-dashboard screenshot --dashboard-id ID --output file.png
        4. Export for issue:       kb-dashboard export-for-issue --dashboard-id ID
        5. Disassemble dashboard:  kb-dashboard disassemble dashboard.ndjson -o output_dir

    \b
    Authentication:
        Use either username/password OR API key (not both):
        - Basic auth: --kibana-username USER --kibana-password PASS
        - API key:    --kibana-api-key KEY (recommended for production)

    Use environment variables (KIBANA_URL, KIBANA_USERNAME, KIBANA_PASSWORD,
    KIBANA_API_KEY) to avoid passing credentials on the command line.
    """
    _ = ctx.ensure_object(CliContext)


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
@kibana_options
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
def compile_dashboards(  # noqa: PLR0913, PLR0912
    ctx: click.Context,
    input_dir: Path,
    output_dir: Path,
    output_file: str,
    upload: bool,
    no_browser: bool,
    overwrite: bool,
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
    # Context is already populated by @kibana_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

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
        if cli_context.kibana_client is None:
            msg = 'Kibana client not configured'
            raise click.ClickException(msg)
        console.print(f'\n[blue]{ICON_UPLOAD}[/blue] Uploading to Kibana...')
        asyncio.run(upload_to_kibana(cli_context.kibana_client, combined_file, overwrite, not no_browser))


async def upload_to_kibana(
    client: KibanaClient,
    ndjson_file: Path,
    overwrite: bool,
    open_browser: bool,
) -> None:
    """Upload NDJSON file to Kibana.

    Args:
        client: Pre-configured Kibana client
        ndjson_file: Path to NDJSON file to upload
        overwrite: Whether to overwrite existing objects
        open_browser: Whether to open browser after successful upload

    Raises:
        click.ClickException: If upload fails.

    """
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


@cli.command('load-sample-data')
@click.option(
    '--input-dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=DEFAULT_INPUT_DIR,
    help='Directory containing YAML dashboard files with sample data.',
)
@elasticsearch_options
def load_sample_data_command(
    ctx: click.Context,
    input_dir: Path,
) -> None:
    r"""Load sample data bundled with dashboards into Elasticsearch.

    This command scans the input directory for YAML dashboard configurations
    that include sample data, and loads that data into Elasticsearch. The
    sample data will be automatically transformed so the maximum timestamp
    becomes "now", making the data appear as if it just happened.

    \b
    Examples:
        # Load sample data from default directory
        kb-dashboard load-sample-data

        # Load with custom input directory
        kb-dashboard load-sample-data --input-dir ./dashboards

        # Load with Elasticsearch authentication
        kb-dashboard load-sample-data --es-url https://es.example.com \\
            --es-username admin --es-password secret

        # Use API key (recommended)
        kb-dashboard load-sample-data --es-url https://es.example.com \\
            --es-api-key "your-api-key-here"
    """
    # Context is already populated by @elasticsearch_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

    if cli_context.es_client is None:
        msg = 'Elasticsearch client not configured'
        raise click.ClickException(msg)

    yaml_files = get_yaml_files(input_dir)
    if len(yaml_files) == 0:
        console.print('[yellow]No YAML files found.[/yellow]')
        return

    dashboards_with_sample_data: list[tuple[Path, list[Dashboard]]] = []

    for yaml_file in yaml_files:
        dashboards = load(str(yaml_file))
        for dashboard in dashboards:
            if dashboard.sample_data is not None:
                dashboards_with_sample_data.append((yaml_file, dashboards))
                break

    if len(dashboards_with_sample_data) == 0:
        console.print('[yellow]No dashboards with sample data found.[/yellow]')
        return

    console.print(f'Found {len(dashboards_with_sample_data)} dashboard(s) with sample data')
    console.print(f'[blue]{ICON_DOWNLOAD}[/blue] Loading sample data to Elasticsearch...\n')

    asyncio.run(load_all_sample_data(cli_context.es_client, dashboards_with_sample_data))


@cli.command('extract-sample-data')
@click.option(
    '--index',
    type=str,
    required=True,
    help='Elasticsearch index pattern to extract data from (e.g., logs-*, metrics-*).',
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    required=True,
    help='Path where the NDJSON file will be saved.',
)
@click.option(
    '--query',
    type=str,
    default='*',
    help='Elasticsearch query to filter documents (default: * for all documents).',
)
@click.option(
    '--max-docs',
    type=int,
    default=1000,
    help='Maximum number of documents to extract (default: 1000).',
)
@elasticsearch_options
def extract_sample_data_command(
    ctx: click.Context,
    index: str,
    output: Path,
    query: str,
    max_docs: int,
) -> None:
    r"""Extract data from Elasticsearch to NDJSON format.

    This command queries Elasticsearch and exports the results to an NDJSON file
    that can be used as sample data for dashboards. Each line in the output file
    is a separate JSON document.

    \b
    Examples:
        # Extract logs data
        kb-dashboard extract-sample-data --index logs-* --output sample-logs.ndjson

        # Extract with custom query
        kb-dashboard extract-sample-data --index metrics-* --output sample-metrics.ndjson \
            --query 'host.name:server01'

        # Extract limited number of documents
        kb-dashboard extract-sample-data --index logs-* --output sample.ndjson --max-docs 100

        # With authentication
        kb-dashboard extract-sample-data --index logs-* --output sample.ndjson \
            --es-url https://es.example.com --es-api-key "your-api-key"
    """
    # Context is already populated by @elasticsearch_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

    if cli_context.es_client is None:
        msg = 'Elasticsearch client not configured'
        raise click.ClickException(msg)

    console.print(f'[blue]{ICON_DOWNLOAD}[/blue] Extracting data from Elasticsearch...')
    console.print(f'Index: {index}')
    console.print(f'Query: {query}')
    console.print(f'Max docs: {max_docs}')
    console.print(f'Output: {output}\n')

    asyncio.run(extract_data(cli_context.es_client, index, output, query, max_docs))


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
@kibana_options
def screenshot_dashboard(  # noqa: PLR0913
    ctx: click.Context,
    dashboard_id: str,
    output: Path,
    time_from: str | None,
    time_to: str | None,
    width: int,
    height: int,
    browser_timezone: str,
    timeout: int,
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
    # Context is already populated by @kibana_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

    if cli_context.kibana_client is None:
        msg = 'Kibana client not configured'
        raise click.ClickException(msg)

    asyncio.run(
        generate_screenshot(
            cli_context.kibana_client,
            dashboard_id=dashboard_id,
            output_path=output,
            time_from=time_from,
            time_to=time_to,
            width=width,
            height=height,
            browser_timezone=browser_timezone,
            timeout_seconds=timeout,
        )
    )


async def generate_screenshot(  # noqa: PLR0913
    client: KibanaClient,
    dashboard_id: str,
    output_path: Path,
    time_from: str | None,
    time_to: str | None,
    width: int,
    height: int,
    browser_timezone: str,
    timeout_seconds: int,
) -> None:
    """Generate a screenshot of a Kibana dashboard.

    Args:
        client: Pre-configured Kibana client
        dashboard_id: The dashboard ID to screenshot
        output_path: Path to save the PNG file
        time_from: Start time for dashboard time range
        time_to: End time for dashboard time range
        width: Screenshot width in pixels
        height: Screenshot height in pixels
        browser_timezone: Timezone for the screenshot
        timeout_seconds: Maximum seconds to wait for screenshot generation

    Raises:
        click.ClickException: If screenshot generation fails.

    """
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


async def extract_data(
    es_client: AsyncElasticsearch,
    index: str,
    output: Path,
    query: str,
    max_docs: int,
) -> None:
    """Extract data from Elasticsearch to NDJSON file.

    Args:
        es_client: Pre-configured Elasticsearch client
        index: Elasticsearch index pattern to query
        output: Path where NDJSON file will be saved
        query: Elasticsearch query string
        max_docs: Maximum number of documents to extract

    Raises:
        click.ClickException: If extraction fails.

    """
    import json

    try:
        response = await es_client.search(
            index=index,
            query={'query_string': {'query': query}},
            size=max_docs,
            sort=['@timestamp:desc'],
        )

        hits = response['hits']['hits']  # pyright: ignore[reportAny]
        doc_count = len(hits)  # pyright: ignore[reportAny]

        if doc_count == 0:
            console.print('[yellow]No documents found matching the query.[/yellow]')
            return

        with output.open('w') as f:
            for hit in hits:  # pyright: ignore[reportAny]
                source = hit['_source']  # pyright: ignore[reportAny]
                _ = f.write(json.dumps(source))
                _ = f.write('\n')

        console.print(f'\n[green]{ICON_SUCCESS}[/green] Successfully extracted {doc_count} document(s) to {output}')

    except (OSError, ValueError, TransportError) as e:
        msg = f'Error extracting data: {e}'
        raise click.ClickException(msg) from e
    finally:
        await es_client.close()


async def load_all_sample_data(
    es_client: AsyncElasticsearch,
    dashboards_with_sample_data: list[tuple[Path, list[Dashboard]]],
) -> None:
    """Load sample data from all dashboards into Elasticsearch.

    Args:
        es_client: Pre-configured Elasticsearch client
        dashboards_with_sample_data: List of (yaml_file_path, dashboards) tuples

    Raises:
        click.ClickException: If sample data loading fails.

    """
    try:
        total_loaded = 0
        total_errors: list[str] = []

        for yaml_file, dashboards in dashboards_with_sample_data:
            for dashboard in dashboards:
                if dashboard.sample_data is None:
                    continue

                console.print(f'Loading sample data for dashboard: {dashboard.name}')

                result = await load_sample_data(
                    es_client,
                    dashboard.sample_data,
                    base_path=yaml_file.parent,
                )

                if result.success is True:
                    console.print(f'[green]{ICON_SUCCESS}[/green] Loaded {result.success_count} document(s) for {dashboard.name}')
                    total_loaded += result.success_count
                else:
                    console.print(f'[red]{ICON_ERROR}[/red] Failed to load sample data for {dashboard.name}')
                    total_errors.extend(result.errors)

        if total_loaded > 0:
            console.print(f'\n[green]{ICON_SUCCESS}[/green] Successfully loaded {total_loaded} total document(s)')

        if len(total_errors) > 0:
            console.print(f'\n[yellow]{ICON_WARNING}[/yellow] Encountered {len(total_errors)} error(s):')
            for error in total_errors:
                console.print(f'  [red]•[/red] {error}', style='red')

    except (OSError, ValueError, TransportError) as e:
        msg = f'Error loading sample data: {e}'
        raise click.ClickException(msg) from e
    finally:
        await es_client.close()


@cli.command('export-for-issue')
@click.option(
    '--dashboard-id',
    required=True,
    help='Kibana dashboard ID to export. Find this in the dashboard URL.',
)
@kibana_options
@click.option(
    '--no-browser',
    is_flag=True,
    help='Do not open browser automatically with pre-filled issue.',
)
def export_for_issue(
    ctx: click.Context,
    dashboard_id: str,
    no_browser: bool,
) -> None:
    r"""Export a dashboard from Kibana and create a pre-filled GitHub issue.

    This command downloads a dashboard's JSON from Kibana and generates a GitHub
    issue URL with the dashboard JSON pre-filled in the body. You can then submit
    the issue to request support for compiling the dashboard from YAML.

    \b
    Examples:
        # Export dashboard and open pre-filled issue in browser
        kb-dashboard export-for-issue --dashboard-id my-dashboard-id

        # Export with API key authentication
        kb-dashboard export-for-issue --dashboard-id my-dashboard-id \
            --kibana-api-key "your-api-key"

        # Export and print URL without opening browser
        kb-dashboard export-for-issue --dashboard-id my-dashboard-id --no-browser
    """
    # Context is already populated by @kibana_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

    if cli_context.kibana_client is None:
        msg = 'Kibana client not configured'
        raise click.ClickException(msg)

    asyncio.run(_export_dashboard_for_issue(cli_context.kibana_client, dashboard_id=dashboard_id, open_browser=not no_browser))


async def _export_dashboard_for_issue(
    client: KibanaClient,
    dashboard_id: str,
    open_browser: bool,
) -> None:
    """Export dashboard and generate GitHub issue URL.

    Args:
        client: Pre-configured Kibana client
        dashboard_id: The dashboard ID to export
        open_browser: Whether to open browser with pre-filled issue

    Raises:
        click.ClickException: If export fails

    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            console=console,
        ) as progress:
            task = progress.add_task(f'Exporting dashboard: {dashboard_id}...', total=None)

            ndjson_data = await client.export_dashboard(dashboard_id)

            progress.update(task, description='Dashboard exported successfully')

        repo_url = 'https://github.com/strawgate/kb-yaml-to-lens'
        issue_title = f'Dashboard support request: {dashboard_id}'
        issue_body = f"""## Dashboard Export Request

I'd like to compile this dashboard using kb-yaml-to-lens.

### Dashboard ID
`{dashboard_id}`

### Exported Dashboard JSON

```json
{ndjson_data}
```

### Additional Context

"""

        encoded_title = urllib.parse.quote(issue_title)
        encoded_body = urllib.parse.quote(issue_body)

        issue_url = f'{repo_url}/issues/new?title={encoded_title}&body={encoded_body}'

        if len(issue_url) > MAX_GITHUB_ISSUE_URL_LENGTH:
            msg = (
                f'[yellow]{ICON_WARNING}[/yellow] URL is very long ({len(issue_url)} chars). '
                'Some browsers may truncate it. Consider copying the NDJSON manually.'
            )
            console.print(msg)

        console.print(f'[green]{ICON_SUCCESS}[/green] Dashboard exported successfully')
        console.print(f'  Dashboard ID: {dashboard_id}')
        console.print(f'  Exported objects: {len(ndjson_data.splitlines())} object(s)')
        console.print()
        console.print('[blue]GitHub Issue URL:[/blue]')
        console.print(f'  {issue_url}')

        if open_browser is True:
            console.print(f'\n[blue]{ICON_BROWSER}[/blue] Opening pre-filled issue in browser...')
            _ = webbrowser.open_new_tab(issue_url)

    except aiohttp.ClientError as e:
        msg = f'Error communicating with Kibana: {e}'
        raise click.ClickException(msg) from e
    except (OSError, ValueError) as e:
        msg = f'Error exporting dashboard: {e}'
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
