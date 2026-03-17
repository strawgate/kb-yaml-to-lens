"""Tests for compile command failure exit behavior."""

import json
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

    def test_compile_writes_elastic_integrations_json_with_unwrapped_fields(self, tmp_path: Path) -> None:
        """Compile should write integrations-style JSON with parsed nested fields."""
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
                'elastic-integrations',
            ],
        )

        assert result.exit_code == 0
        output_files = list(output_dir.glob('*.json'))
        assert len(output_files) == 1
        assert output_files[0].name.startswith('input-')

        compiled = json.loads(output_files[0].read_text(encoding='utf-8'))
        assert isinstance(compiled['attributes']['panelsJSON'], list)
        assert isinstance(compiled['attributes']['optionsJSON'], dict)
        assert isinstance(compiled['attributes']['kibanaSavedObjectMeta']['searchSourceJSON'], dict)
        assert isinstance(compiled['attributes']['controlGroupInput']['ignoreParentSettingsJSON'], dict)
        assert isinstance(compiled['attributes']['controlGroupInput']['panelsJSON'], dict)

    def test_compile_elastic_integrations_uses_explicit_package_name(self, tmp_path: Path) -> None:
        """Explicit package name should prefix elastic-integrations filenames."""
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
                'elastic-integrations',
                '--elastic-package-name',
                'nginx_otel',
            ],
        )

        assert result.exit_code == 0
        output_files = list(output_dir.glob('*.json'))
        assert len(output_files) == 1
        assert output_files[0].name.startswith('nginx_otel-')

    def test_compile_elastic_integrations_input_file_uses_parent_directory_name(self, tmp_path: Path) -> None:
        """When --input-file is outside --input-dir, use parent directory as package prefix."""
        package_dir = tmp_path / 'system_otel'
        output_dir = tmp_path / 'output'
        package_dir.mkdir()

        valid_yaml = package_dir / 'valid.yaml'
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
                '--input-file',
                str(valid_yaml),
                '--output-dir',
                str(output_dir),
                '--format',
                'elastic-integrations',
            ],
        )

        assert result.exit_code == 0
        output_files = list(output_dir.glob('*.json'))
        assert len(output_files) == 1
        assert output_files[0].name.startswith('system_otel-')

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
