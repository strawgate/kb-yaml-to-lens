"""Test that YAML examples in docstrings can be compiled successfully."""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.loader import DashboardConfig


def find_docstring_yaml_examples() -> list[dict[str, str]]:
    """Find all YAML examples in Python docstrings in config files."""
    config_dir = Path(__file__).parent.parent / 'src' / 'dashboard_compiler'

    examples: list[dict[str, str]] = []

    for py_file in config_dir.rglob('*/config.py'):
        content = py_file.read_text()

        # Find all docstrings with Examples sections containing YAML
        # Pattern matches:
        # 1. Docstring start: """
        # 2. Examples: section
        # 3. Code block with yaml language marker
        pattern = r'""".*?Examples:\s*\n(.*?)```yaml\n(.*?)```'

        for match in re.finditer(pattern, content, re.DOTALL):
            yaml_content = match.group(2)
            # Extract the example title/description if present
            description_match = re.search(r'([^\n]+):\s*$', match.group(1).strip())
            description = description_match.group(1) if description_match else 'Example'

            examples.append(
                {'file': str(py_file.relative_to(config_dir.parent.parent)), 'description': description, 'yaml': yaml_content.strip()}
            )

    return examples


# Collect all examples at module load time
EXAMPLES = find_docstring_yaml_examples()


def test_examples_exist() -> None:
    """Ensure that we found some docstring examples to test."""
    assert EXAMPLES, 'No YAML examples found in docstrings'


@pytest.mark.parametrize('example', EXAMPLES, ids=lambda ex: f'{ex["file"]}::{ex["description"]}')
def test_docstring_yaml_example(example: dict[str, Any]) -> None:
    """Test that each YAML example in docstrings can be compiled successfully."""
    yaml_content = example['yaml']

    # Parse the YAML
    try:
        config = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        pytest.fail(f'Invalid YAML in {example["file"]} - {example["description"]}: {e}')

    # Check if this is a full dashboard configuration
    if 'dashboards' in config:
        try:
            dashboard_config = DashboardConfig.model_validate(config)
            for dashboard in dashboard_config.dashboards:
                result = compile_dashboard(dashboard)
                assert result, f'Compilation failed for {example["file"]} - {example["description"]}'
        except Exception as e:
            pytest.fail(f'Compilation error in {example["file"]} - {example["description"]}: {e}')
    # Check if this is a single dashboard object
    elif 'panels' in config:
        # Full dashboard - validate and compile it directly
        try:
            dashboard = Dashboard.model_validate(config)
            result = compile_dashboard(dashboard)
            assert result, f'Compilation failed for {example["file"]} - {example["description"]}'
        except Exception as e:
            pytest.fail(f'Compilation error in {example["file"]} - {example["description"]}: {e}')
    else:
        # Panel snippet - wrap it in a minimal dashboard
        # Determine the panel type from the top-level keys
        supported_keys = {'lens', 'esql', 'markdown', 'image', 'text', 'map'}
        if any(key in config for key in supported_keys):
            panel_config = config
        else:
            # Unknown format - skip
            pytest.skip(f'Example is not a full dashboard and cannot be auto-wrapped: {example["description"]}')

        # Create a minimal dashboard with this panel
        dashboard_dict = {'name': f'Test Dashboard for {example["description"]}', 'panels': [panel_config]}

        try:
            dashboard = Dashboard.model_validate(dashboard_dict)
            result = compile_dashboard(dashboard)
            assert result, f'Compilation failed for {example["file"]} - {example["description"]}'
        except Exception as e:
            pytest.fail(f'Compilation error in {example["file"]} - {example["description"]}: {e}')
