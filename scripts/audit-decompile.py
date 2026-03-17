#!/usr/bin/env python3
"""Fuzz the decompiler against all JSON dashboards in a directory tree.

Finds every *.json file under the given path matching the Kibana dashboard
layout (packages/*/kibana/dashboard/*.json), runs decompile_dashboard() on
each, and writes grouped error reports.

Usage:
    python scripts/audit-decompile.py /path/to/integrations
    python scripts/audit-decompile.py /path/to/integrations --output-dir .audit/decompile
"""

import csv
import json
import traceback
from collections import defaultdict
from pathlib import Path

import click

from kb_dashboard_tools.decompile import decompile_dashboard


@click.command()
@click.argument('integrations_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(path_type=Path),
    default='.audit/decompile',
    help='Directory for audit artifacts.',
)
def audit_decompile(integrations_dir: Path, output_dir: Path) -> None:
    """Fuzz the decompiler against JSON dashboards in INTEGRATIONS_DIR."""
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(integrations_dir.glob('packages/*/kibana/dashboard/*.json'))

    if not json_files:
        raise click.ClickException(
            f'discovered 0 JSON dashboard files under {integrations_dir} — check the path'
        )

    successes = 0
    failures = 0
    error_rows: list[dict[str, str]] = []
    error_groups: dict[str, dict] = defaultdict(
        lambda: {'count': 0, 'message': '', 'example_files': []}
    )
    full_tracebacks: list[str] = []

    for json_file in json_files:
        rel = json_file.relative_to(integrations_dir).as_posix()
        try:
            dashboard = json.loads(json_file.read_text(encoding='utf-8'))
            decompile_dashboard(dashboard)
            successes += 1
        except Exception as exc:
            failures += 1
            etype = type(exc).__name__
            emsg = str(exc)
            group_key = f'{etype}: {emsg[:200]}'
            error_rows.append({'file': rel, 'error_type': etype, 'error_message': emsg})
            g = error_groups[group_key]
            g['count'] += 1
            if not g['message']:
                g['message'] = emsg
            if len(g['example_files']) < 5:
                g['example_files'].append(rel)
            full_tracebacks.append(f'\n=== {rel} ===\n{traceback.format_exc()}')

    total = len(json_files)
    rate = f'{successes * 100 // total}%' if total else 'n/a'
    summary = {
        'total': total,
        'successes': successes,
        'failures': failures,
        'success_rate': rate,
        'unique_error_types': len(error_groups),
    }
    (output_dir / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

    sorted_groups = dict(sorted(error_groups.items(), key=lambda x: x[1]['count'], reverse=True))
    (output_dir / 'errors_by_type.json').write_text(
        json.dumps(sorted_groups, indent=2), encoding='utf-8'
    )

    with (output_dir / 'failures.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'error_type', 'error_message'])
        writer.writeheader()
        writer.writerows(error_rows)

    (output_dir / 'errors.log').write_text(
        '\n'.join(full_tracebacks).strip() + '\n' if full_tracebacks else '', encoding='utf-8'
    )

    click.echo(json.dumps(summary, indent=2))


if __name__ == '__main__':
    audit_decompile()
