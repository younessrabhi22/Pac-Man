"""One level: the maze plus where everything starts."""

import random
from typing import List, Tuple

from maze.maze import Maze
from maze.maze_loader import load_maze

Cell = Tuple[int, int]




class Level:
    """Static layout of a level: maze, spawn cells and pellets."""

    def __init__(self, number: int, width: int, height: int, seed: int,
                 pacgum_count: int, time_limit: int) -> None:
        """Build the maze, pick the spawn cells and place the pellets."""
        self.number = number
        self.time_limit = time_limit
        self.maze: Maze = load_maze(width, height, seed)

        self.ghost_spawns: List[Cell] = [
            (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)
        ]

        cx, cy = width // 2, height // 2
        candidates = [
            (cx, cy), (cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)
        ]
        self.player_spawn: Cell = (0, 0)
        for x, y in candidates:
            if self.maze.is_walkable(x, y):
                self.player_spawn = (x, y)
                break

        self.super_pacgums: List[Cell] = self.ghost_spawns.copy()
        self.pacgums: List[Cell] = self._place_pacgums(pacgum_count)

    def _walkable_cells(self) -> List[Cell]:
        """Return every walkable cell in the maze."""
        cells: List[Cell] = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_walkable(x, y):
                    cells.append((x, y))
        return cells

    def _place_pacgums(self, count: int) -> List[Cell]:
        """Place pacgums randomly on free walkable cells."""
        reserved = self.ghost_spawns + [self.player_spawn]
        free = [c for c in self._walkable_cells() if c not in reserved]
        return random.sample(free, min(count, len(free)))