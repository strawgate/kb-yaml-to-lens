"""Test that documentation links are not broken.

This test uses pytest-check-links to verify that all links in
markdown documentation files are valid and not broken.
"""


def test_readme_links() -> None:
    """Check links in README.md.

    pytest-check-links will automatically check this file when
    invoked with --check-links flag.
    """


def test_contributing_links() -> None:
    """Check links in CONTRIBUTING.md.

    pytest-check-links will automatically check this file when
    invoked with --check-links flag.
    """


def test_documentation_links() -> None:
    """Check links in all documentation files.

    pytest-check-links will automatically check files in docs/
    when invoked with --check-links flag.
    """
