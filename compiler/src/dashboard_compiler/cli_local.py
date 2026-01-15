"""CLI commands for local file operations (compile, disassemble, lsp)."""

import asyncio
import io
import logging
import sys
import webbrowser
from pathlib import Path

# Import TYPE_CHECKING for forward reference
from typing import TYPE_CHECKING

import rich_click as click
import yaml
from pydantic import ValidationError

from dashboard_compiler.cli_context import CliContext
from dashboard_compiler.cli_options import kibana_options
from dashboard_compiler.cli_output import (
    console,
    create_error_table,
    create_progress,
    print_browser,
    print_bullet,
    print_dim_bullet,
    print_error,
    print_plain,
    print_success,
    print_upload,
    print_warning,
)
from dashboard_compiler.dashboard.view import KbnDashboard
from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.shared.error_formatter import format_validation_error, format_yaml_error
from dashboard_compiler.tools.disassemble import disassemble_dashboard, parse_ndjson

if TYPE_CHECKING:
    from dashboard_compiler.kibana_client import KibanaClient

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / 'inputs'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'output'
MAX_EXIT_CODE = 125


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """Convert a string to a filesystem-safe filename.

    Args:
        name: The name to sanitize.
        max_length: Maximum length for the filename (default: 200).

    Returns:
        A sanitized filename safe for all filesystems.

    """
    # Replace filesystem-unsafe characters with underscores
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    result = name
    for char in unsafe_chars:
        result = result.replace(char, '_')

    # Replace spaces with underscores and trim whitespace
    result = result.strip().replace(' ', '_')

    # Strip leading dots to avoid hidden files and reserved names
    result = result.lstrip('.')

    # Handle empty or reserved results
    if len(result) == 0 or result in ('.', '..'):
        result = 'untitled'

    # Truncate to max length
    if len(result) > max_length:
        result = result[:max_length]

    return result


def file_content_changed(file_path: Path, new_content: str) -> bool:
    """Check if writing new content would change the filesystem.

    Args:
        file_path: Path to the existing file.
        new_content: New content to compare against.

    Returns:
        True if the file doesn't exist or has different content, False otherwise.

    """
    if not file_path.exists():
        return True

    existing_content = file_path.read_text(encoding='utf-8')
    return existing_content != new_content


def write_ndjson(output_path: Path, lines: list[str], overwrite: bool = True) -> None:
    """Write a list of JSON strings to an NDJSON file.

    Args:
        output_path: Path to the output NDJSON file.
        lines: List of JSON strings to write.
        overwrite: Whether to overwrite the output file if it exists.

    """
    if overwrite is False and output_path.exists():
        return

    with output_path.open('w', encoding='utf-8') as f:
        for line in lines:
            _ = f.write(line + '\n')


def compile_yaml_to_json(yaml_path: Path) -> tuple[list[str], list[KbnDashboard], str | None]:
    """Compile dashboard YAML to JSON strings for NDJSON.

    Args:
        yaml_path: Path to the dashboard YAML configuration file.

    Returns:
        Tuple of (list of JSON strings for NDJSON lines, list of dashboard models, error message or None).

    """
    try:
        dashboards = load(str(yaml_path))
        json_lines: list[str] = []
        kbn_dashboards: list[KbnDashboard] = []
        for dashboard in dashboards:
            dashboard_kbn_model = render(dashboard)
            json_lines.append(dashboard_kbn_model.model_dump_json(by_alias=True))
            kbn_dashboards.append(dashboard_kbn_model)
    except FileNotFoundError:
        return [], [], f'YAML file not found: {yaml_path}'
    except yaml.YAMLError as e:
        return [], [], format_yaml_error(e, yaml_path)
    except ValidationError as e:
        return [], [], format_validation_error(e, yaml_path)
    except (ValueError, TypeError, KeyError) as e:
        return [], [], f'Error compiling {yaml_path}: {e}'
    else:
        return json_lines, kbn_dashboards, None


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


async def _upload_to_kibana(
    client: 'KibanaClient',
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
    import aiohttp

    async with client:
        try:
            result = await client.upload_ndjson(ndjson_file, overwrite=overwrite)

            if result.success is True:
                print_success(f'Successfully uploaded {result.success_count} object(s) to Kibana')

                dashboard_ids = [obj.destination_id or obj.id for obj in result.success_results if obj.type == 'dashboard']

                if len(dashboard_ids) > 0 and open_browser is True:
                    dashboard_url = client.get_dashboard_url(dashboard_ids[0])
                    print_browser(f'Opening dashboard: {dashboard_url}')
                    _ = webbrowser.open_new_tab(dashboard_url)

                if len(result.errors) > 0:
                    print_warning(f'Encountered {len(result.errors)} error(s):')
                    console.print(create_error_table(result.errors))
            else:
                print_error('Upload failed')
                if len(result.errors) > 0:
                    console.print(create_error_table(result.errors))
                msg = 'Upload to Kibana failed'
                raise click.ClickException(msg)

        except aiohttp.ClientError as e:
            msg = f'Error communicating with Kibana: {e}'
            raise click.ClickException(msg) from e
        except (OSError, ValueError) as e:
            msg = f'Error uploading to Kibana: {e}'
            raise click.ClickException(msg) from e


@click.command('compile')
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
    '--format',
    'output_format',
    type=click.Choice(['ndjson', 'json'], case_sensitive=False),
    default='ndjson',
    help='Output format: "ndjson" for combined files (default), "json" for individual pretty-printed files per dashboard.',
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
def compile_dashboards(  # noqa: PLR0913, PLR0912, PLR0915
    ctx: click.Context,
    input_dir: Path,
    output_dir: Path,
    output_file: str,
    output_format: str,
    upload: bool,
    no_browser: bool,
    overwrite: bool,
) -> None:
    r"""Compile YAML dashboard configurations to NDJSON format.

    This command finds all YAML files in the input directory, compiles them
    to Kibana's JSON format, and outputs them as NDJSON files.

    Optionally, you can upload the compiled dashboards directly to Kibana
    using the --upload flag.

    The --format option controls output format:
    - ndjson (default): Groups dashboards by directory into NDJSON files
    - json: Creates individual pretty-printed JSON files per dashboard

    The exit code indicates the number of files that changed (capped at 125),
    which is useful for CI workflows to detect when YAML and JSON are out of sync.

    \b
    Examples:
        # Compile dashboards from default directory
        kb-dashboard compile

        # Compile with custom input and output directories
        kb-dashboard compile --input-dir ./dashboards --output-dir ./output

        # Compile to individual JSON files per dashboard
        kb-dashboard compile --format json --output-dir ./output

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

    # Normalize output format once for consistent comparisons
    output_format_lower = output_format.lower()

    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = get_yaml_files(input_dir)
    if len(yaml_files) == 0:
        print_plain('No YAML files to compile.', style='yellow')
        return

    ndjson_lines: list[str] = []
    errors: list[str] = []
    files_to_write: dict[Path, list[str]] = {}
    json_files_to_write: list[tuple[Path, str]] = []
    changed_files_count = 0

    with create_progress() as progress:
        task = progress.add_task('Compiling dashboards...', total=len(yaml_files))

        for yaml_file in yaml_files:
            try:
                display_path = yaml_file.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = yaml_file
            progress.update(task, description=f'Compiling: {display_path}')
            compiled_jsons, kbn_dashboards, error = compile_yaml_to_json(yaml_file)

            if len(compiled_jsons) > 0:
                if output_format_lower == 'json':
                    for kbn_dashboard in kbn_dashboards:
                        dashboard_name = kbn_dashboard.attributes.title
                        safe_name = sanitize_filename(dashboard_name)
                        json_file = output_dir / f'{safe_name}.json'
                        pretty_json = kbn_dashboard.model_dump_json(by_alias=True, indent=2)
                        json_files_to_write.append((json_file, pretty_json))
                else:
                    filename = yaml_file.parent.stem
                    individual_file = output_dir / f'{filename}.ndjson'
                    if individual_file not in files_to_write:
                        files_to_write[individual_file] = []
                    files_to_write[individual_file].extend(compiled_jsons)
                ndjson_lines.extend(compiled_jsons)
            elif error is not None:
                errors.append(error)

            progress.advance(task)

    if output_format_lower == 'json':
        for json_file, json_content in json_files_to_write:
            if file_content_changed(json_file, json_content):
                changed_files_count += 1
            with json_file.open('w', encoding='utf-8') as f:
                _ = f.write(json_content)
    else:
        for individual_file, jsons in files_to_write.items():
            content = '\n'.join(jsons) + '\n'
            if file_content_changed(individual_file, content):
                changed_files_count += 1
            write_ndjson(individual_file, jsons, overwrite=True)

    if len(ndjson_lines) > 0:
        print_success(f'Successfully compiled {len(ndjson_lines)} dashboard(s)')

    if len(errors) > 0:
        print_warning(f'Encountered {len(errors)} error(s):')
        for error in errors:
            print_bullet(error)

    if len(ndjson_lines) == 0:
        print_error('No valid YAML configurations found or compiled.')
        return

    if output_format_lower == 'json':
        print_success(f'Wrote {len(json_files_to_write)} individual JSON file(s)')
    else:
        combined_file = output_dir / output_file
        combined_content = '\n'.join(ndjson_lines) + '\n'
        if file_content_changed(combined_file, combined_content):
            changed_files_count += 1
        write_ndjson(combined_file, ndjson_lines, overwrite=True)
        try:
            display_path = combined_file.relative_to(PROJECT_ROOT)
        except ValueError:
            display_path = combined_file
        print_success(f'Wrote combined file: {display_path}')

    if changed_files_count > 0:
        print_warning(f'{changed_files_count} file(s) changed')
    else:
        print_success('No files changed')

    if upload is True:
        if output_format_lower == 'json':
            print_warning('Upload is not supported with --format json')
        else:
            if cli_context.kibana_client is None:
                msg = 'Kibana client not configured'
                raise click.ClickException(msg)
            print_upload('Uploading to Kibana...')
            combined_file = output_dir / output_file
            asyncio.run(_upload_to_kibana(cli_context.kibana_client, combined_file, overwrite, not no_browser))

    exit_code = min(changed_files_count, MAX_EXIT_CODE)
    ctx.exit(exit_code)


@click.command('disassemble')
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
            # Use TextIOWrapper to ensure UTF-8 encoding when reading from stdin
            # This avoids issues on Windows where the default encoding might not be UTF-8
            content = (
                io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read()
                if hasattr(sys.stdin, 'buffer')
                else sys.stdin.read()  # Fallback for environments where stdin.buffer is not available
            )
        else:
            content = input_file.read_text(encoding='utf-8')

        dashboard = parse_ndjson(content)
        components = disassemble_dashboard(dashboard, output)

        print_success(f'Dashboard disassembled to: {output}')
        print_dim_bullet('metadata.json: Dashboard metadata')

        if components.get('options') is True:
            print_dim_bullet('options.json: Dashboard options')

        if components.get('controls') is True:
            print_dim_bullet('controls.json: Control group configuration')

        if components.get('filters') is True:
            print_dim_bullet('filters.json: Dashboard-level filters')

        if components.get('references') is True:
            print_dim_bullet('references.json: Data view references')

        panel_count = components.get('panels')
        if panel_count is not None and isinstance(panel_count, int):
            print_dim_bullet(f'panels/: {panel_count} panel files')

    except (ValueError, OSError) as e:
        msg = f'Error disassembling dashboard: {e}'
        raise click.ClickException(msg) from e


@click.command()
def lsp() -> None:
    """Start the Language Server Protocol (LSP) server for IDE integration.

    The LSP server provides real-time compilation, validation, and code
    completion for YAML dashboard files in supported IDEs like VS Code.

    This server communicates via stdin/stdout using the Language Server
    Protocol specification.
    """
    from dashboard_compiler.lsp.server import start_server as start_lsp_server

    # Force logging to stderr to prevent stdout contamination of JSON-RPC protocol
    logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr, force=True)
    start_lsp_server()
