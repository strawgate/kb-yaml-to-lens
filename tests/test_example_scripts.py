"""Test that example Python scripts execute successfully."""

import subprocess
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / 'examples'
EXAMPLE_SCRIPTS = list(EXAMPLES_DIR.glob('*.py'))


@pytest.mark.parametrize('script_path', EXAMPLE_SCRIPTS, ids=lambda p: p.name)
def test_example_script_runs(script_path: Path) -> None:
    """Test that each example script executes without errors."""
    result = subprocess.run(
        ['python', str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f'Example script {script_path.name} failed with return code {result.returncode}\n'
        f'STDOUT:\n{result.stdout}\n'
        f'STDERR:\n{result.stderr}'
    )

    # Verify that the script produces NDJSON output
    assert result.stdout.strip(), f'Example script {script_path.name} produced no output'
