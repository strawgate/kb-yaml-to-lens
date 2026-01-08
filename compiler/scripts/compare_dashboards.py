#!/usr/bin/env python3
"""Compare disassembled dashboard panels for round-trip validation.

This script compares panels from two disassembled dashboards (original and compiled)
to verify that the YAML conversion preserves the structure and content.

Usage:
    python3 scripts/compare_dashboards.py /path/to/original_disassembled /path/to/compiled_disassembled
"""

import json
import sys
from pathlib import Path


def get_panel_info(dir_path: Path) -> list[tuple[str, str, str]]:
    """Extract panel information from a disassembled dashboard directory.

    Args:
        dir_path: Path to the disassembled dashboard directory

    Returns:
        List of tuples containing (filename, panel_type, panel_title)
    """
    panels = []
    panels_dir = dir_path / 'panels'

    if not panels_dir.exists():
        print(f'Error: Panels directory not found at {panels_dir}', file=sys.stderr)
        return panels

    for fname in sorted(panels_dir.iterdir()):
        if not fname.is_file():
            continue

        try:
            with fname.open() as f:
                panel = json.load(f)
                ptype = panel.get('type', 'unknown')
                title = panel.get('title', panel.get('panelConfig', {}).get('title', '(no title)'))
                panels.append((fname.name, ptype, title))
        except (json.JSONDecodeError, OSError) as e:
            print(f'Warning: Could not read {fname}: {e}', file=sys.stderr)

    return panels


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

    orig = get_panel_info(original_dir)
    comp = get_panel_info(compiled_dir)

    print(f'Original panels: {len(orig)}')
    print(f'Compiled panels: {len(comp)}')
    print()

    if len(orig) != len(comp):
        print(f'⚠️  Panel count mismatch: {len(orig)} original vs {len(comp)} compiled')
        print()

    print('Panel comparison:')
    max_panels = max(len(orig), len(comp))

    for i in range(max_panels):
        if i < len(orig) and i < len(comp):
            _of, ot, otitle = orig[i]
            _cf, ct, ctitle = comp[i]
            match = '✓' if ot == ct else '✗'
            print(f'  {match} Panel {i}: {ot:15s} | {otitle}')
            if ot != ct:
                print(f'      Original: {ot}, Compiled: {ct}')
        elif i < len(orig):
            _of, ot, otitle = orig[i]
            print(f'  ✗ Panel {i}: {ot:15s} | {otitle} (MISSING in compiled)')
        else:
            _cf, ct, ctitle = comp[i]
            print(f'  ✗ Panel {i}: {ct:15s} | {ctitle} (EXTRA in compiled)')

    # Summary
    print()
    matches = sum(1 for i in range(min(len(orig), len(comp))) if orig[i][1] == comp[i][1])
    if len(orig) == len(comp) and matches == len(orig):
        print('✅ All panels match!')
    else:
        print(f'⚠️  {matches}/{max_panels} panels match')


if __name__ == '__main__':
    main()
