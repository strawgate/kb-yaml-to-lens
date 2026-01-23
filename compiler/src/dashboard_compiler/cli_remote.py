"""CLI commands for remote Kibana and Elasticsearch operations."""

import asyncio
import json
import urllib.parse
import webbrowser
from pathlib import Path

import aiohttp
import rich_click as click
from elastic_transport import TransportError
from elasticsearch import AsyncElasticsearch

from dashboard_compiler.cli_context import CliContext

# Import helper from cli_local for shared functionality
from dashboard_compiler.cli_local import PROJECT_ROOT, get_yaml_files
from dashboard_compiler.cli_options import elasticsearch_options, kibana_options
from dashboard_compiler.cli_output import (
    create_progress,
    print_browser,
    print_bullet,
    print_detail,
    print_download,
    print_error,
    print_plain,
    print_success,
    print_warning,
)
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load
from dashboard_compiler.kibana_client import KibanaClient
from dashboard_compiler.sample_data.loader import load_sample_data
from dashboard_compiler.utils import extract_dashboard_id_from_url

# Constants
MAX_GITHUB_ISSUE_URL_LENGTH = 8000


@click.command('screenshot')
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
        _generate_screenshot(
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


async def _generate_screenshot(  # noqa: PLR0913
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
    async with client:
        try:
            with create_progress() as progress:
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

            print_success(f'Screenshot saved to: {display_path}')
            print_detail(f'Dashboard: {dashboard_id}')
            print_detail(f'Size: {width}x{height}')
            if time_from is not None or time_to is not None:
                print_detail(f'Time range: {time_from or "now-15m"} to {time_to or "now"}')

        except aiohttp.ClientError as e:
            msg = f'Error communicating with Kibana: {e}'
            raise click.ClickException(msg) from e
        except TimeoutError as e:
            msg = f'Screenshot generation timed out: {e}'
            raise click.ClickException(msg) from e
        except (OSError, ValueError) as e:
            msg = f'Error generating screenshot: {e}'
            raise click.ClickException(msg) from e


@click.command('fetch')
@click.argument('url_or_id', type=str, required=True)
@click.option(
    '-o',
    '--output',
    type=click.Path(path_type=Path),
    required=True,
    help='Output file path for the dashboard NDJSON.',
)
@kibana_options
def fetch(
    ctx: click.Context,
    url_or_id: str,
    output: Path,
) -> None:
    r"""Fetch a dashboard from Kibana and save it to a file.

    This command retrieves a dashboard's NDJSON from Kibana using a dashboard URL or ID.
    The dashboard and all its dependent objects (panels, data views) are exported and saved
    to the specified output file.

    URL_OR_ID can be:
    - A Kibana dashboard URL (e.g., https://kibana.example.com/app/dashboards#/view/my-id)
    - A plain dashboard ID (e.g., my-dashboard-id)

    \b
    Examples:
        # Fetch using dashboard URL
        kb-dashboard fetch "https://kibana.example.com/app/dashboards#/view/my-id" \
            --output dashboard.ndjson

        # Fetch using plain dashboard ID
        kb-dashboard fetch my-dashboard-id --output dashboard.ndjson

        # Fetch with API key authentication
        kb-dashboard fetch my-dashboard-id --output dashboard.ndjson \
            --kibana-api-key "your-api-key"

        # Fetch from specific space
        kb-dashboard fetch my-dashboard-id --output dashboard.ndjson \
            --kibana-space-id "my-space"
    """
    # Context is already populated by @kibana_options decorator
    if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
        msg = 'Context object must be CliContext'
        raise TypeError(msg)
    cli_context = ctx.obj

    if cli_context.kibana_client is None:
        msg = 'Kibana client not configured'
        raise click.ClickException(msg)

    asyncio.run(_fetch_dashboard(cli_context.kibana_client, url_or_id=url_or_id, output=output))


async def _fetch_dashboard(
    client: KibanaClient,
    url_or_id: str,
    output: Path,
) -> None:
    """Fetch dashboard from Kibana and save to file.

    This function attempts to resolve the dashboard in the following order:
    1. If input is a dashboard URL, extract ID from URL
    2. Otherwise, treat input as a plain dashboard ID

    Args:
        client: Pre-configured Kibana client
        url_or_id: Dashboard URL or ID to fetch
        output: Path to save the NDJSON file

    Raises:
        click.ClickException: If fetch fails

    """
    async with client:
        try:
            # Try to extract dashboard ID from URL
            # If extraction returns something different, it was a URL
            extracted_id = extract_dashboard_id_from_url(url_or_id)
            if extracted_id != url_or_id:
                dashboard_id = extracted_id
                lookup_method = 'URL'
            else:
                # Treat as a plain dashboard ID
                dashboard_id = url_or_id
                lookup_method = 'ID'

            with create_progress() as progress:
                task = progress.add_task(f'Fetching dashboard: {dashboard_id}...', total=None)

                ndjson_data = await client.export_dashboard(dashboard_id)

                progress.update(task, description='Dashboard fetched successfully')

            # Write NDJSON to output file atomically
            output.parent.mkdir(parents=True, exist_ok=True)
            tmp_output = output.with_suffix(output.suffix + '.tmp')
            _ = tmp_output.write_text(ndjson_data, encoding='utf-8')
            _ = tmp_output.replace(output)

            print_success('Dashboard fetched successfully')
            print_detail(f'Dashboard ID: {dashboard_id}')
            print_detail(f'Lookup method: {lookup_method}')
            print_detail(f'Exported objects: {len(ndjson_data.splitlines())} object(s)')
            print_detail(f'Saved to: {output}')

        except ValueError as e:
            msg = f'Invalid dashboard URL or ID: {e}'
            raise click.ClickException(msg) from e
        except aiohttp.ClientError as e:
            msg = f'Error communicating with Kibana: {e}'
            raise click.ClickException(msg) from e
        except OSError as e:
            msg = f'Error writing to file: {e}'
            raise click.ClickException(msg) from e


@click.command('export-for-issue')
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
    async with client:
        try:
            with create_progress() as progress:
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
                print_warning(
                    f'URL is very long ({len(issue_url)} chars). Some browsers may truncate it. Consider copying the NDJSON manually.'
                )

            print_success('Dashboard exported successfully')
            print_detail(f'Dashboard ID: {dashboard_id}')
            print_detail(f'Exported objects: {len(ndjson_data.splitlines())} object(s)')
            print_plain('')
            print_plain('[blue]GitHub Issue URL:[/blue]')
            print_detail(issue_url)

            if open_browser is True:
                print_browser('Opening pre-filled issue in browser...')
                _ = webbrowser.open_new_tab(issue_url)

        except aiohttp.ClientError as e:
            msg = f'Error communicating with Kibana: {e}'
            raise click.ClickException(msg) from e
        except (OSError, ValueError) as e:
            msg = f'Error exporting dashboard: {e}'
            raise click.ClickException(msg) from e


@click.command('load-sample-data')
@click.option(
    '--input-dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help='Directory containing YAML dashboard files with sample data.',
)
@elasticsearch_options
def load_sample_data_command(
    ctx: click.Context,
    input_dir: Path | None,
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
        kb-dashboard load-sample-data --es-url https://es.example.com \
            --es-username admin --es-password secret

        # Use API key (recommended)
        kb-dashboard load-sample-data --es-url https://es.example.com \
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

    # Use default input directory if not specified
    effective_input_dir = input_dir if input_dir is not None else PROJECT_ROOT / 'inputs'

    yaml_files = get_yaml_files(effective_input_dir)
    if len(yaml_files) == 0:
        print_plain('No YAML files found.', style='yellow')
        return

    dashboards_with_sample_data: list[tuple[Path, list[Dashboard]]] = []

    for yaml_file in yaml_files:
        dashboards = load(str(yaml_file))
        for dashboard in dashboards:
            if dashboard.sample_data is not None:
                dashboards_with_sample_data.append((yaml_file, dashboards))
                break

    if len(dashboards_with_sample_data) == 0:
        print_plain('No dashboards with sample data found.', style='yellow')
        return

    print_plain(f'Found {len(dashboards_with_sample_data)} dashboard(s) with sample data')
    print_download('Loading sample data to Elasticsearch...\n')

    asyncio.run(_load_all_sample_data(cli_context.es_client, dashboards_with_sample_data))


async def _load_all_sample_data(
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

                print_plain(f'Loading sample data for dashboard: {dashboard.name}')

                result = await load_sample_data(
                    es_client,
                    dashboard.sample_data,
                    base_path=yaml_file.parent,
                )

                if result.success is True:
                    print_success(f'Loaded {result.success_count} document(s) for {dashboard.name}')
                    total_loaded += result.success_count
                else:
                    print_error(f'Failed to load sample data for {dashboard.name}')
                    total_errors.extend(result.errors)

        if total_loaded > 0:
            print_success(f'Successfully loaded {total_loaded} total document(s)')

        if len(total_errors) > 0:
            print_warning(f'Encountered {len(total_errors)} error(s):')
            for error in total_errors:
                print_bullet(error)

    except (OSError, ValueError, TransportError) as e:
        msg = f'Error loading sample data: {e}'
        raise click.ClickException(msg) from e
    finally:
        await es_client.close()


@click.command('extract-sample-data')
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

    print_download('Extracting data from Elasticsearch...')
    print_plain(f'Index: {index}')
    print_plain(f'Query: {query}')
    print_plain(f'Max docs: {max_docs}')
    print_plain(f'Output: {output}\n')

    asyncio.run(_extract_data(cli_context.es_client, index, output, query, max_docs))


async def _extract_data(
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
            print_plain('No documents found matching the query.', style='yellow')
            return

        # Write to temp file first, then atomically replace
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp_output = output.with_suffix(output.suffix + '.tmp')
        with tmp_output.open('w', encoding='utf-8') as f:
            for hit in hits:  # pyright: ignore[reportAny]
                source = hit['_source']  # pyright: ignore[reportAny]
                _ = f.write(json.dumps(source))
                _ = f.write('\n')
        _ = tmp_output.replace(output)

        print_success(f'Successfully extracted {doc_count} document(s) to {output}')

    except (OSError, ValueError, TransportError) as e:
        msg = f'Error extracting data: {e}'
        raise click.ClickException(msg) from e
    finally:
        await es_client.close()
