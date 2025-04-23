import pytest


SAMPLE_GRID_DATA = {"x": 0, "y": 0, "w": 24, "h": 15}
SAMPLE_GRID_YAML = """
grid:
  x: 0
  y: 0
  w: 24
  h: 15
"""


@pytest.fixture
def sample_grid_data():
    return SAMPLE_GRID_DATA


@pytest.fixture
def sample_grid_yaml():
    return """
grid:
  x: 0
  y: 0
  w: 24
  h: 15
"""
