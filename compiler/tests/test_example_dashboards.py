"""Test that example dashboards in docs/examples/ compile successfully."""

from pathlib import Path

import pytest

from dashboard_compiler.dashboard_compiler import load

# Find all YAML files in docs/examples (recursively)
example_dir = Path('docs/examples')
example_files = sorted(example_dir.rglob('*.yaml'))


@pytest.mark.parametrize('example_path', example_files, ids=lambda p: str(p))
def test_example_dashboard_compiles(example_path: Path) -> None:
    """Test that each example dashboard compiles without errors.

    Args:
        example_path: Path to the example YAML file to compile.

    """
    dashboards = load(str(example_path))
    assert len(dashboards) > 0, f'Should load at least one dashboard from {example_path}'
