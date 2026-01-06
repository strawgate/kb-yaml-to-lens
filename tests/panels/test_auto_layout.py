"""Test auto-layout engine."""

import pytest

from dashboard_compiler.panels.auto_layout import AutoLayoutEngine


class TestAutoLayoutEngine:
    """Test suite for AutoLayoutEngine."""

    def test_single_panel_positioned_at_origin(self) -> None:
        """Test that a single panel is positioned at (0, 0)."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions([(0, 24, 12)])
        assert positions == [(0, 0)]

    def test_two_panels_side_by_side(self) -> None:
        """Test that two half-width panels are placed side by side."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions([(0, 24, 12), (1, 24, 12)])
        assert positions == [(0, 0), (24, 0)]

    def test_four_panels_form_grid(self) -> None:
        """Test that four quarter-width panels form a 2x2 grid with up-left algorithm."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions(
            [
                (0, 24, 12),
                (1, 24, 12),
                (2, 24, 12),
                (3, 24, 12),
            ]
        )
        assert positions == [(0, 0), (24, 0), (0, 12), (24, 12)]

    def test_full_width_panel_then_half_width(self) -> None:
        """Test full-width panel followed by half-width panels."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions(
            [
                (0, 48, 10),
                (1, 24, 12),
                (2, 24, 12),
            ]
        )
        assert positions == [(0, 0), (0, 10), (24, 10)]

    def test_locked_panel_creates_gap(self) -> None:
        """Test that locked panels create gaps that auto panels flow around."""
        engine = AutoLayoutEngine(algorithm='up-left')
        engine.mark_locked_panel(0, 0, 24, 20)
        positions = engine.compute_positions(
            [
                (0, 24, 12),
                (1, 24, 12),
            ]
        )
        assert positions == [(24, 0), (24, 12)]

    def test_locked_panel_in_middle(self) -> None:
        """Test auto-layout around a locked panel in the middle."""
        engine = AutoLayoutEngine(algorithm='up-left')
        engine.mark_locked_panel(12, 0, 24, 12)
        positions = engine.compute_positions(
            [
                (0, 12, 12),
                (1, 12, 12),
            ]
        )
        assert positions == [(0, 0), (36, 0)]

    def test_panels_of_varying_heights(self) -> None:
        """Test panels with different heights."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions(
            [
                (0, 24, 20),
                (1, 24, 10),
                (2, 24, 10),
            ]
        )
        assert positions == [(0, 0), (24, 0), (24, 10)]

    def test_left_right_algorithm_fills_rows(self) -> None:
        """Test left-right algorithm fills rows sequentially."""
        engine = AutoLayoutEngine(algorithm='left-right')
        positions = engine.compute_positions(
            [
                (0, 24, 12),
                (1, 24, 12),
                (2, 24, 12),
                (3, 24, 12),
            ]
        )
        assert positions == [(0, 0), (24, 0), (0, 12), (24, 12)]

    def test_invalid_algorithm_raises_error(self) -> None:
        """Test that invalid algorithm raises ValueError."""
        engine = AutoLayoutEngine(algorithm='up-left')
        engine.algorithm = 'invalid'  # type: ignore[assignment] # pyright: ignore[reportAttributeAccessIssue]
        with pytest.raises(ValueError, match='Unknown packing algorithm'):
            _ = engine.compute_positions([(0, 24, 12)])

    def test_custom_grid_width(self) -> None:
        """Test engine with custom grid width."""
        engine = AutoLayoutEngine(algorithm='up-left', grid_width=24)
        positions = engine.compute_positions(
            [
                (0, 12, 10),
                (1, 12, 10),
                (2, 12, 10),
            ]
        )
        assert positions == [(0, 0), (12, 0), (0, 10)]

    def test_panel_too_wide_for_grid_moves_down(self) -> None:
        """Test that panels too wide to fit next to existing panels move down."""
        engine = AutoLayoutEngine(algorithm='up-left')
        engine.mark_locked_panel(0, 0, 30, 10)
        positions = engine.compute_positions(
            [
                (0, 24, 12),
            ]
        )
        assert positions == [(0, 10)]

    def test_multiple_locked_panels(self) -> None:
        """Test auto-layout with multiple locked panels."""
        engine = AutoLayoutEngine(algorithm='up-left')
        engine.mark_locked_panel(0, 0, 12, 12)
        engine.mark_locked_panel(36, 0, 12, 12)
        positions = engine.compute_positions(
            [
                (0, 24, 12),
            ]
        )
        assert positions == [(12, 0)]

    def test_eighth_width_panels(self) -> None:
        """Test eight panels of eighth width fit in one row."""
        engine = AutoLayoutEngine(algorithm='up-left')
        positions = engine.compute_positions(
            [
                (0, 6, 10),
                (1, 6, 10),
                (2, 6, 10),
                (3, 6, 10),
                (4, 6, 10),
                (5, 6, 10),
                (6, 6, 10),
                (7, 6, 10),
            ]
        )
        assert positions == [
            (0, 0),
            (6, 0),
            (12, 0),
            (18, 0),
            (24, 0),
            (30, 0),
            (36, 0),
            (42, 0),
        ]
