from dataclasses import dataclass
from typing import Any, List

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
CLOSED = NORTH | EAST | SOUTH | WEST


class MazeError(Exception):
    """Raised when a maze is malformed or cannot be generated."""


@dataclass
class Maze:
    """A grid of cells; each cell stores which sides are walled."""

    width: int
    height: int
    walls: List[List[int]]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def has_wall(self, x: int, y: int, side: int) -> bool:
        """Return True if the given side of cell (x, y) is walled."""
        return bool(self.walls[y][x] & side)

    def is_walkable(self, x: int, y: int) -> bool:
        """Return True if the cell is inside the grid and not fully closed."""
        return self.in_bounds(x, y) and self.walls[y][x] != CLOSED

    @classmethod
    def from_grid(cls, grid: Any, width: int, height: int) -> "Maze":
        """Validate a raw grid and build a Maze.

        Args:
            grid: rows of integers, each in 0..15 (wall bitmask).
            width: expected number of columns.
            height: expected number of rows.

        Raises:
            MazeError: if the shape or any value is invalid.
        """
        if not isinstance(grid, list) or len(grid) != height:
            raise MazeError(f"expected {height} rows")
        walls: List[List[int]] = []
        for y, row in enumerate(grid):
            if not isinstance(row, list) or len(row) != width:
                raise MazeError(f"row {y}: expected {width} cells")
            for value in row:
                if (isinstance(value, bool) or not isinstance(value, int)
                        or not 0 <= value <= 15):
                    raise MazeError(f"row {y}: invalid cell {value!r}")
            walls.append(list(row))
            """return a validated instance"""
        return cls(width, height, walls)
