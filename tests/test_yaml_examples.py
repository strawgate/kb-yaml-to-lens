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


def _has_skip_marker(info_string: str) -> bool:
    """Check if a code fence info string contains a skip marker.

    Args:
        info_string: The text after the language identifier in a code fence (e.g., "skip" in ```yaml skip).

    Returns:
        True if the info string contains the word "skip" (case-insensitive).

    Examples:
        >>> _has_skip_marker("skip")
        True
        >>> _has_skip_marker("test skip example")
        True
        >>> _has_skip_marker("")
        False
    """
    return 'skip' in info_string.lower().split()


def _is_placeholder_example(yaml_content: str) -> bool:
    """Check if a YAML example contains placeholder text that indicates it's not a complete example.

    Args:
        yaml_content: The YAML content to check.

    Returns:
        True if the content contains placeholders like ellipsis, "your-" prefixes, or example.com domains.

    Examples:
        >>> _is_placeholder_example("field: ...")
        True
        >>> _is_placeholder_example("url: your-url.com")
        True
        >>> _is_placeholder_example("field: value")
        False
    """
    return '...' in yaml_content or '# ...' in yaml_content or 'your-' in yaml_content.lower() or 'example.com' in yaml_content


def _should_skip_compilation(yaml_content: str, skip: bool) -> bool:
    """Determine if a YAML example should be skipped from compilation testing.

    An example should be skipped if:
    - It has an explicit skip marker in the code fence
    - It contains placeholder text (ellipsis, "your-" prefixes, example.com)
    - It doesn't contain a top-level "dashboards:" key (fragment/incomplete)
    - It contains placeholder comments for user input

    Args:
        yaml_content: The YAML content to evaluate.
        skip: Whether the code fence had an explicit skip marker.

    Returns:
        True if the example should be skipped from compilation tests.
    """
    return (
        skip
        or _is_placeholder_example(yaml_content)
        or 'dashboards:' not in yaml_content
        or '# Your panel definitions go here' in yaml_content
    )


def extract_yaml_examples(file_path: str) -> list[tuple[str, int, bool]]:
    """Extract YAML code blocks from a markdown file.

    Parses markdown files to find all YAML code blocks (delimited by ```yaml fences).
    Supports skip markers in the code fence info string to mark examples that should
    be excluded from validation/compilation tests.

    Args:
        file_path: Path to the markdown file to parse.

    Returns:
        List of tuples containing:
        - yaml_content (str): The YAML code block content
        - line_number (int): The line number where the code block starts
        - skip (bool): Whether the code fence has a skip marker (e.g., ```yaml skip)

    Examples:
        >>> examples = extract_yaml_examples("docs/quickstart.md")
        >>> yaml_content, line_num, skip = examples[0]
    """
    content = Path(file_path).read_text()
    examples = []

    # Find all ```yaml code blocks, capturing optional info string after 'yaml'
    # Matches: ```yaml, ```yaml skip, ```yaml test="skip", etc.
    pattern = r'```yaml([^\n]*)\n(.*?)```'
    for match in re.finditer(pattern, content, re.DOTALL):
        info_string = match.group(1).strip()
        yaml_content = match.group(2)
        # Calculate line number
        line_num = content[: match.start()].count('\n') + 1
        # Check if skip marker is present in the info string
        should_skip = _has_skip_marker(info_string)
        examples.append((yaml_content, line_num, should_skip))

    return examples


@pytest.mark.parametrize('file_path', markdown_files)
def test_yaml_examples_use_dashboards_format(file_path: str) -> None:
    """Test that YAML examples use 'dashboards:' (plural) not 'dashboard:' (singular).

    Validates that all YAML examples use the current array format (dashboards:) instead of
    the deprecated singular format (dashboard:). Skips examples with explicit skip markers.
    """
    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num, skip in examples:
        if skip:
            continue  # Skip examples marked with 'skip' in code fence
        # Check if this example contains a dashboard definition
        # Look for the top-level dashboard: key (not dashboard: inside links/other fields)
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
    """Test that YAML examples have valid syntax.

    Validates that all YAML code blocks in documentation can be parsed by PyYAML.
    Skips examples with explicit skip markers or placeholder content.
    """
    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num, skip in examples:
        # Skip examples marked with 'skip' in code fence or with placeholders
        if skip or _is_placeholder_example(yaml_content):
            continue

        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            pytest.fail(f'{file_path}:{line_num} - Invalid YAML syntax: {e}')


@pytest.mark.parametrize('file_path', markdown_files)
def test_yaml_examples_compilable(file_path: str, tmp_path: Path) -> None:
    """Test that complete YAML examples can be loaded by the dashboard compiler.

    Validates that YAML examples can be successfully compiled by the dashboard compiler.
    Skips examples with explicit skip markers, placeholder content, or fragments that
    don't represent complete dashboard configurations.
    """
    from dashboard_compiler.dashboard_compiler import load

    examples = extract_yaml_examples(file_path)

    for yaml_content, line_num, skip in examples:
        # Skip examples marked with 'skip' in code fence, or that are fragments/placeholders
        if _should_skip_compilation(yaml_content, skip):
            continue

        try:
            temp_yaml = tmp_path / f'example_{line_num}.yaml'
            _ = temp_yaml.write_text(yaml_content)

            dashboards = load(str(temp_yaml))
            assert len(dashboards) > 0, 'Should load at least one dashboard'
        except Exception as e:
            pytest.fail(f'{file_path}:{line_num} - Failed to compile YAML: {e}')
