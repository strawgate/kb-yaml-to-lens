"""Test grid positioning validation."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.config import Grid


def test_grid_valid_position() -> None:
    """Test that valid grid positions are accepted."""
    grid = Grid(x=0, y=0, w=24, h=15)
    assert grid.x == 0
    assert grid.y == 0
    assert grid.w == 24
    assert grid.h == 15


def test_grid_negative_x() -> None:
    """Test that negative x coordinate raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=-1, y=0, w=24, h=15)
    assert 'Input should be greater than or equal to 0' in str(exc_info.value)


def test_grid_negative_y() -> None:
    """Test that negative y coordinate raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=0, y=-5, w=24, h=15)
    assert 'Input should be greater than or equal to 0' in str(exc_info.value)


def test_grid_zero_width() -> None:
    """Test that zero width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=0, y=0, w=0, h=15)
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_negative_width() -> None:
    """Test that negative width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=0, y=0, w=-10, h=15)
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_zero_height() -> None:
    """Test that zero height raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=0, y=0, w=24, h=0)
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_negative_height() -> None:
    """Test that negative height raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=0, y=0, w=24, h=-3)
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_large_y_position() -> None:
    """Test that large y positions are accepted (no height restriction)."""
    grid = Grid(x=0, y=200, w=24, h=30)
    assert grid.x == 0
    assert grid.y == 200
    assert grid.w == 24
    assert grid.h == 30


def test_grid_exceeds_kibana_width() -> None:
    """Test that panel extending beyond Kibana grid width raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid(x=30, y=0, w=24, h=15)
    error_msg = str(exc_info.value)
    assert 'Panel extends beyond standard Kibana grid width (48 units)' in error_msg
    assert 'x=30 + w=24 = 54' in error_msg


def test_grid_at_kibana_width_boundary() -> None:
    """Test that panel exactly at Kibana grid width boundary is accepted."""
    grid = Grid(x=24, y=0, w=24, h=15)
    assert grid.x == 24
    assert grid.w == 24
    assert grid.x + grid.w == 48


def test_grid_full_width() -> None:
    """Test that full-width panel (w=48) is accepted."""
    grid = Grid(x=0, y=0, w=48, h=15)
    assert grid.x == 0
    assert grid.w == 48


def test_overlaps_with_partial_overlap() -> None:
    """Test that partially overlapping grids are detected."""
    grid1 = Grid(x=0, y=0, w=20, h=10)
    grid2 = Grid(x=10, y=5, w=20, h=10)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_complete_overlap() -> None:
    """Test that completely overlapping grids are detected."""
    grid1 = Grid(x=0, y=0, w=20, h=10)
    grid2 = Grid(x=0, y=0, w=20, h=10)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_contained_grid() -> None:
    """Test that a grid contained within another is detected as overlapping."""
    grid1 = Grid(x=0, y=0, w=30, h=20)
    grid2 = Grid(x=5, y=5, w=10, h=8)
    assert grid1.overlaps_with(grid2) is True
    assert grid2.overlaps_with(grid1) is True


def test_overlaps_with_adjacent_horizontal() -> None:
    """Test that horizontally adjacent grids (touching edges) do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=10, y=0, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_adjacent_vertical() -> None:
    """Test that vertically adjacent grids (touching edges) do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=0, y=10, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_horizontal() -> None:
    """Test that horizontally separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=20, y=0, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_vertical() -> None:
    """Test that vertically separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=0, y=20, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_overlaps_with_separated_diagonal() -> None:
    """Test that diagonally separated grids do not overlap."""
    grid1 = Grid(x=0, y=0, w=10, h=10)
    grid2 = Grid(x=20, y=20, w=10, h=10)
    assert grid1.overlaps_with(grid2) is False
    assert grid2.overlaps_with(grid1) is False


def test_grid_verbose_syntax() -> None:
    """Test that verbose parameter names work correctly."""
    grid = Grid.model_validate({'from_left': 0, 'from_top': 5, 'width': 24, 'height': 15})
    assert grid.x == 0
    assert grid.y == 5
    assert grid.w == 24
    assert grid.h == 15


def test_grid_mixed_syntax() -> None:
    """Test that mixing shorthand and verbose parameter names works."""
    grid = Grid.model_validate({'x': 10, 'from_top': 0, 'width': 20, 'h': 12})
    assert grid.x == 10
    assert grid.y == 0
    assert grid.w == 20
    assert grid.h == 12


def test_grid_verbose_negative_from_left() -> None:
    """Test that negative from_left raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid.model_validate({'from_left': -1, 'from_top': 0, 'width': 24, 'height': 15})
    assert 'Input should be greater than or equal to 0' in str(exc_info.value)


def test_grid_verbose_negative_from_top() -> None:
    """Test that negative from_top raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid.model_validate({'from_left': 0, 'from_top': -5, 'width': 24, 'height': 15})
    assert 'Input should be greater than or equal to 0' in str(exc_info.value)


def test_grid_verbose_zero_width() -> None:
    """Test that zero width raises validation error with verbose syntax."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid.model_validate({'from_left': 0, 'from_top': 0, 'width': 0, 'height': 15})
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_verbose_zero_height() -> None:
    """Test that zero height raises validation error with verbose syntax."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid.model_validate({'from_left': 0, 'from_top': 0, 'width': 24, 'height': 0})
    assert 'Input should be greater than 0' in str(exc_info.value)


def test_grid_verbose_exceeds_kibana_width() -> None:
    """Test that panel extending beyond Kibana grid width raises error with verbose syntax."""
    with pytest.raises(ValidationError) as exc_info:
        _ = Grid.model_validate({'from_left': 30, 'from_top': 0, 'width': 24, 'height': 15})
    error_msg = str(exc_info.value)
    assert 'Panel extends beyond standard Kibana grid width (48 units)' in error_msg
    assert 'x=30 + w=24 = 54' in error_msg


def test_grid_verbose_at_kibana_width_boundary() -> None:
    """Test that panel exactly at Kibana grid width boundary works with verbose syntax."""
    grid = Grid.model_validate({'from_left': 24, 'from_top': 0, 'width': 24, 'height': 15})
    assert grid.x == 24
    assert grid.w == 24
    assert grid.x + grid.w == 48


def test_grid_serialization_uses_shorthand() -> None:
    """Test that serialization uses shorthand field names, not verbose aliases."""
    grid = Grid.model_validate({'from_left': 5, 'from_top': 10, 'width': 20, 'height': 15})
    serialized = grid.model_dump()
    assert 'x' in serialized
    assert 'y' in serialized
    assert 'w' in serialized
    assert 'h' in serialized
    assert 'from_left' not in serialized
    assert 'from_top' not in serialized
    assert 'width' not in serialized
    assert 'height' not in serialized
