"""Test that code examples in markdown files execute successfully."""

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

# Find all Python code examples in markdown files
markdown_files = [
    'docs/programmatic-usage.md',
    'docs/api/panels.md',
    'docs/panels/image.md',
    'docs/panels/links.md',
    'docs/panels/markdown.md',
    'docs/panels/metric.md',
    'docs/panels/pie.md',
    'docs/panels/search.md',
    'docs/panels/xy.md',
]


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
        eval_example.run(example)


def _is_complete_example(example: CodeExample) -> bool:
    """Check if an example is a complete, runnable code snippet."""
    # Examples with imports are typically complete and runnable
    # Fragments without imports that reference undefined variables should be skipped
    code = example.source
    return 'import ' in code or 'from ' in code
