"""Command-line interface for the dashboard compiler.

This module serves as the entry point and command registry for the CLI.
Commands are organized into separate modules:

- cli_local: Local file operations (compile, disassemble, lsp)
- cli_remote: Remote Kibana/Elasticsearch operations (fetch, screenshot, etc.)
- cli_output: Centralized output helpers for consistent messaging
- cli_options: Reusable option decorators for Kibana and Elasticsearch
- cli_context: Context object for sharing clients across commands
"""

import logging
import os
import sys
from importlib.metadata import PackageNotFoundError, version

import rich_click as click

from dashboard_compiler.cli_context import CliContext
from dashboard_compiler.cli_local import compile_dashboards, disassemble, lsp
from dashboard_compiler.cli_remote import (
    export_for_issue,
    extract_sample_data_command,
    fetch,
    load_sample_data_command,
    screenshot_dashboard,
)

# Disable rich_click colors when generating documentation or when NO_COLOR is set
# This prevents ANSI escape sequences from appearing in mkdocs-click generated docs
if 'NO_COLOR' in os.environ or not sys.stdout.isatty():
    click.rich_click.COLOR_SYSTEM = None
    click.rich_click.FORCE_TERMINAL = False

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

# Get package version dynamically from installed package metadata
try:
    __version__ = version('kb-dashboard-cli')
except PackageNotFoundError:
    # Fallback if package is not installed (e.g., during development)
    __version__ = '0.0.0-dev'


@click.group()
@click.version_option(version=__version__)
@click.option(
    '--loglevel',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default='WARNING',
    help='Set logging verbosity level for compilation output.',
)
@click.pass_context
def cli(ctx: click.Context, loglevel: str) -> None:
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
    # Configure logging based on CLI option
    log_level: int = getattr(logging, loglevel.upper())  # pyright: ignore[reportAny]
    logging.basicConfig(level=log_level, format='%(message)s')
    # Also set level for our specific logger
    logging.getLogger('dashboard_compiler').setLevel(log_level)

    _ = ctx.ensure_object(CliContext)


# Register local file operation commands
cli.add_command(compile_dashboards)
cli.add_command(disassemble)
cli.add_command(lsp)

# Register remote Kibana/Elasticsearch commands
cli.add_command(screenshot_dashboard, name='screenshot')
cli.add_command(fetch)
cli.add_command(export_for_issue, name='export-for-issue')
cli.add_command(load_sample_data_command, name='load-sample-data')
cli.add_command(extract_sample_data_command, name='extract-sample-data')


if __name__ == '__main__':
    cli()
