"""Tests for compile command file output behavior."""

from pathlib import Path

from click.testing import CliRunner

from dashboard_compiler.cli import cli

VALID_DASHBOARD_YAML = """\
dashboards:
  - name: Test Dashboard
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello World
"""


class TestSingleFileCompilation:
    """Test compile command with --input-file option."""

    def test_single_file_produces_only_combined_output(self, tmp_path: Path) -> None:
        """When using --input-file, only the combined output file should be created."""
        input_dir = tmp_path / 'inputs' / 'my-project'
        input_dir.mkdir(parents=True)
        yaml_file = input_dir / 'dashboard.yaml'
        yaml_file.write_text(VALID_DASHBOARD_YAML)

        output_dir = tmp_path / 'output'

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--input-file',
                str(yaml_file),
                '--output-dir',
                str(output_dir),
                '--output-file',
                'combined.ndjson',
            ],
        )

        assert result.exit_code == 0, f'Command failed: {result.output}'

        output_files = list(output_dir.glob('*.ndjson'))
        assert len(output_files) == 1, f'Expected 1 output file, got {len(output_files)}: {[f.name for f in output_files]}'
        assert output_files[0].name == 'combined.ndjson'

    def test_single_file_does_not_create_directory_based_file(self, tmp_path: Path) -> None:
        """When using --input-file, no directory-based file (named after parent dir) should be created."""
        input_dir = tmp_path / 'inputs' / 'cursor-analytics'
        input_dir.mkdir(parents=True)
        yaml_file = input_dir / 'dashboard.yaml'
        yaml_file.write_text(VALID_DASHBOARD_YAML)

        output_dir = tmp_path / 'output'

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--input-file',
                str(yaml_file),
                '--output-dir',
                str(output_dir),
                '--output-file',
                'my-output.ndjson',
            ],
        )

        assert result.exit_code == 0, f'Command failed: {result.output}'

        # Should NOT have a file named after the parent directory
        directory_based_file = output_dir / 'cursor-analytics.ndjson'
        assert directory_based_file.exists() is False, f'Directory-based file should not exist: {directory_based_file}'

        # Should have only the specified output file
        specified_file = output_dir / 'my-output.ndjson'
        assert specified_file.exists() is True, f'Combined output file should exist: {specified_file}'


class TestDirectoryCompilation:
    """Test compile command with --input-dir option (directory mode)."""

    def test_directory_mode_creates_individual_and_combined_files(self, tmp_path: Path) -> None:
        """When using --input-dir, both individual directory-based files and combined file should be created."""
        input_dir = tmp_path / 'inputs'
        project1_dir = input_dir / 'project1'
        project2_dir = input_dir / 'project2'
        project1_dir.mkdir(parents=True)
        project2_dir.mkdir(parents=True)

        (project1_dir / 'dashboard.yaml').write_text(VALID_DASHBOARD_YAML)
        (project2_dir / 'dashboard.yaml').write_text(VALID_DASHBOARD_YAML)

        output_dir = tmp_path / 'output'

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--input-dir',
                str(input_dir),
                '--output-dir',
                str(output_dir),
                '--output-file',
                'combined.ndjson',
            ],
        )

        assert result.exit_code == 0, f'Command failed: {result.output}'

        # Should have individual files for each directory
        assert (output_dir / 'project1.ndjson').exists() is True
        assert (output_dir / 'project2.ndjson').exists() is True

        # Should also have the combined file
        assert (output_dir / 'combined.ndjson').exists() is True

        # Total of 3 files
        output_files = list(output_dir.glob('*.ndjson'))
        assert len(output_files) == 3


class TestOutputDirectory:
    """Test output directory path behavior."""

    def test_output_dir_is_relative_to_cwd(self, tmp_path: Path) -> None:
        """Output directory should be relative to the current working directory."""
        # Create input file
        input_file = tmp_path / 'dashboard.yaml'
        input_file.write_text(VALID_DASHBOARD_YAML)

        # Create a working directory
        work_dir = tmp_path / 'workdir'
        work_dir.mkdir()

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=work_dir):
            result = runner.invoke(
                cli,
                [
                    'compile',
                    '--input-file',
                    str(input_file),
                    '--output-dir',
                    'my-output',
                    '--output-file',
                    'result.ndjson',
                ],
            )

            assert result.exit_code == 0, f'Command failed: {result.output}'

            # Output should be in the current working directory
            output_path = Path('my-output') / 'result.ndjson'
            assert output_path.exists() is True, f'Output file should exist at {output_path}'

    def test_explicit_output_dir_is_respected(self, tmp_path: Path) -> None:
        """Explicit --output-dir path should be respected."""
        input_file = tmp_path / 'dashboard.yaml'
        input_file.write_text(VALID_DASHBOARD_YAML)

        explicit_output_dir = tmp_path / 'explicit-output'

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'compile',
                '--input-file',
                str(input_file),
                '--output-dir',
                str(explicit_output_dir),
                '--output-file',
                'result.ndjson',
            ],
        )

        assert result.exit_code == 0, f'Command failed: {result.output}'
        assert (explicit_output_dir / 'result.ndjson').exists() is True
