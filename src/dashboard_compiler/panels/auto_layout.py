"""Auto-layout engine for dashboard panels.

This module provides automatic positioning of panels on the dashboard grid
using various packing algorithms.
"""

from typing import Literal

from dashboard_compiler.panels.config import KIBANA_GRID_WIDTH

PackingAlgorithm = Literal['up-left', 'left-right']

# Buffer for searching beyond occupied space when no position is found
_MAX_Y_SEARCH_BUFFER = 100


class AutoLayoutEngine:
    """Engine for automatically positioning panels on a dashboard grid.

    Supports multiple packing algorithms:
    - 'up-left': Float panels up first, then left (default, creates nice grids)
    - 'left-right': Fill rows left to right, then move to next row
    """

    def __init__(self, algorithm: PackingAlgorithm = 'up-left', grid_width: int = KIBANA_GRID_WIDTH) -> None:
        """Initialize the auto-layout engine.

        Args:
            algorithm: The packing algorithm to use.
            grid_width: The width of the grid in units.

        """
        self.algorithm: PackingAlgorithm = algorithm
        self.grid_width: int = grid_width
        self.occupied: set[tuple[int, int]] = set()

    def compute_positions(self, panels: list[tuple[int, int, int]]) -> list[tuple[int, int]]:
        """Compute positions for panels.

        Args:
            panels: List of (index, width, height) tuples for panels needing positions.

        Returns:
            List of (x, y) positions in the same order as input panels.

        """
        positions: list[tuple[int, int]] = []

        for _, width, height in panels:
            if self.algorithm == 'up-left':
                x, y = self._find_position_up_left(width, height)
            elif self.algorithm == 'left-right':
                x, y = self._find_position_left_right(width, height)
            else:
                msg = f'Unknown packing algorithm: {self.algorithm}'
                raise ValueError(msg)

            positions.append((x, y))
            self._mark_occupied(x, y, width, height)

        return positions

    def mark_locked_panel(self, x: int, y: int, width: int, height: int) -> None:
        """Mark a region as occupied by a locked panel.

        Args:
            x: The x coordinate.
            y: The y coordinate.
            width: The panel width.
            height: The panel height.

        """
        self._mark_occupied(x, y, width, height)

    def _mark_occupied(self, x: int, y: int, width: int, height: int) -> None:
        """Mark grid cells as occupied.

        Args:
            x: The x coordinate.
            y: The y coordinate.
            width: The panel width.
            height: The panel height.

        """
        for dy in range(height):
            for dx in range(width):
                self.occupied.add((x + dx, y + dy))

    def _find_position_up_left(self, width: int, height: int) -> tuple[int, int]:
        """Find next position using up-then-left algorithm.

        This creates nice grids by floating panels up first, then left.
        For example, 4 panels with no position info will form a 2x2 grid.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        """
        y = 0
        max_y = max((coord[1] for coord in self.occupied), default=0) + _MAX_Y_SEARCH_BUFFER

        while y <= max_y:
            for x in range(self.grid_width - width + 1):
                if self._can_place(x, y, width, height):
                    return (x, y)
            y += 1

        return (0, max_y + 1)

    def _find_position_left_right(self, width: int, height: int) -> tuple[int, int]:
        """Find next position using left-to-right, top-to-bottom algorithm.

        This fills rows from left to right, moving to the next row when needed.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        Raises:
            ValueError: If panel width exceeds grid width.

        """
        if width > self.grid_width:
            msg = f'Panel width {width} exceeds grid width {self.grid_width}'
            raise ValueError(msg)

        y = 0
        max_height_in_row = 0
        max_y = max((coord[1] for coord in self.occupied), default=0) + _MAX_Y_SEARCH_BUFFER

        while y <= max_y:
            for x in range(self.grid_width - width + 1):
                if self._can_place(x, y, width, height):
                    max_height_in_row = max(max_height_in_row, height)
                    return (x, y)

            y += max_height_in_row if max_height_in_row > 0 else 1
            max_height_in_row = 0

        return (0, max_y + 1)

    def _can_place(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if a panel can be placed at the given position.

        Args:
            x: The x coordinate.
            y: The y coordinate.
            width: The panel width.
            height: The panel height.

        Returns:
            bool: True if the panel can be placed, False otherwise.

        """
        if x + width > self.grid_width:
            return False

        for dy in range(height):
            for dx in range(width):
                if (x + dx, y + dy) in self.occupied:
                    return False

        return True
