"""Opt-in integrations-backed decompiler tests."""

import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from inline_snapshot import snapshot
from ruamel.yaml import YAML

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


def _decompile_yaml_text(dashboard: dict[str, Any]) -> str:
    # Snapshot canonical YAML content only (strip ruamel comments/TODO JSON blobs).
    canonical = json.loads(json.dumps(decompile_dashboard(dashboard)))
    yaml = YAML(typ='safe')
    yaml_any = cast('Any', yaml)
    yaml_any.sort_base_mapping_type_on_output = False
    stream = io.StringIO()
    yaml.dump(canonical, stream)
    return stream.getvalue()


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
def test_integrations_decompile_yaml_inline_snapshots(integrations_target_files: list[Path]) -> None:
    """Inline-snapshot generated YAML for selected integrations dashboards."""
    actual_outputs: list[dict[str, str]] = []
    for source in integrations_target_files:
        first_dashboard = next(_iter_dashboard_objects(source), None)
        if first_dashboard is None:
            continue
        actual_outputs.append(
            {
                'source': source.as_posix(),
                'yaml': _decompile_yaml_text(first_dashboard),
            }
        )
    assert actual_outputs == snapshot([])
