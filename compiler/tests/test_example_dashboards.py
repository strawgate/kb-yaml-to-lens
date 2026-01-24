"""Test that example dashboards in docs/content/examples/ compile successfully."""

from pathlib import Path

import pytest

from dashboard_compiler.dashboard_compiler import load

# Find all YAML files in docs/content/examples (recursively)
# Use absolute path since tests run from compiler/ directory
_project_root = Path(__file__).parent.parent.parent
example_dir = _project_root / 'docs' / 'content' / 'examples'

example_files = sorted(f for f in example_dir.rglob('*.yaml'))

# Ensure we actually found example files (fail fast if path is wrong)
assert len(example_files) > 0, (
    f'No example YAML files found in {example_dir}. '
    f'Expected to find files but got empty list. '
    f'This indicates a test infrastructure bug - please check the path configuration.'
)

# Files with known validation issues from elastic/integrations repository.
# These use schema patterns (e.g., format.decimals, legacy panel structures) that
# predate current compiler schema.
# TODO: Fix these files to use the current schema.
# See: https://github.com/strawgate/kb-yaml-to-lens/issues/1049
_KNOWN_FAILING_FILES = {
    # All elastic_agent files have validation issues inherited from elastic/integrations
    'elastic_agent/',
}


def _is_known_failing(path: Path) -> bool:
    """Check if a path matches a known failing file pattern."""
    path_str = str(path)
    return any(pattern in path_str for pattern in _KNOWN_FAILING_FILES)


@pytest.mark.parametrize('example_path', example_files, ids=lambda p: str(p))
def test_example_dashboard_compiles(example_path: Path) -> None:
    """Test that each example dashboard compiles without errors.

    Args:
        example_path: Path to the example YAML file to compile.

    """
    if _is_known_failing(example_path):
        pytest.xfail('Known validation issue with format.decimals - see issue #1049')

    dashboards = load(str(example_path))
    assert len(dashboards) > 0, f'Should load at least one dashboard from {example_path}'
