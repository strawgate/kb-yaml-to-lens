"""Pytest configuration for kb_dashboard_docs tests."""

from importlib.resources import as_file, files
from pathlib import Path

import pytest


def _has_vendored_content() -> bool:
    """Check if vendored documentation content is available."""
    try:
        resources = files('kb_dashboard_docs.resources')
        llms_full = resources.joinpath('llms-full.txt')
        with as_file(llms_full) as path:
            return Path(path).exists() and Path(path).is_file()
    except (TypeError, FileNotFoundError):
        return False


# Check once at module load time
VENDORED_CONTENT_AVAILABLE = _has_vendored_content()


@pytest.fixture
def requires_vendored_content_fixture() -> None:
    """Fixture that skips tests if vendored content is not available."""
    if not VENDORED_CONTENT_AVAILABLE:
        pytest.skip('Vendored documentation content not available. Run "just vendor-docs" first.')
