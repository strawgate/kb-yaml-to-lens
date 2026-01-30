"""Test that YAML examples in markdown files use correct format and can compile."""

import re
from pathlib import Path

import pytest
import yaml

# Automatically discover markdown files that contain YAML dashboard examples
_project_root = Path(__file__).parent.parent.parent.parent
_docs_dir = _project_root / 'packages' / 'kb-dashboard-docs'

# Find all markdown files in the repository (use absolute paths since tests run from compiler/)
_all_markdown_files = sorted(str(p.absolute()) for p in [_project_root / 'README.md', *_docs_dir.rglob('*.md')] if p.exists())

# Exclude files that shouldn't be tested (add patterns here if needed)
_excluded_patterns = [
    # 'docs/dev/',  # Example: exclude development docs
]

markdown_files = [f for f in _all_markdown_files if not any(pattern in f for pattern in _excluded_patterns)]


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
        skip is True
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
    content = Path(file_path).read_text(encoding='utf-8')
    examples: list[tuple[str, int, bool]] = []

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


def _collect_all_yaml_examples() -> tuple[list[tuple[str, str, int, bool]], list[str]]:
    """Collect all YAML examples from all markdown files.

    Returns:
        Tuple containing:
        - List of tuples (file_path, yaml_content, line_number, skip)
        - List of test IDs in the format "file_path:line_number"
    """
    all_examples: list[tuple[str, str, int, bool]] = []
    all_ids: list[str] = []
    for file_path in markdown_files:
        examples = extract_yaml_examples(file_path)
        for yaml_content, line_num, skip in examples:
            all_examples.append((file_path, yaml_content, line_num, skip))
            all_ids.append(f'{file_path}:{line_num}')
    return all_examples, all_ids


# Collect examples and IDs once at module level
_all_yaml_examples, _all_yaml_example_ids = _collect_all_yaml_examples()


@pytest.mark.parametrize(
    ('file_path', 'yaml_content', 'line_num', 'skip'),
    _all_yaml_examples,
    ids=_all_yaml_example_ids,
)
def test_yaml_examples(file_path: str, yaml_content: str, line_num: int, skip: bool, tmp_path: Path) -> None:
    """Test that YAML examples have valid syntax and can be compiled.

    Validates that YAML examples:
    1. Have valid YAML syntax (can be parsed by PyYAML)
    2. Can be successfully compiled by the dashboard compiler (if they are complete examples)

    Skips examples with explicit skip markers or placeholder content.
    """
    from kb_dashboard_core.dashboard_compiler import load

    if skip is True or _is_placeholder_example(yaml_content) is True:
        pytest.skip('Example marked with skip or contains placeholders')

    # First, validate YAML syntax
    try:
        yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        pytest.fail(f'{file_path}:{line_num} - Invalid YAML syntax: {e}')

    # Then, validate compilation (if this is a complete example)
    if _should_skip_compilation(yaml_content, skip):
        pytest.skip('Example is a fragment or contains placeholders')

    try:
        temp_yaml = tmp_path / f'example_{line_num}.yaml'
        _ = temp_yaml.write_text(yaml_content, encoding='utf-8')

        dashboards = load(str(temp_yaml))
        assert len(dashboards) > 0, 'Should load at least one dashboard'
    except Exception as e:
        pytest.fail(f'{file_path}:{line_num} - Failed to compile YAML: {e}')
