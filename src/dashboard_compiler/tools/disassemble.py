#!/usr/bin/env python3
"""Disassemble a Kibana dashboard JSON into component parts.

This tool reads a Kibana dashboard JSON file (in NDJSON format) and breaks it
down into separate files for easier processing by LLMs. This allows for
incremental conversion of large dashboards to YAML format instead of requiring
one-shot conversion of the entire dashboard.

The dashboard is split into:
- metadata.json: Dashboard metadata (id, title, description, version, timestamps)
- options.json: Dashboard display options (margins, color sync, etc.)
- controls.json: Dashboard control group configuration
- filters.json: Dashboard-level filters
- references.json: Data view and index pattern references
- panels/: Directory containing individual panel JSON files
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_ndjson(content: str) -> dict[str, Any]:
    """Parse NDJSON content and extract the dashboard object.

    Args:
        content: NDJSON content (newline-delimited JSON objects)

    Returns:
        The dashboard object (should be the first object with type='dashboard')

    Raises:
        ValueError: If no dashboard object is found
    """
    lines = content.strip().split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue
        obj = json.loads(line)
        if obj.get('type') == 'dashboard':
            return obj

    msg = 'No dashboard object found in NDJSON file'
    raise ValueError(msg)


def _write_json_file(file_path: Path, data: Any) -> None:
    """Write data to a JSON file.

    Args:
        file_path: Path to write the JSON file
        data: Data to write
    """
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def _parse_json_field(field: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a JSON field that may be a string, dict, list, or None.

    Args:
        field: The field to parse (may be string, dict, list, or None)

    Returns:
        Parsed dict/list or None
    """
    if field is None:
        return None
    if isinstance(field, str):
        return json.loads(field)
    return field


def disassemble_dashboard(dashboard: dict[str, Any], output_dir: Path) -> None:
    """Disassemble a dashboard into component parts.

    Args:
        dashboard: The dashboard object to disassemble
        output_dir: Directory where component files will be written
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    attributes = dashboard.get('attributes', {})

    metadata = {
        'id': dashboard.get('id'),
        'type': dashboard.get('type'),
        'version': dashboard.get('version'),
        'coreMigrationVersion': dashboard.get('coreMigrationVersion'),
        'typeMigrationVersion': dashboard.get('typeMigrationVersion'),
        'managed': dashboard.get('managed'),
        'created_at': dashboard.get('created_at'),
        'created_by': dashboard.get('created_by'),
        'updated_at': dashboard.get('updated_at'),
        'updated_by': dashboard.get('updated_by'),
        'title': attributes.get('title'),
        'description': attributes.get('description'),
    }
    _write_json_file(output_dir / 'metadata.json', metadata)

    options = _parse_json_field(attributes.get('optionsJSON'))
    if options is not None:
        _write_json_file(output_dir / 'options.json', options)

    control_group_input = attributes.get('controlGroupInput')
    if control_group_input is not None:
        _write_json_file(output_dir / 'controls.json', control_group_input)

    kbn_saved_object_meta = attributes.get('kibanaSavedObjectMeta', {})
    search_source = _parse_json_field(kbn_saved_object_meta.get('searchSourceJSON'))
    if search_source is not None and isinstance(search_source, dict):
        filters = search_source.get('filter', [])
        if len(filters) > 0:
            _write_json_file(output_dir / 'filters.json', filters)

    references = dashboard.get('references', [])
    if len(references) > 0:
        _write_json_file(output_dir / 'references.json', references)

    panels = _parse_json_field(attributes.get('panelsJSON'))
    if panels is not None and isinstance(panels, list) and len(panels) > 0:
        panels_dir = output_dir / 'panels'
        panels_dir.mkdir(exist_ok=True)

        for i, panel in enumerate(panels):
            if not isinstance(panel, dict):
                continue
            panel_id = panel.get('panelIndex', f'panel_{i}')
            panel_type = panel.get('type', 'unknown')
            filename = f'{i:03d}_{panel_id}_{panel_type}.json'
            _write_json_file(panels_dir / filename, panel)


def main() -> int:
    """Run the dashboard disassembly tool.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description='Disassemble a Kibana dashboard JSON into component parts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Disassemble a dashboard NDJSON file
  python -m dashboard_compiler.tools.disassemble dashboard.ndjson -o output_dir

  # Read from stdin
  cat dashboard.ndjson | python -m dashboard_compiler.tools.disassemble -o output_dir
        """,
    )

    _ = parser.add_argument(
        'input',
        nargs='?',
        help='Path to the dashboard NDJSON file (use - or omit for stdin)',
    )
    _ = parser.add_argument(
        '-o',
        '--output',
        required=True,
        help='Output directory for component files',
    )

    args = parser.parse_args()

    try:
        if args.input is None or args.input == '-':
            content = sys.stdin.read()
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f'Error: Input file not found: {input_path}', file=sys.stderr)
                return 1
            content = input_path.read_text(encoding='utf-8')

        dashboard = parse_ndjson(content)
        output_dir = Path(args.output)
        disassemble_dashboard(dashboard, output_dir)

        print(f'Dashboard disassembled successfully to: {output_dir}')
        print('  - metadata.json: Dashboard metadata')

        if (output_dir / 'options.json').exists():
            print('  - options.json: Dashboard options')

        if (output_dir / 'controls.json').exists():
            print('  - controls.json: Control group configuration')

        if (output_dir / 'filters.json').exists():
            print('  - filters.json: Dashboard-level filters')

        if (output_dir / 'references.json').exists():
            print('  - references.json: Data view references')

        panels_dir = output_dir / 'panels'
        if panels_dir.exists():
            panel_count = len(list(panels_dir.glob('*.json')))
            print(f'  - panels/: {panel_count} panel files')

    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
