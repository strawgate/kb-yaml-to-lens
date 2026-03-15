"""Tests for compare command registration and behavior."""

import json
import re
from pathlib import Path

from click.testing import CliRunner

from dashboard_compiler.cli import cli

ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


def _write_panel(output_dir: Path, filename: str, panel_type: str, title: str) -> None:
    panels_dir = output_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    panel_payload = {
        'type': panel_type,
        'title': title,
    }
    (panels_dir / filename).write_text(json.dumps(panel_payload), encoding='utf-8')


class TestCompareCommandRegistration:
    """Tests for compare command registration in the main CLI."""

    def test_compare_command_is_registered(self) -> None:
        """Compare command is available from the top-level CLI."""
        command_names = list(cli.commands)
        assert 'compare' in command_names


class TestCompareCommand:
    """Tests for compare command output and failure behavior."""

    def test_compare_reports_matching_panels(self, tmp_path: Path) -> None:
        """Compare succeeds and reports a matching summary when panel types align."""
        original_dir = tmp_path / 'original'
        compiled_dir = tmp_path / 'compiled'
        _write_panel(original_dir, '000_panel_a_lens.json', 'lens', 'CPU Usage')
        _write_panel(compiled_dir, '000_panel_a_lens.json', 'lens', 'CPU Usage')

        runner = CliRunner()
        result = runner.invoke(cli, ['compare', str(original_dir), str(compiled_dir)])
        output = ANSI_ESCAPE_PATTERN.sub('', result.output)

        assert result.exit_code == 0
        assert 'Original panels: 1' in output
        assert 'Compiled panels: 1' in output
        assert 'All panels match!' in output

    def test_compare_fails_when_panels_dir_missing(self, tmp_path: Path) -> None:
        """Compare returns a non-zero exit code when panels directory is missing."""
        original_dir = tmp_path / 'original'
        compiled_dir = tmp_path / 'compiled'
        original_dir.mkdir()
        compiled_dir.mkdir()
        (original_dir / 'panels').mkdir()

        runner = CliRunner()
        result = runner.invoke(cli, ['compare', str(original_dir), str(compiled_dir)])

        assert result.exit_code != 0
        assert 'Error comparing disassembled dashboards:' in result.output
