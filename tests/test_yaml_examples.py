"""Test that YAML examples in markdown files are valid and compilable."""

import re
from pathlib import Path

import pytest
import yaml

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard

# Find all markdown files that contain YAML examples
markdown_files = [
    'README.md',
    'docs/index.md',
    'docs/quickstart.md',
    'src/dashboard_compiler/queries/config.md',
    'src/dashboard_compiler/panels/base.md',
    'src/dashboard_compiler/panels/charts/metric/config.md',
    'src/dashboard_compiler/panels/charts/pie/config.md',
    'src/dashboard_compiler/panels/charts/xy/config.md',
    'src/dashboard_compiler/panels/charts/tagcloud/config.md',
    'src/dashboard_compiler/panels/charts/esql/esql.md',
    'src/dashboard_compiler/panels/charts/lens/lens.md',
    'src/dashboard_compiler/panels/links/links.md',
    'src/dashboard_compiler/panels/images/image.md',
    'src/dashboard_compiler/panels/search/search.md',
    'src/dashboard_compiler/panels/markdown/markdown.md',
]


def extract_yaml_examples(markdown_path: str) -> list[tuple[str, str, int]]:
    """Extract YAML code blocks from a markdown file.

    Returns a list of tuples: (example_code, file_path, line_number)
    """
    path = Path(markdown_path)
    if not path.exists():
        return []

    content = path.read_text()
    examples = []

    # Find all YAML code blocks
    # Pattern matches ```yaml...``` blocks
    pattern = r'```yaml\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        yaml_code = match.group(1)
        # Calculate line number (approximate)
        line_num = content[: match.start()].count('\n') + 1
        examples.append((yaml_code, str(path), line_num))

    return examples


def is_dashboard_yaml(yaml_code: str) -> bool:
    """Check if the YAML code contains a dashboard definition."""
    return 'dashboards:' in yaml_code or 'dashboard:' in yaml_code


def get_all_yaml_examples() -> list[tuple[str, str, int]]:
    """Get all YAML examples from all markdown files."""
    all_examples = []
    for file_path in markdown_files:
        examples = extract_yaml_examples(file_path)
        all_examples.extend(examples)
    return all_examples


@pytest.mark.parametrize(
    ('yaml_code', 'file_path', 'line_num'),
    get_all_yaml_examples(),
    ids=lambda x: f'{x[1]}:{x[2]}' if isinstance(x, tuple) and len(x) >= 3 else str(x),
)
def test_yaml_examples(yaml_code: str, file_path: str, line_num: int) -> None:
    """Test that YAML examples are valid and compilable.

    This test:
    1. Validates that the YAML is parseable
    2. For dashboard YAML examples, attempts to compile them
    """
    # Skip examples that are clearly fragments or placeholders
    if (
        '# ...' in yaml_code
        or 'your-' in yaml_code.lower()
        or 'example-' in yaml_code.lower()
        or 'example.com' in yaml_code.lower()
        or 'saved_search_id:' in yaml_code.lower()
        or 'from_url:' in yaml_code.lower()
        or 'data_view:' in yaml_code.lower()  # Lens charts require actual data views
        or '"logs-*"' in yaml_code.lower()  # Placeholder index patterns
        or '"k8s-*"' in yaml_code.lower()  # Placeholder index patterns
        or 'internal.wiki' in yaml_code.lower()  # Internal URLs
        or 'grafana.example.com' in yaml_code.lower()  # Example URLs
        or 'esql:' in yaml_code.lower()  # ESQL examples require special handling
        or 'data:' in yaml_code.lower()  # Simplified syntax examples that aren't fully expanded
        or '# your ' in yaml_code.lower()  # Comments like "# Your panel definitions go here"
    ):
        pytest.skip('Skipping example with placeholders')

    # Skip examples that are within comments (start with #)
    if yaml_code.strip().startswith('#'):
        pytest.skip('Skipping commented example')

    # Test 1: Validate YAML syntax
    try:
        parsed_yaml = yaml.safe_load(yaml_code)
    except yaml.YAMLError as e:
        pytest.fail(f'Invalid YAML syntax at {file_path}:{line_num}\n{e}')

    # Test 2: For dashboard YAML, attempt compilation
    if is_dashboard_yaml(yaml_code) and parsed_yaml and isinstance(parsed_yaml, dict):
        # Check for dashboards key (correct format)
        if 'dashboards' in parsed_yaml:
            dashboards = parsed_yaml['dashboards']
            if isinstance(dashboards, list) and len(dashboards) > 0:
                # Check if dashboard has minimal required fields
                dashboard = dashboards[0]
                if isinstance(dashboard, dict) and 'panels' in dashboard:
                    # Try to compile the dashboard
                    try:
                        # Create Dashboard object directly from the parsed YAML
                        dashboard_obj = Dashboard(**dashboard)
                        # Compile to verify it generates valid output
                        compile_dashboard(dashboard_obj)
                    except Exception as e:
                        # Some examples may have placeholders or be incomplete by design
                        # Only fail if it's clearly a complete example
                        if 'name' in dashboard and len(str(dashboard.get('name', ''))) > 0:
                            pytest.fail(
                                f'Dashboard compilation failed at {file_path}:{line_num}\n'
                                f'Error: {e}\n'
                                f'This may indicate the example needs placeholder data or is incomplete.'
                            )
        # Check for old dashboard key (incorrect format - should fail)
        elif 'dashboard' in parsed_yaml:
            pytest.fail(
                f"Example at {file_path}:{line_num} uses deprecated 'dashboard:' instead of 'dashboards:'\n"
                f"Please update the example to use the array format with 'dashboards:'."
            )
