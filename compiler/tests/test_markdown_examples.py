"""Test that code examples in markdown files execute successfully."""

from pathlib import Path

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

# Find all Python code examples in markdown files using glob pattern
docs_dir = Path(__file__).parent.parent.parent / 'docs'
# Use absolute paths for pytest-examples since it runs from the compiler directory
markdown_files = sorted(str(p.absolute()) for p in docs_dir.rglob('*.md'))

# Fail fast if no markdown files are found (likely a path or checkout issue)
assert markdown_files, f'No markdown files found in {docs_dir}'


@pytest.mark.parametrize('example', find_examples(*markdown_files), ids=str)
def test_markdown_examples(example: CodeExample, eval_example: EvalExample) -> None:
    """Test that each example in markdown files executes without errors and has correct formatting."""
    if eval_example.update_examples:
        # When updating, format the examples
        eval_example.format(example)
    # When testing, lint and run complete examples only
    # Skip linting/running for incomplete code fragments (they would fail with undefined names)
    elif _is_complete_example(example):
        eval_example.lint(example)
        _ = eval_example.run(example)


def _is_complete_example(example: CodeExample) -> bool:
    """Check if an example is a complete, runnable code snippet."""
    # Examples with imports are typically complete and runnable
    # Fragments without imports that reference undefined variables should be skipped
    code = example.source
    return 'import ' in code or 'from ' in code
