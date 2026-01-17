"""Fixture utilities for loading and comparing against external Kibana JSON fixtures.

This module provides utilities for:
- Discovering fixture JSON files from the submodule directory
- Loading and parsing fixture JSON into Python dicts
- Extracting visualization/panel configuration from Kibana saved object structure

Fixture Repository:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - output/v8.19.9/ - Kibana 8.19.9 visualizations
    - output/v9.2.2/ - Kibana 9.2.2 visualizations
"""

import json
from pathlib import Path
from typing import Any

# Path to the external fixtures submodule
FIXTURES_DIR = Path(__file__).parent / 'external' / 'output'

# Supported Kibana versions
SUPPORTED_VERSIONS = ['v8.19.9', 'v9.2.2']


def get_fixtures_path(version: str = 'v8.19.9') -> Path:
    """Get the path to fixtures for a specific Kibana version.

    Args:
        version: Kibana version directory name (e.g., 'v8.19.9')

    Returns:
        Path to the fixtures directory for that version

    Raises:
        FileNotFoundError: If the fixtures directory doesn't exist
    """
    fixtures_path = FIXTURES_DIR / version
    if not fixtures_path.exists():
        msg = f'Fixtures directory not found: {fixtures_path}\nEnsure the submodule is initialized: git submodule update --init'
        raise FileNotFoundError(msg)
    return fixtures_path


def list_fixtures(version: str = 'v8.19.9', chart_type: str | None = None) -> list[Path]:
    """List all fixture JSON files for a Kibana version.

    Args:
        version: Kibana version directory name (e.g., 'v8.19.9')
        chart_type: Optional filter for chart type (e.g., 'metric', 'pie', 'xy-chart')

    Returns:
        List of Path objects to fixture JSON files
    """
    fixtures_path = get_fixtures_path(version)
    fixtures = sorted(fixtures_path.glob('*.json'))
    if chart_type is not None:
        fixtures = [f for f in fixtures if f.stem.startswith(chart_type)]
    return fixtures


def load_fixture(fixture_path: Path) -> dict[str, Any]:
    """Load a fixture JSON file.

    Args:
        fixture_path: Path to the fixture JSON file

    Returns:
        Parsed JSON as a dictionary
    """
    with fixture_path.open() as f:
        return json.load(f)


def load_fixture_by_name(name: str, version: str = 'v8.19.9') -> dict[str, Any]:
    """Load a fixture by name.

    Args:
        name: Fixture name (without .json extension)
        version: Kibana version directory name

    Returns:
        Parsed JSON as a dictionary
    """
    fixture_path = get_fixtures_path(version) / f'{name}.json'
    return load_fixture(fixture_path)


def extract_visualization_state(fixture: dict[str, Any]) -> dict[str, Any]:
    """Extract the visualization state from a Kibana fixture.

    The fixture format is:
    {
        "title": "...",
        "visualizationType": "lnsMetric",
        "references": [...],
        "state": {
            "datasourceStates": {...},
            "visualization": {...},  # <-- This is what we want
            ...
        }
    }

    Args:
        fixture: Loaded fixture dictionary

    Returns:
        The visualization state dictionary
    """
    return fixture.get('state', {}).get('visualization', {})


def extract_datasource_state(fixture: dict[str, Any]) -> dict[str, Any]:
    """Extract the datasource state from a Kibana fixture.

    Args:
        fixture: Loaded fixture dictionary

    Returns:
        The datasource states dictionary (contains 'textBased' for ES|QL or 'formBased' for data view)
    """
    return fixture.get('state', {}).get('datasourceStates', {})


def get_fixture_visualization_type(fixture: dict[str, Any]) -> str:
    """Get the visualization type from a fixture.

    Args:
        fixture: Loaded fixture dictionary

    Returns:
        The visualization type (e.g., 'lnsMetric', 'lnsPie', 'lnsXY')
    """
    return fixture.get('visualizationType', '')


def get_fixture_title(fixture: dict[str, Any]) -> str:
    """Get the title from a fixture.

    Args:
        fixture: Loaded fixture dictionary

    Returns:
        The fixture title
    """
    return fixture.get('title', '')
