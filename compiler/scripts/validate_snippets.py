#!/usr/bin/env python3
"""Validate ES|QL snippets from VS Code extension against Pydantic schemas.

This script:
1. Reads the snippets JSON file
2. Extracts all ES|QL-related snippets
3. Converts each snippet body to a YAML dashboard structure
4. Validates using the Dashboard Pydantic models
5. Reports validation errors with specific details
"""
# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dashboard_compiler.loader import DashboardConfig


def convert_snippet_to_yaml(snippet_body: list[str]) -> str:
    """Convert VS Code snippet body to YAML string.

    Args:
        snippet_body: List of strings from the snippet body

    Returns:
        Complete YAML string ready for parsing
    """
    # Join the lines and remove VS Code snippet placeholders
    yaml_text = '\n'.join(snippet_body)

    # Remove VS Code snippet placeholders like ${1:text} and ${1|choice1,choice2|}
    import re

    # Process placeholders iteratively to handle nested cases
    max_iterations = 10
    for _ in range(max_iterations):
        # Remove choice placeholders: ${1|choice1,choice2|} -> choice1
        new_text = re.sub(r'\$\{(\d+)\|([^|,}]+)[^}]*\}', r'\2', yaml_text)
        # Remove simple placeholders: ${1:text} -> text (non-greedy)
        new_text = re.sub(r'\$\{(\d+):([^}]+?)\}', r'\2', new_text)
        # Remove empty placeholders: ${0} or ${1} -> ''
        new_text = re.sub(r'\$\{\d+\}', '', new_text)
        # Remove remaining placeholder syntax: $number -> ''
        new_text = re.sub(r'\$\d+', '', new_text)

        # If no change, we're done
        if new_text == yaml_text:
            break
        yaml_text = new_text

    # Also handle lines that start with ${number: which might span multiple lines
    # Just remove the optional field prefix patterns like "${2:description: ${3:...}}"
    # by stripping the ${number: prefix
    yaml_text = re.sub(r'\$\{\d+:', '', yaml_text)
    # Remove trailing }
    return re.sub(r'\}(?=\s*$)', '', yaml_text, flags=re.MULTILINE)


def create_dashboard_wrapper(panel_yaml: str) -> str:
    """Wrap a panel snippet in a minimal dashboard structure.

    Args:
        panel_yaml: YAML for a single panel

    Returns:
        Complete dashboard YAML
    """
    # Check if this is already a dashboard or a panel/control
    if panel_yaml.strip().startswith('---'):
        # Already has document separator
        return panel_yaml

    # Panel yaml is already indented, just add the dashboard wrapper
    # Don't add extra indentation
    lines = panel_yaml.strip().split('\n')
    # First line should start with '- ' (list item)
    # Subsequent lines are already indented
    indented_panel = '\n'.join('    ' + line for line in lines)

    # Wrap panel in dashboard structure
    return f"""---
dashboards:
  - name: 'Snippet Test Dashboard'
    description: Test dashboard for snippet validation
    panels:
{indented_panel}
"""


def create_dashboard_with_control(control_yaml: str) -> str:
    """Wrap a control snippet in a minimal dashboard structure.

    Args:
        control_yaml: YAML for a single control

    Returns:
        Complete dashboard YAML with control
    """
    # Control yaml is already indented, just add the dashboard wrapper
    lines = control_yaml.strip().split('\n')
    indented_control = '\n'.join('      ' + line for line in lines)

    return f"""---
dashboards:
  - name: 'Snippet Test Dashboard'
    description: Test dashboard for snippet validation
    controls:
{indented_control}
    panels:
      - title: Test Panel
        size:
          w: whole
          h: 8
        markdown:
          content: Test content
"""


def validate_snippet(snippet_body: list[str], *, is_control: bool = False) -> tuple[bool, str, str]:
    """Validate a single snippet against the Pydantic schema.

    Args:
        snippet_body: VS Code snippet body (list of lines)
        is_control: Whether this is a control snippet (vs a panel snippet)

    Returns:
        Tuple of (success: bool, message: str, yaml_text: str)
    """
    try:
        # Convert snippet to YAML
        yaml_text = convert_snippet_to_yaml(snippet_body)

        # Wrap in dashboard structure
        dashboard_yaml = create_dashboard_with_control(yaml_text) if is_control else create_dashboard_wrapper(yaml_text)

        # Parse YAML
        try:
            yaml_data = yaml.safe_load(dashboard_yaml)
        except yaml.YAMLError as e:
            return False, f'YAML parsing error: {e}', dashboard_yaml

        # Validate with Pydantic
        try:
            _ = DashboardConfig.model_validate(yaml_data)
        except ValidationError as e:
            # Format the validation error nicely
            error_messages = []
            for error in e.errors():
                loc = ' -> '.join(str(x) for x in error['loc'])
                msg = error['msg']
                input_val = error.get('input')
                if input_val is not None and isinstance(input_val, dict) and len(input_val) > 0:
                    # Show the actual input value for context
                    error_messages.append(f'  • {loc}: {msg}\n    Input: {input_val}')
                else:
                    error_messages.append(f'  • {loc}: {msg}')

            error_text = '\n'.join(error_messages)
            return False, f'Validation error:\n{error_text}', dashboard_yaml
        else:
            return True, '✓ Valid', dashboard_yaml

    except Exception as e:
        return False, f'Unexpected error: {e}', ''


def main() -> int:  # noqa: PLR0915 - script with many print statements
    """Run ES|QL snippet validation and report results.

    Returns:
        Exit code (0 for success, 1 for validation errors)
    """
    # Path to snippets file
    repo_root = Path(__file__).parent.parent.parent
    snippets_file = repo_root / 'vscode-extension' / 'snippets' / 'dashboards.json'

    if not snippets_file.exists():
        print(f'Error: Snippets file not found at {snippets_file}')
        return 1

    # Load snippets
    with snippets_file.open() as f:
        snippets = json.load(f)

    # Define ES|QL snippets to validate
    esql_panel_snippets = [
        'ESQL Metric Panel',
        'ESQL Line Chart',
        'ESQL Bar Chart',
        'ESQL Datatable',
        'ESQL Tagcloud Panel',
        'ESQL Heatmap Panel',
        'ESQL XY Chart with Appearance',
    ]

    esql_control_snippets = [
        'Control - ESQL Static Values',
        'Control - ESQL Query',
    ]

    print('=' * 80)
    print('ES|QL Snippet Validation Report')
    print('=' * 80)
    print()

    all_valid = True
    results: dict[str, dict[str, Any]] = {
        'panels': {},
        'controls': {},
    }

    # Validate panel snippets
    print('Validating Panel Snippets:')
    print('-' * 80)
    for snippet_name in esql_panel_snippets:
        if snippet_name not in snippets:
            print(f'\n⚠ {snippet_name}: NOT FOUND in snippets file')
            all_valid = False
            continue

        snippet = snippets[snippet_name]
        success, message, yaml_text = validate_snippet(snippet['body'], is_control=False)
        results['panels'][snippet_name] = {'success': success, 'message': message, 'yaml': yaml_text}

        status_icon = '✓' if success else '✗'
        print(f'\n{status_icon} {snippet_name}:')
        print(f'  {message}')

        if not success:
            all_valid = False
            # Print a snippet of the panel YAML (not the full dashboard wrapper)
            panel_yaml = convert_snippet_to_yaml(snippet['body'])
            panel_lines = panel_yaml.split('\n')
            preview_lines = 15
            print(f'\n  Panel YAML (first {preview_lines} lines):')
            for i, line in enumerate(panel_lines[:preview_lines], 1):
                print(f'    {i:2}: {line}')
            if len(panel_lines) > preview_lines:
                print(f'    ... ({len(panel_lines) - preview_lines} more lines)')

    # Validate control snippets
    print('\n')
    print('Validating Control Snippets:')
    print('-' * 80)
    for snippet_name in esql_control_snippets:
        if snippet_name not in snippets:
            print(f'\n⚠ {snippet_name}: NOT FOUND in snippets file')
            all_valid = False
            continue

        snippet = snippets[snippet_name]
        success, message, yaml_text = validate_snippet(snippet['body'], is_control=True)
        results['controls'][snippet_name] = {'success': success, 'message': message, 'yaml': yaml_text}

        status_icon = '✓' if success else '✗'
        print(f'\n{status_icon} {snippet_name}:')
        print(f'  {message}')

        if not success:
            all_valid = False
            # Print control YAML
            control_yaml = convert_snippet_to_yaml(snippet['body'])
            print('\n  Control YAML:')
            for i, line in enumerate(control_yaml.split('\n'), 1):
                print(f'    {i:2}: {line}')

    # Summary
    print('\n')
    print('=' * 80)
    print('Summary:')
    print('=' * 80)

    total_panels = len(esql_panel_snippets)
    valid_panels = sum(1 for r in results['panels'].values() if r['success'])
    total_controls = len(esql_control_snippets)
    valid_controls = sum(1 for r in results['controls'].values() if r['success'])

    print(f'Panels: {valid_panels}/{total_panels} valid')
    print(f'Controls: {valid_controls}/{total_controls} valid')
    print()

    if all_valid:
        print('✓ All ES|QL snippets are valid!')
        return 0
    print('✗ Some ES|QL snippets have validation errors.')
    print()
    print('=' * 80)
    print('Detailed Issue Analysis:')
    print('=' * 80)
    print()

    # Analyze common issues
    print('Issue #1: INCORRECT QUERY STRUCTURE')
    print('-' * 80)
    print('Affected snippets:')
    print('  - ESQL Metric Panel')
    print('  - ESQL Line Chart')
    print('  - ESQL Bar Chart')
    print('  - ESQL Datatable')
    print()
    print('Problem:')
    print('  Snippets use nested structure:')
    print('    query:')
    print('      esql: |')
    print('        FROM logs-*')
    print()
    print('  But schema requires flat structure:')
    print('    query: |')
    print('      FROM logs-*')
    print()
    print("  OR using the 'root' key (for lists):")
    print('    query:')
    print('      root: FROM logs-*')
    print()
    print('  The ESQLQuery model (ESQLQueryTypes) expects either:')
    print('    - A string directly (query: "...")')
    print("    - A dict with 'root' key (query: { root: \"...\" })")
    print()
    print("Fix: Remove the nested 'esql:' key, use 'query: |' directly")
    print()

    print('Issue #2: MISSING REQUIRED FIELDS')
    print('-' * 80)
    print('Affected snippets:')
    print("  - ESQL Metric Panel (missing 'primary' field)")
    print("  - ESQL Line Chart (missing 'metrics' field)")
    print("  - ESQL Bar Chart (missing 'metrics' field)")
    print()
    print('Problem:')
    print('  These chart types require specific configuration fields that define')
    print('  which columns from the ES|QL query result should be used.')
    print()
    print("  For metric panels: 'primary' field is required")
    print("  For XY charts (line/bar): 'metrics' field is required")
    print()
    print('Fix: Add the required fields to map query result columns to chart elements')
    print()

    print('Issue #3: EXTRA/INVALID FIELDS')
    print('-' * 80)
    print('Affected snippets:')
    print('  - ESQL XY Chart with Appearance')
    print()
    print('Problem:')
    print("  The snippet includes 'dimensions' and 'series' fields that are not")
    print('  permitted in the ES|QL chart configuration.')
    print()
    print("  - 'dimensions' field: Extra inputs are not permitted")
    print("  - 'appearance.series' field: Extra inputs are not permitted")
    print()
    print('Fix: Remove these unsupported fields or verify they should be at a different')
    print('      location in the config structure')
    print()

    return 1


if __name__ == '__main__':
    sys.exit(main())
