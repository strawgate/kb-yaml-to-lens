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

    def test_compile_writes_combined_ndjson_by_default(self, tmp_path: Path) -> None:
        """Compile should succeed and write combined NDJSON output by default."""
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()

        valid_yaml = input_dir / 'valid.yaml'
        valid_yaml.write_text("""
dashboards:
  - name: Test Dashboard
    panels:
      - markdown:
          content: Hello
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

        assert result.exit_code == 0
        assert (output_dir / 'compiled_dashboards.ndjson').exists()

    def test_compile_writes_individual_json_files_with_format_json(self, tmp_path: Path) -> None:
        """Compile should succeed and write per-dashboard JSON files when format=json."""
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()

        valid_yaml = input_dir / 'valid.yaml'
        valid_yaml.write_text("""
dashboards:
  - name: Test Dashboard
    panels:
      - markdown:
          content: Hello
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
                '--format',
                'json',
            ],
        )

        assert result.exit_code == 0
        assert len(list(output_dir.glob('*.json'))) == 1

    def test_compile_rejects_deprecated_fields_without_flag(self, tmp_path: Path) -> None:
        """Compile should fail when deprecated fields are present and flag is not set."""
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()

        deprecated_yaml = input_dir / 'deprecated.yaml'
        deprecated_yaml.write_text("""\
dashboards:
  - name: Deprecated Dashboard
    panels:
      - title: Deprecated Pie
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: pie
          query: |
            FROM logs-* | STATS total = COUNT(*) BY service.name
          metrics:
            - field: total
          breakdowns:
            - field: service.name
          titles_and_text:
            slice_values: integer
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
        assert '--allow-deprecated' in result.output

    def test_compile_accepts_deprecated_fields_with_flag(self, tmp_path: Path) -> None:
        """Compile should succeed for deprecated fields when --allow-deprecated is set."""
        input_dir = tmp_path / 'input'
        output_dir = tmp_path / 'output'
        input_dir.mkdir()

        deprecated_yaml = input_dir / 'deprecated.yaml'
        deprecated_yaml.write_text("""\
dashboards:
  - name: Deprecated Dashboard
    panels:
      - title: Deprecated Pie
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: pie
          query: |
            FROM logs-* | STATS total = COUNT(*) BY service.name
          metrics:
            - field: total
          breakdowns:
            - field: service.name
          titles_and_text:
            slice_values: integer
""")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--allow-deprecated',
                '--input-dir',
                str(input_dir),
                '--output-dir',
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        assert (output_dir / 'compiled_dashboards.ndjson').exists()
