"""Test grid positioning validation."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.config import Grid


def test_grid_valid_position():
    """Test that valid grid positions are accepted."""
    grid = Grid(x=0, y=0, w=24, h=15)
    assert grid.x == 0
    assert grid.y == 0
    assert grid.w == 24
    assert grid.h == 15


def test_grid_negative_x():
    """Test that negative x coordinate raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=-1, y=0, w=24, h=15)
    assert 'Position coordinates (x, y) must be non-negative' in str(exc_info.value)


def test_grid_negative_y():
    """Test that negative y coordinate raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=0, y=-5, w=24, h=15)
    assert 'Position coordinates (x, y) must be non-negative' in str(exc_info.value)


def test_grid_zero_width():
    """Test that zero width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=0, y=0, w=0, h=15)
    assert 'Width and height (w, h) must be positive' in str(exc_info.value)


def test_grid_negative_width():
    """Test that negative width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=0, y=0, w=-10, h=15)
    assert 'Width and height (w, h) must be positive' in str(exc_info.value)


def test_grid_zero_height():
    """Test that zero height raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=0, y=0, w=24, h=0)
    assert 'Width and height (w, h) must be positive' in str(exc_info.value)


def test_grid_negative_height():
    """Test that negative height raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=0, y=0, w=24, h=-3)
    assert 'Width and height (w, h) must be positive' in str(exc_info.value)


def test_grid_large_y_position():
    """Test that large y positions are accepted (no height restriction)."""
    grid = Grid(x=0, y=200, w=24, h=30)
    assert grid.x == 0
    assert grid.y == 200
    assert grid.w == 24
    assert grid.h == 30


def test_grid_exceeds_kibana_width():
    """Test that panel extending beyond Kibana grid width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Grid(x=30, y=0, w=24, h=15)
    error_msg = str(exc_info.value)
    assert 'Panel extends beyond standard Kibana grid width (48 units)' in error_msg
    assert 'x=30 + w=24 = 54' in error_msg


def test_grid_at_kibana_width_boundary():
    """Test that panel exactly at Kibana grid width boundary is accepted."""
    grid = Grid(x=24, y=0, w=24, h=15)
    assert grid.x == 24
    assert grid.w == 24
    assert grid.x + grid.w == 48


def test_grid_full_width():
    """Test that full-width panel (w=48) is accepted."""
    grid = Grid(x=0, y=0, w=48, h=15)
    assert grid.x == 0
    assert grid.w == 48


def test_overlaps_with_partial_overlap():
    """Test that partially overlapping grids are detected."""
    grid1 = Grid(x=0, y=0, w=20, h=10)
    grid2 = Grid(x=10, y=5, w=20, h=10)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_complete_overlap():
    """Test that completely overlapping grids are detected."""
    grid1 = Grid(x=0, y=0, w=20, h=10)
    grid2 = Grid(x=0, y=0, w=20, h=10)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_contained_grid():
    """Test that a grid contained within another is detected as overlapping."""
    grid1 = Grid(x=0, y=0, w=30, h=20)
    grid2 = Grid(x=5, y=5, w=10, h=8)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_adjacent_horizontal():
    """Test that horizontally adjacent grids (touching edges) do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=10, y=0, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_adjacent_vertical():
    """Test that vertically adjacent grids (touching edges) do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=0, y=10, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_horizontal():
    """Test that horizontally separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=20, y=0, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_vertical():
    """Test that vertically separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=0, y=20, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_diagonal():
    """Test that diagonally separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=20, y=20, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False
