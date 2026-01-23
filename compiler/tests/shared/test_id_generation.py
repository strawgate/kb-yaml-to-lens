"""Unit tests for ID generation functions."""

import uuid
from pathlib import Path

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.shared.config import stable_id_generator


def test_stable_id_generator_consistency() -> None:
    """Verify that the same input produces the same output."""
    id1 = stable_id_generator(['field', 'aggregation'])
    id2 = stable_id_generator(['field', 'aggregation'])
    assert id1 == id2


def test_stable_id_generator_different_inputs() -> None:
    """Verify that different inputs produce different outputs."""
    id1 = stable_id_generator(['field', 'sum'])
    id2 = stable_id_generator(['field', 'count'])
    assert id1 != id2


def test_stable_id_generator_order_matters() -> None:
    """Verify that order of inputs affects the output."""
    id1 = stable_id_generator(['a', 'b'])
    id2 = stable_id_generator(['b', 'a'])
    assert id1 != id2


def test_stable_id_generator_uuid_format() -> None:
    """Verify that output is a valid UUID format."""
    result = stable_id_generator(['test'])
    # This will raise ValueError if the result is not a valid UUID
    _ = uuid.UUID(result)


def test_stable_id_generator_with_numbers() -> None:
    """Verify stable ID generation with numeric values."""
    id1 = stable_id_generator(['field', 100])
    id2 = stable_id_generator(['field', 100])
    id3 = stable_id_generator(['field', 200])

    assert id1 == id2
    assert id1 != id3
    # Verify it's a valid UUID
    _ = uuid.UUID(id1)


def test_stable_id_generator_with_floats() -> None:
    """Verify stable ID generation with float values."""
    id1 = stable_id_generator(['field', 95.5])
    id2 = stable_id_generator(['field', 95.5])
    id3 = stable_id_generator(['field', 95.6])

    assert id1 == id2
    assert id1 != id3
    _ = uuid.UUID(id1)


def test_stable_id_generator_with_none() -> None:
    """Verify stable ID generation with None values."""
    id1 = stable_id_generator(['field', None])
    id2 = stable_id_generator(['field', None])
    id3 = stable_id_generator(['field', 'value'])

    assert id1 == id2
    assert id1 != id3
    _ = uuid.UUID(id1)


def test_stable_id_generator_mixed_types() -> None:
    """Verify stable ID generation with mixed types."""
    id1 = stable_id_generator(['field', 'aggregation', 100, 95.5, None])
    id2 = stable_id_generator(['field', 'aggregation', 100, 95.5, None])

    assert id1 == id2
    _ = uuid.UUID(id1)


def test_stable_id_generator_empty_list() -> None:
    """Verify stable ID generation with empty list."""
    id1 = stable_id_generator([])
    id2 = stable_id_generator([])

    assert id1 == id2
    _ = uuid.UUID(id1)


# Find example files for deterministic compilation tests
_project_root = Path(__file__).parent.parent.parent.parent
_example_dir = _project_root / 'docs' / 'content' / 'examples'


def test_deterministic_compilation_controls_example() -> None:
    """Verify dashboard with controls compiles deterministically."""
    example_path = _example_dir / 'controls-example.yaml'
    dashboards = load(str(example_path))

    # Compile each dashboard twice and compare
    for dashboard in dashboards:
        result1 = render(dashboard).model_dump(by_alias=True)
        result2 = render(dashboard).model_dump(by_alias=True)

        assert result1 == result2, 'Same dashboard should compile to identical output'


def test_deterministic_compilation_multi_panel_showcase() -> None:
    """Verify complex multi-panel dashboard compiles deterministically."""
    example_path = _example_dir / 'multi-panel-showcase.yaml'
    dashboards = load(str(example_path))

    for dashboard in dashboards:
        result1 = render(dashboard).model_dump(by_alias=True)
        result2 = render(dashboard).model_dump(by_alias=True)

        assert result1 == result2, 'Same dashboard should compile to identical output'


def test_deterministic_compilation_dimensions_example() -> None:
    """Verify dashboard with various dimension types compiles deterministically."""
    example_path = _example_dir / 'dimensions-example.yaml'
    dashboards = load(str(example_path))

    for dashboard in dashboards:
        result1 = render(dashboard).model_dump(by_alias=True)
        result2 = render(dashboard).model_dump(by_alias=True)

        assert result1 == result2, 'Same dashboard should compile to identical output'


def test_deterministic_compilation_from_dict() -> None:
    """Verify dashboard created from dict compiles deterministically."""
    dashboard_dict = {
        'name': 'Test Deterministic IDs',
        'panels': [
            {
                'title': 'Test Pie Chart',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 12},
                'lens': {
                    'type': 'pie',
                    'data_view': 'metrics-*',
                    'dimensions': [{'field': 'host.name', 'type': 'values', 'size': 5}],
                    'metrics': [{'aggregation': 'count'}],
                },
            },
            {
                'title': 'Test Line Chart',
                'position': {'x': 24, 'y': 0},
                'size': {'w': 24, 'h': 12},
                'lens': {
                    'type': 'line',
                    'data_view': 'metrics-*',
                    'dimension': {'field': '@timestamp', 'type': 'date_histogram'},
                    'metrics': [
                        {'aggregation': 'average', 'field': 'system.cpu.total.pct'},
                        {'aggregation': 'max', 'field': 'system.cpu.total.pct'},
                    ],
                },
            },
        ],
    }

    # Create dashboard twice from same dict
    dashboard1 = Dashboard(**dashboard_dict)
    dashboard2 = Dashboard(**dashboard_dict)

    result1 = render(dashboard1).model_dump(by_alias=True)
    result2 = render(dashboard2).model_dump(by_alias=True)

    assert result1 == result2, 'Dashboards from same dict should compile identically'
