# pyright: reportAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
# Disassemble deals with unstructured JSON data from Kibana dashboards
"""Disassemble a Kibana dashboard JSON into components.

This module provides functionality to break down Kibana dashboard JSON files
(in NDJSON format) into separate files for easier processing by LLMs. This
enables incremental conversion of large dashboards to YAML format.

The dashboard is split into:
- metadata.json: Dashboard metadata (id, title, description, version, timestamps)
- options.json: Dashboard display options (margins, color sync, etc.)
- controls.json: Dashboard control group configuration
- filters.json: Dashboard-level filters
- references.json: Data view and index pattern references
- panels/: Directory containing individual panel JSON files
"""

import json
from pathlib import Path
from typing import Any


def parse_ndjson(content: str) -> dict[str, Any]:
    """Parse NDJSON content and extract the dashboard object.

    Args:
        content: NDJSON content (newline-delimited JSON objects)

    Returns:
        The dashboard object (first object with type='dashboard')

    Raises:
        ValueError: If no dashboard object is found
    """
    for line in content.strip().split('\n'):
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

    Raises:
        TypeError: If field is not a supported type
    """
    if field is None:
        return None
    if isinstance(field, str):
        return json.loads(field)
    if isinstance(field, (dict, list)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return field
    msg = f'Unsupported field type in _parse_json_field: {type(field).__name__}'  # pyright: ignore[reportUnreachable]
    raise TypeError(msg)


def disassemble_dashboard(dashboard: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    """Disassemble a dashboard into component parts.

    Args:
        dashboard: The dashboard object to disassemble
        output_dir: Directory where component files will be written

    Returns:
        Dictionary indicating which components were written
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    attributes = dashboard.get('attributes', {})

    # Write metadata
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

    components: dict[str, Any] = {'metadata': True}

    # Write options if present
    options = _parse_json_field(attributes.get('optionsJSON'))
    if options is not None:
        _write_json_file(output_dir / 'options.json', options)
        components['options'] = True

    # Write controls if present
    control_group_input = attributes.get('controlGroupInput')
    if control_group_input is not None:
        _write_json_file(output_dir / 'controls.json', control_group_input)
        components['controls'] = True

    # Write filters if present
    kbn_saved_object_meta = attributes.get('kibanaSavedObjectMeta', {})
    search_source = _parse_json_field(kbn_saved_object_meta.get('searchSourceJSON'))
    if search_source is not None and isinstance(search_source, dict):
        filters = search_source.get('filter', [])
        if len(filters) > 0:
            _write_json_file(output_dir / 'filters.json', filters)
            components['filters'] = True

    # Write references if present
    references = dashboard.get('references', [])
    if len(references) > 0:
        _write_json_file(output_dir / 'references.json', references)
        components['references'] = True

    # Write panels if present
    panels = _parse_json_field(attributes.get('panelsJSON'))
    if panels is not None and isinstance(panels, list) and len(panels) > 0:
        panels_dir = output_dir / 'panels'
        panels_dir.mkdir(exist_ok=True)

        panel_count = 0
        for i, panel in enumerate(panels):
            if not isinstance(panel, dict):
                continue
            panel_id = panel.get('panelIndex', f'panel_{i}')
            panel_type = panel.get('type', 'unknown')
            # Sanitize panel_id and panel_type for filesystem safety
            safe_panel_id = str(panel_id).replace('/', '_').replace('\\', '_')
            safe_panel_type = str(panel_type).replace('/', '_').replace('\\', '_')
            filename = f'{i:03d}_{safe_panel_id}_{safe_panel_type}.json'
            _write_json_file(panels_dir / filename, panel)
            panel_count += 1

        components['panels'] = panel_count

    return components
