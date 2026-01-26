"""Test auto-layout engine."""

import pytest

from kb_dashboard_core.panels.auto_layout import (
    BlockedEngine,
    FirstAvailableGapEngine,
    LeftRightEngine,
    UpLeftEngine,
    create_layout_engine,
)


class TestStatefulAPI:
    """Test suite for the stateful add_panel API."""

    def test_add_panel_returns_position(self) -> None:
        """Test that add_panel returns the position immediately."""
        engine = UpLeftEngine()
        x, y = engine.add_panel(24, 12)
        assert (x, y) == (0, 0)

    def test_add_multiple_panels_statefully(self) -> None:
        """Test adding multiple panels and getting positions immediately."""
        engine = UpLeftEngine()
        pos1 = engine.add_panel(24, 12)
        pos2 = engine.add_panel(24, 12)
        pos3 = engine.add_panel(24, 12)

        assert pos1 == (0, 0)
        assert pos2 == (24, 0)
        assert pos3 == (0, 12)

    def test_mark_locked_panel_before_add(self) -> None:
        """Test marking a panel as locked before adding panels."""
        engine = UpLeftEngine()
        engine.mark_locked_panel(0, 0, 24, 12)

        pos = engine.add_panel(24, 12)
        assert pos == (24, 0)

    def test_oversized_panel_raises_error(self) -> None:
        """Test that adding a panel wider than grid raises error."""
        engine = UpLeftEngine()
        with pytest.raises(ValueError, match=r'Panel width .* exceeds grid width'):
            engine.add_panel(60, 12)


class TestUpLeftEngine:
    """Test suite for UpLeftEngine."""

    def test_single_panel_at_origin(self) -> None:
        """Test that a single panel is positioned at (0, 0)."""
        engine = UpLeftEngine()
        assert engine.add_panel(24, 12) == (0, 0)

    def test_two_panels_side_by_side(self) -> None:
        """Test that two half-width panels are placed side by side."""
        engine = UpLeftEngine()
        assert engine.add_panel(24, 12) == (0, 0)
        assert engine.add_panel(24, 12) == (24, 0)

    def test_four_panels_form_grid(self) -> None:
        """Test that four panels form a 2x2 grid."""
        engine = UpLeftEngine()
        positions = [
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
        ]
        assert positions == [(0, 0), (24, 0), (0, 12), (24, 12)]

    def test_floats_up_to_fill_gap(self) -> None:
        """Test that panels float up to fill gaps."""
        engine = UpLeftEngine()
        engine.mark_locked_panel(0, 0, 24, 20)

        # First panel goes to the right of locked panel
        assert engine.add_panel(24, 12) == (24, 0)

        # Second panel floats up to fill the gap at (24, 12)
        assert engine.add_panel(24, 8) == (24, 12)

    def test_varying_heights(self) -> None:
        """Test panels with varying heights."""
        engine = UpLeftEngine()
        assert engine.add_panel(24, 20) == (0, 0)
        assert engine.add_panel(24, 10) == (24, 0)
        assert engine.add_panel(24, 10) == (24, 10)


class TestLeftRightEngine:
    """Test suite for LeftRightEngine."""

    def test_single_panel_at_origin(self) -> None:
        """Test that a single panel is positioned at (0, 0)."""
        engine = LeftRightEngine()
        assert engine.add_panel(24, 12) == (0, 0)

    def test_fills_row_left_to_right(self) -> None:
        """Test that panels fill rows from left to right."""
        engine = LeftRightEngine()
        positions = [
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
            engine.add_panel(24, 12),
        ]
        assert positions == [(0, 0), (24, 0), (0, 12), (24, 12)]

    def test_row_height_determined_by_tallest_panel(self) -> None:
        """Test that row height is determined by tallest panel in row."""
        engine = LeftRightEngine()
        assert engine.add_panel(12, 10) == (0, 0)
        assert engine.add_panel(12, 20) == (12, 0)
        assert engine.add_panel(12, 5) == (24, 0)

        # Next row should start at y=20 (tallest panel in first row)
        assert engine.add_panel(12, 10) == (36, 0)
        assert engine.add_panel(12, 10) == (0, 20)

    def test_locked_panel_affects_row_placement(self) -> None:
        """Test that locked panels affect row placement."""
        engine = LeftRightEngine()
        engine.mark_locked_panel(24, 0, 24, 15)

        # First panel fits before locked panel
        assert engine.add_panel(12, 10) == (0, 0)

        # Second panel won't fit in row, goes to next row
        assert engine.add_panel(24, 10) == (0, 15)


class TestBlockedEngine:
    """Test suite for BlockedEngine."""

    def test_single_panel_at_origin(self) -> None:
        """Test that a single panel is positioned at (0, 0)."""
        engine = BlockedEngine()
        assert engine.add_panel(24, 12) == (0, 0)

    def test_never_fills_gaps_above(self) -> None:
        """Test that panels never fill gaps above current bottom."""
        engine = BlockedEngine()
        engine.mark_locked_panel(0, 0, 24, 20)

        # First panel goes to right of locked panel (same row)
        assert engine.add_panel(24, 12) == (24, 0)

        # Second panel does NOT float up to (24, 12), instead goes below at y=20
        assert engine.add_panel(24, 10) == (0, 20)

    def test_maintains_vertical_order(self) -> None:
        """Test that panels maintain vertical order."""
        engine = BlockedEngine()
        positions = [
            engine.add_panel(24, 10),
            engine.add_panel(24, 10),
            engine.add_panel(24, 10),
        ]

        # Each panel should be at or below the previous
        assert positions[0][1] <= positions[1][1]
        assert positions[1][1] <= positions[2][1]

    def test_multiple_panels_same_row(self) -> None:
        """Test multiple panels can fit in same row if space available."""
        engine = BlockedEngine()
        assert engine.add_panel(12, 10) == (0, 0)
        assert engine.add_panel(12, 10) == (12, 0)
        assert engine.add_panel(12, 10) == (24, 0)
        assert engine.add_panel(12, 10) == (36, 0)

        # Next panel moves to next row
        assert engine.add_panel(12, 10) == (0, 10)


class TestFirstAvailableGapEngine:
    """Test suite for FirstAvailableGapEngine."""

    def test_single_panel_at_origin(self) -> None:
        """Test that a single panel is positioned at (0, 0)."""
        engine = FirstAvailableGapEngine()
        assert engine.add_panel(24, 12) == (0, 0)

    def test_fills_first_available_gap(self) -> None:
        """Test that panels fill the first available gap."""
        engine = FirstAvailableGapEngine()
        engine.mark_locked_panel(0, 0, 24, 20)

        # First panel fills gap to right
        assert engine.add_panel(24, 12) == (24, 0)

        # Second small panel fills the first gap it finds at (24, 12)
        assert engine.add_panel(24, 8) == (24, 12)

    def test_small_panel_fills_earlier_gap(self) -> None:
        """Test that small panels can fill gaps earlier than larger panels."""
        engine = FirstAvailableGapEngine()

        # Create a grid with a gap
        engine.add_panel(24, 20)
        engine.add_panel(24, 10)

        # Small panel fills gap at (24, 10) instead of going to y=20
        assert engine.add_panel(12, 10) == (24, 10)

    def test_scans_from_origin(self) -> None:
        """Test that algorithm scans from (0,0) for each panel."""
        engine = FirstAvailableGapEngine()
        engine.mark_locked_panel(12, 0, 24, 12)

        # First gap is at (0, 0)
        assert engine.add_panel(12, 12) == (0, 0)

        # Next gap is at (36, 0)
        assert engine.add_panel(12, 12) == (36, 0)


class TestCreateLayoutEngine:
    """Test suite for create_layout_engine factory."""

    def test_creates_up_left_engine(self) -> None:
        """Test factory creates UpLeftEngine."""
        engine = create_layout_engine('up-left')
        assert isinstance(engine, UpLeftEngine)

    def test_creates_left_right_engine(self) -> None:
        """Test factory creates LeftRightEngine."""
        engine = create_layout_engine('left-right')
        assert isinstance(engine, LeftRightEngine)

    def test_creates_blocked_engine(self) -> None:
        """Test factory creates BlockedEngine."""
        engine = create_layout_engine('blocked')
        assert isinstance(engine, BlockedEngine)

    def test_creates_first_available_gap_engine(self) -> None:
        """Test factory creates FirstAvailableGapEngine."""
        engine = create_layout_engine('first-available-gap')
        assert isinstance(engine, FirstAvailableGapEngine)

    def test_invalid_algorithm_raises_error(self) -> None:
        """Test that invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match='Unknown layout algorithm'):
            create_layout_engine('invalid')  # type: ignore[arg-type]

    def test_custom_grid_width(self) -> None:
        """Test factory respects custom grid width."""
        engine = create_layout_engine('up-left', grid_width=24)
        assert engine.grid_width == 24
