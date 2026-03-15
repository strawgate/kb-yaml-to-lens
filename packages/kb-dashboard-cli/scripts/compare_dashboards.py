#!/usr/bin/env python3
"""Compare disassembled dashboard panels for round-trip validation.

This script compares panels from two disassembled dashboards (original and compiled)
to verify that the YAML conversion preserves the structure and content.

Usage:
    python3 scripts/compare_dashboards.py /path/to/original_disassembled /path/to/compiled_disassembled
"""

import json
import os
import sys
from pathlib import Path

from kb_dashboard_tools.compare import compare_disassembled_dashboards  # pyright: ignore[reportMissingTypeStubs]

# Use ASCII fallbacks on Windows to avoid encoding errors with cp1252
_USE_ASCII = sys.platform == 'win32' and os.environ.get('PYTHONUTF8') != '1'

_ICON_CHECK = '[OK]' if _USE_ASCII else '✓'
_ICON_CROSS = '[X]' if _USE_ASCII else '✗'
_ICON_WARNING = '[!]' if _USE_ASCII else '⚠'
_ICON_SUCCESS = '[OK]' if _USE_ASCII else '✅'


REQUIRED_ARGS = 3


def main() -> None:
    """Compare two disassembled dashboards and report differences."""
    if len(sys.argv) != REQUIRED_ARGS:
        print(__doc__)
        sys.exit(1)

    original_dir = Path(sys.argv[1])
    compiled_dir = Path(sys.argv[2])

    if not original_dir.exists():
        print(f'Error: Original directory not found: {original_dir}', file=sys.stderr)
        sys.exit(1)

    if not compiled_dir.exists():
        print(f'Error: Compiled directory not found: {compiled_dir}', file=sys.stderr)
        sys.exit(1)

    try:
        comparison = compare_disassembled_dashboards(original_dir, compiled_dir)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    print(f'Original panels: {comparison.original_count}')
    print(f'Compiled panels: {comparison.compiled_count}')
    print()

    if comparison.original_count != comparison.compiled_count:
        print(f'{_ICON_WARNING}  Panel count mismatch: {comparison.original_count} original vs {comparison.compiled_count} compiled')
        print()

    print('Panel comparison:')
    for panel in comparison.panels:
        if panel.original is not None and panel.compiled is not None:
            match = _ICON_CHECK if panel.types_match else _ICON_CROSS
            print(f'  {match} Panel {panel.index}: {panel.original.panel_type:15s} | {panel.original.title}')
            if not panel.types_match:
                print(f'      Original: {panel.original.panel_type}, Compiled: {panel.compiled.panel_type}')
        elif panel.original is not None:
            print(f'  {_ICON_CROSS} Panel {panel.index}: {panel.original.panel_type:15s} | {panel.original.title} (MISSING in compiled)')
        elif panel.compiled is not None:
            print(f'  {_ICON_CROSS} Panel {panel.index}: {panel.compiled.panel_type:15s} | {panel.compiled.title} (EXTRA in compiled)')

    # Summary
    print()
    total = max(comparison.original_count, comparison.compiled_count)
    if comparison.all_panels_match:
        print(f'{_ICON_SUCCESS} All panels match!')
    else:
        print(f'{_ICON_WARNING}  {comparison.matching_panel_types}/{total} panels match')


if __name__ == '__main__':
    main()
