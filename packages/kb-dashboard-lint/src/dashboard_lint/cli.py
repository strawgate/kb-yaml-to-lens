"""Command-line interface for dashboard linting."""

import json
import os
import sys
from collections import defaultdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import rich_click as click
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from dashboard_lint.config import load_config
from dashboard_lint.runner import LintRunner
from dashboard_lint.types import SEVERITY_ORDER, Severity, Violation

# Disable rich_click colors when generating documentation or when NO_COLOR is set
if 'NO_COLOR' in os.environ or not sys.stdout.isatty():
    click.rich_click.COLOR_SYSTEM = None
    click.rich_click.FORCE_TERMINAL = False

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

console = Console()

# Get package version
try:
    __version__ = version('kb-dashboard-lint')
except PackageNotFoundError:
    __version__ = '0.0.0-dev'


def _format_violations_text(violations: list[Violation]) -> None:
    """Format and print violations as text output."""
    # Group by dashboard
    by_dashboard: defaultdict[str, list[Violation]] = defaultdict(list)
    for v in violations:
        by_dashboard[v.dashboard_name].append(v)

    for dashboard_name, dashboard_violations in by_dashboard.items():
        console.print(f'\n[bold]Dashboard: {dashboard_name}[/bold]')
        console.print('─' * 60)

        for v in dashboard_violations:
            # Severity-based styling
            if v.severity == Severity.ERROR:
                icon = '[red]✗[/red]'
                severity_style = 'red'
            elif v.severity == Severity.WARNING:
                icon = '[yellow]⚠[/yellow]'
                severity_style = 'yellow'
            else:
                icon = '[blue]i[/blue]'
                severity_style = 'blue'

            # Panel info
            panel_info = f' → {v.panel_title}' if v.panel_title is not None else ''

            console.print(f'{icon} [{severity_style}]{v.severity.value:7}[/{severity_style}] {v.rule_id:30} {panel_info}')
            console.print(f'          {v.message}')


def _format_violations_json(violations: list[Violation]) -> str:
    """Format violations as JSON."""
    data: list[dict[str, object]] = []
    for v in violations:
        violation_data: dict[str, object] = {
            'rule_id': v.rule_id,
            'message': v.message,
            'severity': v.severity.value,
            'dashboard_name': v.dashboard_name,
            'panel_title': v.panel_title,
            'location': v.location,
        }
        # Include source range if available (LSP-compatible format)
        if v.source_range is not None:
            violation_data['range'] = v.source_range.to_lsp_range()
            if v.source_range.file_path is not None:
                violation_data['file'] = v.source_range.file_path
        data.append(violation_data)
    return json.dumps(data, indent=2)


def _print_summary(violations: list[Violation]) -> None:
    """Print a summary of violations by severity."""
    errors = sum(1 for v in violations if v.severity == Severity.ERROR)
    warnings = sum(1 for v in violations if v.severity == Severity.WARNING)
    infos = sum(1 for v in violations if v.severity == Severity.INFO)

    console.print('\n' + '─' * 60)
    parts: list[str] = []
    if errors > 0:
        parts.append(f'[red]{errors} error{"s" if errors != 1 else ""}[/red]')
    if warnings > 0:
        parts.append(f'[yellow]{warnings} warning{"s" if warnings != 1 else ""}[/yellow]')
    if infos > 0:
        parts.append(f'[blue]{infos} info[/blue]')

    if len(parts) > 0:
        console.print('Summary: ' + ', '.join(parts))
    else:
        console.print('[green]No issues found![/green]')


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Dashboard Linter - Check YAML dashboards for best practices.

    This tool analyzes dashboard configurations and flags potentially
    problematic patterns based on configurable rules.
    """


@cli.command()
@click.option(
    '--input-dir',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help='Directory containing YAML dashboard files.',
)
@click.option(
    '--input-file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help='Single YAML file to check.',
)
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help='Path to lint configuration file.',
)
@click.option(
    '--severity-threshold',
    type=click.Choice(['error', 'warning', 'info'], case_sensitive=False),
    default='warning',
    help='Exit non-zero if violations at this severity or higher are found.',
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='Output format.',
)
def check(
    input_dir: Path | None,
    input_file: Path | None,
    config: Path | None,
    severity_threshold: str,
    output_format: str,
) -> None:
    """Check dashboard YAML files for issues.

    Examples:
        kb-dashboard-lint check --input-dir ./inputs

        kb-dashboard-lint check --input-file dashboard.yaml

        kb-dashboard-lint check --config .dashboard-lint.yaml
    """
    # Import rules to register them
    import dashboard_lint.rules  # pyright: ignore[reportUnusedImport]
    from dashboard_compiler import load

    # Validate input options
    if input_dir is None and input_file is None:
        # Default to current directory
        input_dir = Path('inputs')
        if not input_dir.exists():
            input_dir = Path()

    # Load configuration
    lint_config = load_config(config)

    # Load dashboards
    try:
        if input_file is not None:
            dashboards = load(str(input_file))
        elif input_dir is not None:
            dashboards = load(str(input_dir))
        else:
            console.print('[red]Error: No input specified[/red]')
            sys.exit(1)
    except (FileNotFoundError, PermissionError, OSError, yaml.YAMLError, ValidationError) as e:
        console.print(f'[red]Error loading dashboards: {e}[/red]')
        sys.exit(1)

    if len(dashboards) == 0:
        console.print('[yellow]No dashboards found to check[/yellow]')
        sys.exit(0)

    # Run linting
    runner = LintRunner(config=lint_config)
    violations = runner.run(dashboards)

    # Output results
    if output_format == 'json':
        print(_format_violations_json(violations))
    elif len(violations) > 0:
        _format_violations_text(violations)
        _print_summary(violations)
    else:
        console.print('[green]✓ No issues found![/green]')

    # Determine exit code based on threshold
    threshold_severity = Severity(severity_threshold.lower())
    threshold_level = SEVERITY_ORDER.get(threshold_severity, 2)

    has_violations_above_threshold = any(SEVERITY_ORDER.get(v.severity, 0) >= threshold_level for v in violations)

    if has_violations_above_threshold:
        sys.exit(1)


@cli.command()
def list_rules() -> None:
    """List all available lint rules."""
    # Import rules to register them
    import dashboard_lint.rules  # pyright: ignore[reportUnusedImport]
    from dashboard_lint.registry import default_registry

    table = Table(title='Available Lint Rules')
    table.add_column('Rule ID', style='cyan')
    table.add_column('Default Severity', style='yellow')
    table.add_column('Description')

    for rule in default_registry.get_all_rules():
        table.add_row(rule.id, rule.default_severity.value, rule.description)

    console.print(table)


if __name__ == '__main__':
    cli()
