"""Auto-layout engine for dashboard panels.

This module provides automatic positioning of panels on the dashboard grid
using various packing algorithms. Each algorithm is implemented as a subclass
of BaseLayoutEngine, providing a stateful API where panels can be added
one at a time.
"""

from abc import ABC, abstractmethod
from typing import Literal, override

from kb_dashboard_core.panels.config import KIBANA_GRID_WIDTH

LayoutAlgorithm = Literal['up-left', 'left-right', 'blocked', 'first-available-gap']

# Buffer for searching beyond occupied space when no position is found
_MAX_Y_SEARCH_BUFFER = 100


class BaseLayoutEngine(ABC):
    """Abstract base class for panel layout algorithms.

    Provides a stateful API where panels are added one at a time,
    with each panel receiving its position immediately.
    """

    def __init__(self, grid_width: int = KIBANA_GRID_WIDTH) -> None:
        """Initialize the layout engine.

        Args:
            grid_width: The width of the grid in units.

        """
        self.grid_width: int = grid_width
        self.occupied: set[tuple[int, int]] = set()

    def add_panel(self, width: int, height: int) -> tuple[int, int]:
        """Add a panel and return its position.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates where the panel was placed.

        Raises:
            ValueError: If panel width exceeds grid width.

        """
        if width > self.grid_width:
            msg = f'Panel width {width} exceeds grid width {self.grid_width}'
            raise ValueError(msg)

        x, y = self._find_position(width, height)
        self._mark_occupied(x, y, width, height)
        return (x, y)

    def mark_locked_panel(self, x: int, y: int, width: int, height: int) -> None:
        """Mark a region as occupied by a locked panel.

        Args:
            x: The x coordinate.
            y: The y coordinate.
            width: The panel width.
            height: The panel height.

        """
        self._mark_occupied(x, y, width, height)

    @abstractmethod
    def _find_position(self, width: int, height: int) -> tuple[int, int]:
        """Find the next position for a panel.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        """

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


class UpLeftEngine(BaseLayoutEngine):
    """Layout engine that floats panels up first, then left.

    This creates nice grids by trying to place panels as high and left
    as possible. For example, 4 panels with no position info will form
    a 2x2 grid.
    """

    @override
    def _find_position(self, width: int, height: int) -> tuple[int, int]:
        """Find next position using up-then-left algorithm.

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


class LeftRightEngine(BaseLayoutEngine):
    """Layout engine that fills rows from left to right.

    This fills each row completely from left to right before moving
    to the next row. The row height is determined by the tallest panel
    in that row (including locked panels).

    Example layout for panels with widths [24, 24, 12, 12, 24] and heights [8, 10, 8, 8, 8]:
        Row 1: Panel 1 (w=24, h=8) | Panel 2 (w=24, h=10)
               [Row height = 10, determined by tallest panel]
        Row 2: Panel 3 (w=12, h=8) | Panel 4 (w=12, h=8) | Panel 5 (w=24, h=8)
               [Row height = 8, all panels same height]

    This creates a reading flow similar to text, where panels appear
    in the order they're defined when read left-to-right, top-to-bottom.
    """

    def __init__(self, grid_width: int = KIBANA_GRID_WIDTH) -> None:
        """Initialize the left-right layout engine.

        Args:
            grid_width: The width of the grid in units.

        """
        super().__init__(grid_width)
        self.current_row_y: int = 0
        self.current_row_max_height: int = 0

    def _get_row_height(self, y: int) -> int:
        """Get the height of the current row based on all occupied cells.

        Finds the maximum vertical extent from row y to any occupied cell
        at or below y, which gives the row height needed to clear all panels.

        Args:
            y: The current row's y coordinate.

        Returns:
            The maximum height of any panel in this row.

        """
        max_height = 0
        for _x, cell_y in self.occupied:
            if cell_y >= y:
                max_height = max(max_height, cell_y - y + 1)
        return max_height

    @override
    def _find_position(self, width: int, height: int) -> tuple[int, int]:
        """Find next position using left-to-right algorithm.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        """
        max_y = max((coord[1] for coord in self.occupied), default=0) + _MAX_Y_SEARCH_BUFFER

        while self.current_row_y <= max_y:
            for x in range(self.grid_width - width + 1):
                if self._can_place(x, self.current_row_y, width, height):
                    self.current_row_max_height = max(self.current_row_max_height, height)
                    return (x, self.current_row_y)

            # Move to next row - height is determined by all panels in current row
            row_height = max(self.current_row_max_height, self._get_row_height(self.current_row_y))
            self.current_row_y += row_height if row_height > 0 else 1
            self.current_row_max_height = 0

        return (0, max_y + 1)


class BlockedEngine(BaseLayoutEngine):
    """Layout engine that never fills gaps higher than the current bottom.

    This algorithm tracks the lowest Y position where panels have been placed
    and never places new panels above that line. It can fill horizontally in
    the current row, but won't backfill gaps created by varying panel heights.

    When a row contains locked panels, the entire row is skipped after placing
    the first auto-positioned panel in that row.

    Useful for maintaining a strict top-to-bottom flow where panels
    appear in the same vertical order as they're defined.
    """

    def __init__(self, grid_width: int = KIBANA_GRID_WIDTH) -> None:
        """Initialize the blocked layout engine.

        Args:
            grid_width: The width of the grid in units.

        """
        super().__init__(grid_width)
        self.min_y: int = 0
        self.locked_positions: set[tuple[int, int]] = set()

    @override
    def mark_locked_panel(self, x: int, y: int, width: int, height: int) -> None:
        """Mark a region as occupied by a locked panel.

        Args:
            x: The x coordinate.
            y: The y coordinate.
            width: The panel width.
            height: The panel height.

        """
        super().mark_locked_panel(x, y, width, height)
        # Track which cells belong to locked panels
        for dy in range(height):
            for dx in range(width):
                self.locked_positions.add((x + dx, y + dy))

    @override
    def _find_position(self, width: int, height: int) -> tuple[int, int]:
        """Find next position without filling gaps above current bottom.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        """
        max_y = self.min_y + _MAX_Y_SEARCH_BUFFER

        y = self.min_y
        while y <= max_y:
            for x in range(self.grid_width - width + 1):
                if self._can_place(x, y, width, height):
                    return (x, y)
            y += 1

        return (0, max_y + 1)

    @override
    def add_panel(self, width: int, height: int) -> tuple[int, int]:
        """Add a panel and return its position.

        Overrides base class to update min_y tracking.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates where the panel was placed.

        Raises:
            ValueError: If panel width exceeds grid width.

        """
        x, y = super().add_panel(width, height)

        # If we placed in a row that has locked panels, skip the entire row
        if y >= self.min_y:
            # Check if there are locked panels in this row
            has_locked_in_row = any(cell_y == y for _cell_x, cell_y in self.locked_positions)

            if has_locked_in_row is True:
                # Find the maximum bottom edge of all panels in this row
                max_y_in_row = y + height - 1
                for cell_x, cell_y in self.occupied:
                    if cell_y == y:
                        panel_bottom = cell_y
                        while (cell_x, panel_bottom + 1) in self.occupied:
                            panel_bottom += 1
                        max_y_in_row = max(max_y_in_row, panel_bottom)

                self.min_y = max_y_in_row + 1

        return (x, y)


class FirstAvailableGapEngine(BaseLayoutEngine):
    """Layout engine that scans the entire grid for the first available gap.

    This algorithm searches the grid systematically from (0, 0) going
    left-to-right, top-to-bottom to find the first position where the
    panel fits. This can result in panels appearing earlier in the grid
    than panels defined before them in the array.

    Useful for maximizing space utilization and minimizing dashboard height.
    """

    @override
    def _find_position(self, width: int, height: int) -> tuple[int, int]:
        """Find first available gap in the entire grid.

        Args:
            width: The panel width.
            height: The panel height.

        Returns:
            Tuple of (x, y) coordinates.

        """
        max_y = max((coord[1] for coord in self.occupied), default=0) + _MAX_Y_SEARCH_BUFFER

        for y in range(max_y + 1):
            for x in range(self.grid_width - width + 1):
                if self._can_place(x, y, width, height):
                    return (x, y)

        return (0, max_y + 1)


def create_layout_engine(algorithm: LayoutAlgorithm, grid_width: int = KIBANA_GRID_WIDTH) -> BaseLayoutEngine:
    """Create a layout engine for the given algorithm.

    Args:
        algorithm: The layout algorithm to use.
        grid_width: The width of the grid in units.

    Returns:
        A layout engine instance.

    Raises:
        ValueError: If the algorithm is not recognized.

    """
    if algorithm == 'up-left':
        return UpLeftEngine(grid_width)
    if algorithm == 'left-right':
        return LeftRightEngine(grid_width)
    if algorithm == 'blocked':
        return BlockedEngine(grid_width)
    if algorithm == 'first-available-gap':
        return FirstAvailableGapEngine(grid_width)

    # This should be unreachable due to the Literal type, but handle runtime errors gracefully
    msg = f'Unknown layout algorithm: {algorithm}'
    raise ValueError(msg)  # pyright: ignore[reportUnreachable]
