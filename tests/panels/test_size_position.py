"""Test Size and Position models."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.config import Position, Size


class TestSize:
    """Test suite for Size model."""

    def test_size_default_values(self) -> None:
        """Test that Size uses default values of 24w x 12h."""
        size = Size()
        assert size.w == 24
        assert size.h == 12

    def test_size_with_explicit_values(self) -> None:
        """Test Size with explicit numeric values."""
        size = Size(w=48, h=20)
        assert size.w == 48
        assert size.h == 20

    def test_size_semantic_width_whole(self) -> None:
        """Test semantic width 'whole' resolves to 48."""
        size = Size(w='whole')
        assert size.w == 48

    def test_size_semantic_width_half(self) -> None:
        """Test semantic width 'half' resolves to 24."""
        size = Size(w='half')
        assert size.w == 24

    def test_size_semantic_width_third(self) -> None:
        """Test semantic width 'third' resolves to 16."""
        size = Size(w='third')
        assert size.w == 16

    def test_size_semantic_width_quarter(self) -> None:
        """Test semantic width 'quarter' resolves to 12."""
        size = Size(w='quarter')
        assert size.w == 12

    def test_size_semantic_width_sixth(self) -> None:
        """Test semantic width 'sixth' resolves to 8."""
        size = Size(w='sixth')
        assert size.w == 8

    def test_size_semantic_width_eighth(self) -> None:
        """Test semantic width 'eighth' resolves to 6."""
        size = Size(w='eighth')
        assert size.w == 6

    def test_size_mixed_semantic_and_numeric(self) -> None:
        """Test mixing semantic and numeric dimensions."""
        size = Size(w='quarter', h=20)
        assert size.w == 12
        assert size.h == 20

    def test_size_width_alias(self) -> None:
        """Test 'width' alias works for 'w'."""
        size = Size(width=30)
        assert size.w == 30

    def test_size_height_alias(self) -> None:
        """Test 'height' alias works for 'h'."""
        size = Size(height=15)
        assert size.h == 15

    def test_size_zero_width_rejected(self) -> None:
        """Test that zero width is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Size(w=0)
        assert 'Input should be greater than 0' in str(exc_info.value)

    def test_size_negative_width_rejected(self) -> None:
        """Test that negative width is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Size(w=-10)
        assert 'Input should be greater than 0' in str(exc_info.value)

    def test_size_zero_height_rejected(self) -> None:
        """Test that zero height is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Size(h=0)
        assert 'Input should be greater than 0' in str(exc_info.value)

    def test_size_negative_height_rejected(self) -> None:
        """Test that negative height is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Size(h=-5)
        assert 'Input should be greater than 0' in str(exc_info.value)

    def test_size_exceeds_grid_width_rejected(self) -> None:
        """Test that width exceeding 48 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Size(w=50)
        assert 'Input should be less than or equal to 48' in str(exc_info.value)


class TestPosition:
    """Test suite for Position model."""

    def test_position_default_none(self) -> None:
        """Test that Position defaults to None for both x and y."""
        pos = Position()
        assert pos.x is None
        assert pos.y is None

    def test_position_with_explicit_values(self) -> None:
        """Test Position with explicit numeric values."""
        pos = Position(x=10, y=20)
        assert pos.x == 10
        assert pos.y == 20

    def test_position_x_only(self) -> None:
        """Test Position with only x specified."""
        pos = Position(x=5)
        assert pos.x == 5
        assert pos.y is None

    def test_position_y_only(self) -> None:
        """Test Position with only y specified."""
        pos = Position(y=15)
        assert pos.x is None
        assert pos.y == 15

    def test_position_zero_coordinates(self) -> None:
        """Test that zero coordinates are valid."""
        pos = Position(x=0, y=0)
        assert pos.x == 0
        assert pos.y == 0

    def test_position_from_left_alias(self) -> None:
        """Test 'from_left' alias works for 'x'."""
        pos = Position(from_left=12)
        assert pos.x == 12

    def test_position_from_top_alias(self) -> None:
        """Test 'from_top' alias works for 'y'."""
        pos = Position(from_top=8)
        assert pos.y == 8

    def test_position_negative_x_rejected(self) -> None:
        """Test that negative x is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Position(x=-5)
        assert 'Input should be greater than or equal to 0' in str(exc_info.value)

    def test_position_negative_y_rejected(self) -> None:
        """Test that negative y is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Position(y=-10)
        assert 'Input should be greater than or equal to 0' in str(exc_info.value)
