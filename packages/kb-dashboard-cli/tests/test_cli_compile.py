"""Tests for compile command failure exit behavior."""

from pathlib import Path

from click.testing import CliRunner

from dashboard_compiler.cli import cli


class TestCompileCommand:
    """Tests for compile command exit codes on validation failures."""

    def test_compile_exits_non_zero_when_all_inputs_fail_validation(self, tmp_path: Path) -> None:
        """Compile should return non-zero when no dashboards compile successfully."""
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()

        invalid_yaml = input_dir / 'invalid.yaml'
        invalid_yaml.write_text("""
dashboards:
  - description: Missing required name
    panels: []
""")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--input-dir',
                str(input_dir),
                '--output-dir',
                str(output_dir),
            ],
        )

        assert result.exit_code == 1
        assert 'No valid YAML configurations found or compiled.' in result.output
