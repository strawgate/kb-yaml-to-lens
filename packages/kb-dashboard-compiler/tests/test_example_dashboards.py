"""Test that example dashboards in packages/kb-dashboard-docs/content/examples/ compile successfully."""

from pathlib import Path

import pytest

from dashboard_compiler.dashboard_compiler import load

# Find all YAML files in packages/kb-dashboard-docs/content/examples (recursively)
# Use absolute path since tests run from packages/kb-dashboard-compiler directory
_project_root = Path(__file__).parent.parent.parent.parent
example_dir = _project_root / 'packages' / 'kb-dashboard-docs' / 'content' / 'examples'

example_files = sorted(f for f in example_dir.rglob('*.yaml'))

# Ensure we actually found example files (fail fast if path is wrong)
assert len(example_files) > 0, (
    f'No example YAML files found in {example_dir}. '
    f'Expected to find files but got empty list. '
    f'This indicates a test infrastructure bug - please check the path configuration.'
)


@pytest.mark.parametrize('example_path', example_files, ids=lambda p: str(p))
def test_example_dashboard_compiles(example_path: Path) -> None:
    """Test that each example dashboard compiles without errors.

    Args:
        example_path: Path to the example YAML file to compile.

    """
    dashboards = load(str(example_path))
    assert len(dashboards) > 0, f'Should load at least one dashboard from {example_path}'
