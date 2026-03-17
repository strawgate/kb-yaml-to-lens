"""Pytest fixtures and options for kb-dashboard-tools tests."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from .integrations_targets import INTEGRATIONS_DASHBOARD_TARGETS, INTEGRATIONS_PINNED_SHA

INTEGRATIONS_REPO_URL = 'https://github.com/elastic/integrations.git'
GIT_BIN = shutil.which('git')


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register opt-in integrations test flags."""
    parser.addoption(
        '--run-integrations',
        action='store_true',
        default=False,
        help='Enable tests that clone and read dashboards from elastic/integrations.',
    )
    parser.addoption(
        '--integrations-repo-url',
        action='store',
        default=INTEGRATIONS_REPO_URL,
        help='Git URL for elastic/integrations fixture source.',
    )
    parser.addoption(
        '--integrations-sha',
        action='store',
        default=os.getenv('KB_INTEGRATIONS_SHA', INTEGRATIONS_PINNED_SHA),
        help='Pinned commit SHA to checkout for integrations-backed tests.',
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip integrations-marked tests unless explicitly enabled."""
    if config.getoption('--run-integrations'):
        return
    skip_marker = pytest.mark.skip(reason='requires --run-integrations')
    for item in items:
        if 'integrations' in item.keywords:
            item.add_marker(skip_marker)


def _run_git(command: list[str], cwd: Path | None = None) -> None:
    if GIT_BIN is None:
        pytest.skip('git executable is required for integrations tests')
    subprocess.run(  # noqa: S603
        [GIT_BIN, *command],
        cwd=str(cwd) if cwd is not None else None,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope='session')
def integrations_repo_path(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Clone elastic/integrations at a pinned SHA (session cached)."""
    if not request.config.getoption('--run-integrations'):
        pytest.skip('requires --run-integrations')

    pinned_sha = str(request.config.getoption('--integrations-sha')).strip()
    if len(pinned_sha) == 0:
        pytest.skip('set --integrations-sha (or KB_INTEGRATIONS_SHA) to pin fixture source')

    repo_url = str(request.config.getoption('--integrations-repo-url')).strip() or INTEGRATIONS_REPO_URL
    cache_root = tmp_path_factory.getbasetemp().parent / 'integrations-cache'
    cache_root.mkdir(parents=True, exist_ok=True)
    repo_path = cache_root / pinned_sha

    if not repo_path.exists():
        _run_git(['clone', '--filter=blob:none', '--sparse', repo_url, str(repo_path)])
    _run_git(['fetch', '--depth=1', 'origin', pinned_sha], cwd=repo_path)
    _run_git(['checkout', '--force', pinned_sha], cwd=repo_path)
    _run_git(['sparse-checkout', 'init', '--no-cone'], cwd=repo_path)
    _run_git(['sparse-checkout', 'set', '--skip-checks', *INTEGRATIONS_DASHBOARD_TARGETS], cwd=repo_path)

    return repo_path


@pytest.fixture(scope='session')
def integrations_pinned_sha(request: pytest.FixtureRequest) -> str:
    """Return pinned integrations SHA used for fixture checkout."""
    pinned_sha = str(request.config.getoption('--integrations-sha')).strip()
    if len(pinned_sha) == 0:
        pytest.skip('set --integrations-sha (or KB_INTEGRATIONS_SHA) to pin fixture source')
    return pinned_sha
