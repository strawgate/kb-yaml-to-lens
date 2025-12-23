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
