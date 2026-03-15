"""CLI tests for dashboard lint output."""

from pathlib import Path

from click.testing import CliRunner

from dashboard_lint.cli import cli


def test_check_prints_warning_for_from_metrics_dashboard() -> None:
    """CLI should print warning output for FROM metrics-* dashboards."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'from_metrics_warning_dashboard.yaml'
    runner = CliRunner()

    result = runner.invoke(cli, ['check', '--input-file', str(fixture_path)])

    assert result.exit_code == 1
    assert 'esql-ts-metrics-min-version' in result.output
    assert 'FROM metrics-* should use TS metrics-*' in result.output


def test_check_prints_warning_for_from_metrics_inside_collapsible_dashboard() -> None:
    """CLI should print warning output for FROM metrics-* dashboards inside sections."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'from_metrics_warning_collapsible_dashboard.yaml'
    runner = CliRunner()

    result = runner.invoke(cli, ['check', '--input-file', str(fixture_path)])

    assert result.exit_code == 1
    assert 'esql-ts-metrics-min-version' in result.output
    assert 'FROM metrics-* should use TS metrics-*' in result.output
