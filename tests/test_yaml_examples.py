"""Test that YAML examples in markdown files use correct format and can compile."""

import re
from pathlib import Path

import pytest
import yaml

# Markdown files that contain YAML dashboard examples
markdown_files = [
    'README.md',
    'docs/index.md',
    'docs/quickstart.md',
    'docs/panels/base.md',
    'docs/panels/esql.md',
    'docs/panels/image.md',
    'docs/panels/lens.md',
    'docs/panels/links.md',
    'docs/panels/markdown.md',
    'docs/panels/metric.md',
    'docs/panels/pie.md',
    'docs/panels/search.md',
    'docs/panels/tagcloud.md',
    'docs/panels/xy.md',
    'docs/queries/config.md',
]


def extract_yaml_examples(file_path: str) -> list[tuple[str, int]]:
    """Extract YAML code blocks from a markdown file.

    Returns list of (yaml_content, line_number) tuples.
    """
    content = Path(file_path).read_text()
    examples = []

    pattern = r'```yaml\n(.*?)```'
    for match in re.finditer(pattern, content, re.DOTALL):
        yaml_content = match.group(1)
        line_num = content[: match.start()].count('\n') + 1
        examples.append((yaml_content, line_num))

    return examples


@pytest.mark.parametrize('file_path', markdown_files)
def test_yaml_examples_use_dashboards_format(file_path: str) -> None:
    """Test that YAML examples use 'dashboards:' (plural) not 'dashboard:' (singular)."""
    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num in examples:
        lines = yaml_content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                continue
            if line.startswith('dashboard:'):
                msg = (
                    f"{file_path}:{line_num} - YAML example uses deprecated 'dashboard:' format. "
                    "Use 'dashboards:' (plural, array format) instead."
                )
                pytest.fail(msg)


@pytest.mark.parametrize('file_path', markdown_files)
def test_yaml_examples_valid_syntax(file_path: str) -> None:
    """Test that YAML examples have valid syntax."""
    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num in examples:
        if '...' in yaml_content or 'your-' in yaml_content.lower() or '# ...' in yaml_content:
            pytest.skip(f'Skipping example with placeholders at {file_path}:{line_num}')

        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            pytest.fail(f'{file_path}:{line_num} - Invalid YAML syntax: {e}')


@pytest.mark.parametrize('file_path', markdown_files)
def test_yaml_examples_compilable(file_path: str, tmp_path: Path) -> None:
    """Test that complete YAML examples can be loaded by the dashboard compiler."""
    from dashboard_compiler.dashboard_compiler import load

    placeholder_docs = [
        'docs/panels/esql.md',
        'docs/panels/lens.md',
        'docs/panels/tagcloud.md',
    ]
    if file_path in placeholder_docs:
        pytest.skip(f'Skipping doc with placeholder examples: {file_path}')

    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num in examples:
        if (
            '...' in yaml_content
            or '# ...' in yaml_content
            or 'your-' in yaml_content.lower()
            or 'example.com' in yaml_content
            or 'dashboards:' not in yaml_content
            or '# Your panel definitions go here' in yaml_content
        ):
            pytest.skip(f'Skipping incomplete/placeholder example at {file_path}:{line_num}')

        try:
            temp_yaml = tmp_path / f'example_{line_num}.yaml'
            _ = temp_yaml.write_text(yaml_content)

            dashboards = load(str(temp_yaml))
            assert len(dashboards) > 0, 'Should load at least one dashboard'
        except Exception as e:
            pytest.fail(f'{file_path}:{line_num} - Failed to compile YAML: {e}')
