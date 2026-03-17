"""Pytest fixtures and options for kb-dashboard-tools tests."""

import io
import json
import os
import re
import shutil
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from ruamel.yaml import YAML

from kb_dashboard_tools.decompile import decompile_dashboard

from .integrations_targets import INTEGRATIONS_DASHBOARD_TARGETS, INTEGRATIONS_PINNED_SHA

_SHA_PATTERN = re.compile(r'^[0-9a-fA-F]{7,40}$')

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
    if _SHA_PATTERN.match(pinned_sha) is None:
        pytest.fail('--integrations-sha must be a valid commit SHA (7-40 hex characters)')

    repo_url = str(request.config.getoption('--integrations-repo-url')).strip() or INTEGRATIONS_REPO_URL
    cache_root = tmp_path_factory.getbasetemp().parent / 'integrations-cache'
    cache_root.mkdir(parents=True, exist_ok=True)
    repo_path = cache_root / pinned_sha

    if not (repo_path / '.git').exists():
        if repo_path.exists():
            shutil.rmtree(repo_path)
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


def _iter_dashboard_objects(path: Path) -> Iterator[dict[str, Any]]:
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.ndjson':
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if len(stripped) == 0:
                continue
            obj = json.loads(stripped)
            if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                yield cast('dict[str, Any]', obj)
        return

    parsed = json.loads(text)
    if isinstance(parsed, dict):
        if parsed.get('type') == 'dashboard':
            yield cast('dict[str, Any]', parsed)
            return
        objects = parsed.get('objects')
        if isinstance(objects, list):
            for obj in objects:
                if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                    yield cast('dict[str, Any]', obj)
            return
    if isinstance(parsed, list):
        for obj in parsed:
            if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                yield cast('dict[str, Any]', obj)


def _decompile_yaml_text(dashboard: dict[str, Any]) -> str:
    canonical = json.loads(json.dumps(decompile_dashboard(dashboard)))
    yaml = YAML(typ='safe')
    yaml_any = cast('Any', yaml)
    yaml_any.sort_base_mapping_type_on_output = False
    stream = io.StringIO()
    yaml.dump(canonical, stream)
    return stream.getvalue()


@pytest.fixture(scope='session')
def integrations_target_files(integrations_repo_path: Path, integrations_pinned_sha: str) -> dict[str, Path]:
    """Resolve hardcoded dashboard files to test from integrations fixture clone."""
    if integrations_pinned_sha != INTEGRATIONS_PINNED_SHA:
        message_template = 'inline snapshots are pinned to {pinned}; got {got}. Use --integrations-sha {pinned}.'
        message = message_template.format(pinned=INTEGRATIONS_PINNED_SHA, got=integrations_pinned_sha)
        pytest.skip(message)

    resolved = {rel: integrations_repo_path / rel for rel in INTEGRATIONS_DASHBOARD_TARGETS}
    missing = [path for path in resolved.values() if not path.exists()]
    if missing:
        pytest.fail(f'missing hardcoded integrations dashboards: {missing}')
    return resolved


@pytest.fixture(scope='session')
def integrations_yaml_for(integrations_target_files: dict[str, Path]) -> Callable[[str], str]:
    """Return decompiled YAML text for a hardcoded integrations dashboard path."""

    def _yaml_for_target(source_rel: str) -> str:
        source_path = integrations_target_files[source_rel]
        first_dashboard = next(_iter_dashboard_objects(source_path), None)
        if first_dashboard is None:
            pytest.fail(f'no dashboard object found in {source_rel}')
        return _decompile_yaml_text(first_dashboard)

    return _yaml_for_target
