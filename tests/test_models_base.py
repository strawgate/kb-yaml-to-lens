import yaml
from dashboard_compiler.models.panels import Grid

# Sample data extracted from samples/simple/markdown-only.json panelsJSON[0].gridData
SAMPLE_GRID_DATA = {
    "x": 0,
    "y": 0,
    "w": 24,
    "h": 15,
    "i": "780e08fc-1a39-401b-849f-703b951bc243",
}

SAMPLE_GRID_YAML = yaml.safe_load("""
---
grid:
    x: 0
    y: 0
    w: 24
    h: 15
""")


def test_grid_model_instantiation_as_yaml():
    """Tests successful instantiation of the Grid model."""
    grid = Grid.model_validate(SAMPLE_GRID_YAML["grid"])

    assert grid.x == 0
    assert grid.y == 0
    assert grid.w == 24
    assert grid.h == 15

    # In this case we should not have a grid index as the grid index relies on the panel index
    assert grid.i is None


def test_grid_model_instantiation_as_code():
    """Tests successful instantiation of the Grid model."""
    grid = Grid(**SAMPLE_GRID_DATA)
    assert grid.x == 0
    assert grid.y == 0
    assert grid.w == 24
    assert grid.h == 15
    # Ensure extra fields ('i') are ignored without error
    assert grid.i == "780e08fc-1a39-401b-849f-703b951bc243"


# Panel tests have been moved to tests/test_models_panels.py
