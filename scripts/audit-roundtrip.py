#!/usr/bin/env python3
"""Round-trip audit: decompile JSON → YAML → compile back to JSON.

For each Kibana dashboard JSON in the integrations directory:
  1. Decompile it with kb-dashboard-tools into a YAML stub.
  2. Load that YAML stub through the kb-dashboard-core config model.
  3. Compile it back to a KbnDashboard via the kb-dashboard-core compiler.

Errors in steps 2 or 3 indicate compiler bugs (the decompiler produced
valid YAML that the compiler cannot handle).  Errors in step 1 are
decompiler bugs and are reported separately.

Panels that decompiled to TODO stubs are expected to have gaps; the
`has_todo` flag in the output lets you separate genuine compiler bugs
from known incomplete-decompile coverage.

Usage:
    python scripts/audit-roundtrip.py /path/to/integrations
    python scripts/audit-roundtrip.py /path/to/integrations --output-dir .audit/roundtrip
"""

import csv
import io
import json
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

import click
import yaml
from ruamel.yaml import YAML as RuamelYAML

from kb_dashboard_core.dashboard.compile import compile_dashboard
from kb_dashboard_core.loader import DashboardConfig
from kb_dashboard_tools.decompile import decompile_dashboard


def _iter_dashboard_objects(path: Path):  # type: ignore[return]
    """Yield raw dashboard dicts from a .json or .ndjson file."""
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.ndjson':
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if not stripped:
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


def _to_yaml_text(compiled_map: Any) -> str:
    """Convert a CommentedMap produced by decompile_dashboard to a plain YAML string."""
    canonical = json.loads(json.dumps(compiled_map))
    ry = RuamelYAML(typ='safe')
    ry_any = cast('Any', ry)
    ry_any.sort_base_mapping_type_on_output = False
    stream = io.StringIO()
    ry.dump(canonical, stream)
    return stream.getvalue()


@click.command()
@click.argument('integrations_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(path_type=Path),
    default='.audit/roundtrip',
    help='Directory for audit artifacts.',
)
def audit_roundtrip(integrations_dir: Path, output_dir: Path) -> None:
    """Round-trip audit: decompile + load + compile for each dashboard in INTEGRATIONS_DIR."""
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(integrations_dir.glob('packages/*/kibana/dashboard/*.json'))

    if not json_files:
        raise click.ClickException(
            f'discovered 0 JSON dashboard files under {integrations_dir} — check the path'
        )

    # Counters
    total_dashboards = 0
    decompile_ok = 0
    load_ok = 0
    compile_ok = 0
    decompile_failures = 0
    load_failures = 0
    compile_failures = 0

    error_rows: list[dict[str, str]] = []
    decompile_groups: dict[str, dict] = defaultdict(lambda: {'count': 0, 'message': '', 'example_files': []})
    load_groups: dict[str, dict] = defaultdict(lambda: {'count': 0, 'message': '', 'example_files': []})
    compile_groups: dict[str, dict] = defaultdict(lambda: {'count': 0, 'message': '', 'example_files': []})
    full_tracebacks: list[str] = []

    def _record_error(groups: dict, rel: str, exc: Exception, stage: str, has_todo: bool) -> None:
        etype = type(exc).__name__
        emsg = str(exc)
        group_key = f'{etype}: {emsg[:200]}'
        error_rows.append({
            'file': rel,
            'stage': stage,
            'error_type': etype,
            'error_message': emsg,
            'has_todo': str(has_todo),
        })
        g = groups[group_key]
        g['count'] += 1
        if not g['message']:
            g['message'] = emsg
        if len(g['example_files']) < 5:
            g['example_files'].append(rel)
        full_tracebacks.append(f'\n=== [{stage}] {rel} ===\n{traceback.format_exc()}')

    for json_file in json_files:
        rel = json_file.relative_to(integrations_dir).as_posix()
        for dashboard_raw in _iter_dashboard_objects(json_file):
            total_dashboards += 1

            # ── Stage 1: Decompile JSON → YAML ─────────────────────────────
            try:
                compiled_map = decompile_dashboard(dashboard_raw)
                yaml_text = _to_yaml_text(compiled_map)
                decompile_ok += 1
            except Exception as exc:
                decompile_failures += 1
                _record_error(decompile_groups, rel, exc, 'decompile', has_todo=False)
                continue

            has_todo = 'TODO' in yaml_text

            # ── Stage 2: Load YAML → Dashboard config model ─────────────────
            try:
                config_data = yaml.safe_load(yaml_text)
                config = DashboardConfig.model_validate(config_data)
                load_ok += 1
            except Exception as exc:
                load_failures += 1
                _record_error(load_groups, rel, exc, 'load', has_todo=has_todo)
                continue

            # ── Stage 3: Compile Dashboard → KbnDashboard ───────────────────
            for dashboard_model in config.dashboards:
                try:
                    compile_dashboard(dashboard_model)
                    compile_ok += 1
                except Exception as exc:
                    compile_failures += 1
                    _record_error(compile_groups, rel, exc, 'compile', has_todo=has_todo)

    # ── Write artifacts ─────────────────────────────────────────────────────
    summary = {
        'total_dashboards': total_dashboards,
        'decompile': {'ok': decompile_ok, 'failures': decompile_failures},
        'load': {'ok': load_ok, 'failures': load_failures},
        'compile': {'ok': compile_ok, 'failures': compile_failures},
        'compiler_bugs_no_todo': sum(
            1 for r in error_rows
            if r['stage'] in ('load', 'compile') and r['has_todo'] == 'False'
        ),
        'compiler_bugs_with_todo': sum(
            1 for r in error_rows
            if r['stage'] in ('load', 'compile') and r['has_todo'] == 'True'
        ),
    }
    (output_dir / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

    errors_by_stage = {
        'decompile': dict(sorted(decompile_groups.items(), key=lambda x: x[1]['count'], reverse=True)),
        'load': dict(sorted(load_groups.items(), key=lambda x: x[1]['count'], reverse=True)),
        'compile': dict(sorted(compile_groups.items(), key=lambda x: x[1]['count'], reverse=True)),
    }
    (output_dir / 'errors_by_type.json').write_text(
        json.dumps(errors_by_stage, indent=2), encoding='utf-8'
    )

    with (output_dir / 'failures.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'stage', 'error_type', 'error_message', 'has_todo'])
        writer.writeheader()
        writer.writerows(error_rows)

    (output_dir / 'errors.log').write_text(
        '\n'.join(full_tracebacks).strip() + '\n' if full_tracebacks else '', encoding='utf-8'
    )

    click.echo(json.dumps(summary, indent=2))


if __name__ == '__main__':
    audit_roundtrip()
