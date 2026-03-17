"""Opt-in integrations-backed decompiler tests."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from kb_dashboard_core.dashboard_compiler import load, render
from kb_dashboard_core.loader import DashboardConfig

from kb_dashboard_tools.decompile import decompile_dashboard

_MAX_AUTO_TARGETS = 12


def _dashboard_files(repo_path: Path) -> list[Path]:
    files = [p for p in repo_path.rglob('*') if p.suffix in {'.json', '.ndjson'} and '/kibana/dashboard/' in p.as_posix()]
    return sorted(files)


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


def _panel_keys(panel: dict[str, Any]) -> set[str]:
    reserved = {'id', 'title', 'description', 'size', 'position', 'collapsed', 'section'}
    return {k for k in panel if k not in reserved}


@pytest.fixture(scope='session')
def integrations_target_files(request: pytest.FixtureRequest, integrations_repo_path: Path) -> list[Path]:
    """Resolve dashboard files to test from integrations fixture clone."""
    explicit = [Path(p) for p in request.config.getoption('--integrations-dashboard')]
    if explicit:
        resolved = [integrations_repo_path / p for p in explicit]
        missing = [p for p in resolved if not p.exists()]
        if missing:
            pytest.fail(f'missing integrations dashboard targets: {missing}')
        return resolved

    auto = _dashboard_files(integrations_repo_path)
    if not auto:
        pytest.fail('no dashboard files found in integrations fixture checkout')
    return auto[:_MAX_AUTO_TARGETS]


@pytest.mark.integrations
def test_integrations_decompile_produces_valid_dashboard_shape(integrations_target_files: list[Path]) -> None:
    """Decompile selected integrations dashboards and assert stable structural invariants."""
    tested = 0
    for source in integrations_target_files:
        for dashboard in _iter_dashboard_objects(source):
            tested += 1
            result = decompile_dashboard(dashboard)
            dashboards = cast('list[dict[str, Any]]', result.get('dashboards', []))
            assert len(dashboards) == 1
            decompiled = dashboards[0]
            assert isinstance(decompiled.get('name'), str)
            assert isinstance(decompiled.get('panels'), list)
            for panel in cast('list[dict[str, Any]]', decompiled.get('panels', [])):
                keys = _panel_keys(panel)
                assert len(keys) == 1
            break
    assert tested > 0


@pytest.mark.integrations
def test_integrations_decompile_output_is_compiler_loadable(integrations_target_files: list[Path]) -> None:
    """Ensure decompiled YAML model output still loads and renders via core compiler."""
    checked = 0
    for source in integrations_target_files[:4]:
        for dashboard in _iter_dashboard_objects(source):
            checked += 1
            decompiled = decompile_dashboard(dashboard)
            dashboard_config = DashboardConfig.model_validate(decompiled)
            rendered, _ = render(load(dashboard_config))
            assert len(rendered) > 0
            break
    assert checked > 0
