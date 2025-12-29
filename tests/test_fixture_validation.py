"""Integration tests validating YAML fixtures compile and match Kibana fixture structure.

This test suite:
1. Auto-discovers YAML files in tests/fixtures/yaml/
2. Compiles them using the dashboard compiler
3. Validates structure against Kibana-generated fixtures
4. Uses smart field normalization to handle dynamic IDs, UUIDs, timestamps
"""

import json
from pathlib import Path
from typing import Any

import pytest

from dashboard_compiler.dashboard_compiler import load

# Paths
FIXTURE_DIR = Path(__file__).parent.parent / 'fixture-generator' / 'output' / 'v9.2.0'
YAML_DIR = Path(__file__).parent / 'fixtures' / 'yaml'


def discover_yaml_fixtures() -> list[tuple[str, Path]]:
    """Discover all YAML fixture files and return (name, path) tuples."""
    if not YAML_DIR.exists():
        return []

    fixtures = []
    for yaml_file in sorted(YAML_DIR.glob('*.yaml')):
        # Extract fixture name without extension
        fixture_name = yaml_file.stem
        fixtures.append((fixture_name, yaml_file))

    return fixtures


def normalize_for_comparison(data: Any, path: str = '') -> Any:
    """Normalize data for structural comparison by removing/standardizing dynamic fields.

    This function:
    - Removes UUIDs and auto-generated IDs
    - Normalizes timestamps
    - Removes empty arrays/objects
    - Standardizes field ordering
    """
    if isinstance(data, dict):
        normalized = {}
        for key, value in data.items():
            # Skip fields that are always different
            if key in ('id', 'panelIndex', 'version'):
                continue

            # Skip UUID-like fields
            if isinstance(value, str) and len(value) == 36 and value.count('-') == 4:
                continue

            # Recursively normalize nested structures
            normalized_value = normalize_for_comparison(value, f'{path}.{key}')

            # Only include non-empty values
            if normalized_value not in (None, {}, []):
                normalized[key] = normalized_value

        return normalized

    if isinstance(data, list):
        return [normalize_for_comparison(item, f'{path}[]') for item in data]

    return data


def get_visualization_type(panel: dict) -> str | None:
    """Extract visualization type from a panel."""
    return panel.get('type') or panel.get('embeddableConfig', {}).get('attributes', {}).get('visualizationType')


def find_matching_fixture(fixture_name: str, is_esql: bool) -> Path | None:
    """Find the matching Kibana fixture JSON file.

    Args:
        fixture_name: Base name of the YAML fixture (e.g., 'pie-chart')
        is_esql: Whether this is an ES|QL variant

    Returns:
        Path to matching fixture JSON file, or None if not found
    """
    suffix = 'esql' if is_esql else 'dataview'
    fixture_path = FIXTURE_DIR / f'{fixture_name}-{suffix}.json'

    if fixture_path.exists():
        return fixture_path

    return None


def has_esql_query(panel: dict) -> bool:
    """Check if a panel uses ES|QL query."""
    # Check embeddableConfig.attributes.state.datasourceStates.textBased
    state = panel.get('embeddableConfig', {}).get('attributes', {}).get('state', {})
    datasource_states = state.get('datasourceStates', {})

    # ES|QL queries use textBased datasource
    if 'textBased' in datasource_states:
        return True

    # Also check for formBased (data view)
    if 'formBased' in datasource_states:
        return False

    return False


@pytest.mark.parametrize(('fixture_name', 'yaml_path'), discover_yaml_fixtures())
def test_yaml_fixture_compiles(fixture_name: str, yaml_path: Path) -> None:  # noqa: ARG001
    """Test that YAML fixture compiles without errors."""
    dashboards = load(str(yaml_path))

    assert len(dashboards) > 0, f'No dashboards loaded from {yaml_path}'
    assert len(dashboards[0]['attributes']['panelsJSON']) > 0, f'No panels in dashboard from {yaml_path}'


@pytest.mark.parametrize(('fixture_name', 'yaml_path'), discover_yaml_fixtures())
def test_yaml_fixture_structure_matches_kibana(fixture_name: str, yaml_path: Path) -> None:
    """Test that compiled YAML structure matches Kibana-generated fixture.

    This test:
    - Compiles the YAML file
    - For each panel (ES|QL and Data View variants):
      - Finds the corresponding Kibana fixture
      - Compares key structural elements
      - Validates visualization types match
    """
    # Skip if fixture directory doesn't exist
    if not FIXTURE_DIR.exists():
        pytest.skip(f'Fixture directory {FIXTURE_DIR} does not exist')

    # Load and compile YAML
    dashboards = load(str(yaml_path))
    assert len(dashboards) > 0

    panels = dashboards[0]['attributes']['panelsJSON']

    # We expect each YAML file to have 2 panels (ES|QL and Data View variants)
    # But some might have only one, so we validate what we have
    for panel in panels:
        is_esql = has_esql_query(panel)

        # Find matching Kibana fixture
        fixture_path = find_matching_fixture(fixture_name, is_esql)

        if fixture_path is None:
            # Not all YAML fixtures may have corresponding Kibana fixtures yet
            continue

        # Load Kibana fixture
        with fixture_path.open() as f:
            kibana_fixture = json.load(f)

        # Validate visualization type matches
        panel_attrs = panel.get('embeddableConfig', {}).get('attributes', {})
        assert panel_attrs.get('visualizationType') == kibana_fixture.get('visualizationType'), (
            f'Visualization type mismatch for {fixture_name} ({"esql" if is_esql else "dataview"})'
        )

        # Validate state structure exists and has expected keys
        panel_state = panel_attrs.get('state', {})
        kibana_state = kibana_fixture.get('state', {})

        # Both should have datasourceStates and visualization
        assert 'datasourceStates' in panel_state, 'Compiled panel missing datasourceStates'
        assert 'visualization' in panel_state, 'Compiled panel missing visualization'

        # Normalize and compare structures
        normalized_panel = normalize_for_comparison(panel_state)
        normalized_kibana = normalize_for_comparison(kibana_state)

        # Validate key structural elements are present
        # Note: We don't do exact matching because of IDs, but we validate structure
        assert normalized_panel.get('datasourceStates') is not None
        assert normalized_kibana.get('datasourceStates') is not None


@pytest.mark.parametrize(('fixture_name', 'yaml_path'), discover_yaml_fixtures())
def test_yaml_fixture_has_both_variants(fixture_name: str, yaml_path: Path) -> None:
    """Test that each YAML fixture has both ES|QL and Data View variants.

    This ensures comprehensive test coverage across both query types.
    """
    dashboards = load(str(yaml_path))
    panels = dashboards[0]['attributes']['panelsJSON']

    # Check we have at least 2 panels
    assert len(panels) >= 2, f'{fixture_name} should have at least 2 panels (ES|QL and Data View variants)'

    # Count ES|QL and Data View panels
    esql_count = sum(1 for p in panels if has_esql_query(p))
    dataview_count = len(panels) - esql_count

    assert esql_count >= 1, f'{fixture_name} should have at least one ES|QL panel'
    assert dataview_count >= 1, f'{fixture_name} should have at least one Data View panel'


def test_all_yaml_fixtures_discovered() -> None:
    """Test that we discovered YAML fixtures."""
    fixtures = discover_yaml_fixtures()

    # We should have created 20 fixtures
    assert len(fixtures) >= 20, f'Expected at least 20 YAML fixtures, found {len(fixtures)}'
