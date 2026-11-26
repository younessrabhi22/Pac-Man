"""Draw a Maze on the screen with MiniLibX-compatible primitives only.

The maze is rendered ONCE into an image buffer (mlx_new_image + pixel writes),
then the whole image is put on the window each frame
(mlx_put_image_to_window).
"""

from dataclasses import dataclass
from typing import Tuple

import pygame

from maze.maze import Maze, NORTH, EAST, SOUTH, WEST, CLOSED
from .draw_tools import WIDTH, HEIGHT

WALL_COLOR = (33, 33, 222)
CLOSED_COLOR = (20, 20, 140)      # the isolated '42' cells
MAX_WALL = 8                      # thickest wall, in pixels


@dataclass
class MazeView:
    """A pre-rendered maze and where it sits on the screen."""

    image: pygame.Surface
    x: int          # screen position of the image's top-left corner
    y: int
    cell: int       # cell size in pixels
    wall: int       # wall thickness in pixels

    def cell_to_screen(self, cx: int, cy: int) -> Tuple[int, int]:
        """Top-left screen pixel of cell (cx, cy) (for player / ghosts)."""
        return self.x + cx * self.cell, self.y + cy * self.cell

    def cell_center(self, cx: int, cy: int) -> Tuple[int, int]:
        """Centre screen pixel of cell (cx, cy)."""
        px, py = self.cell_to_screen(cx, cy)
        return px + self.cell // 2, py + self.cell // 2


# --- image buffer primitives (what you'd write on a mlx image) -------------

def _image_put_pixel(img: pygame.Surface, x: int, y: int,
                     color: Tuple[int, int, int]) -> None:
    """Write one pixel into the image buffer, with a bounds check."""
    if 0 <= x < img.get_width() and 0 <= y < img.get_height():
        img.set_at((x, y), color)


def _image_fill_rect(img: pygame.Surface, x: int, y: int, w: int, h: int,
                     color: Tuple[int, int, int]) -> None:
    """Fill a rectangle pixel by pixel."""
    for j in range(y, y + h):
        for i in range(x, x + w):
            _image_put_pixel(img, i, j, color)


# --- wall lookup (robust if two neighbours disagree about a shared wall) ---

def _wall_north(maze: Maze, x: int, y: int) -> bool:
    return maze.has_wall(x, y, NORTH) or (y > 0 and maze.has_wall(x, y - 1, SOUTH))


def _wall_west(maze: Maze, x: int, y: int) -> bool:
    return maze.has_wall(x, y, WEST) or (x > 0 and maze.has_wall(x - 1, y, EAST))


# --- layout + rendering -----------------------------------------------------

def build_maze_view(maze: Maze, top_margin: int = 0) -> MazeView:
    """Render the maze into an image, sized to fit the screen and centred.

    Args:
        maze: the Maze (built from MazeGenerator.maze by load_maze).
        top_margin: pixels kept free at the top (for score / lives HUD).
    """
    cell = max(4, min((WIDTH - MAX_WALL) // maze.width,
                      (HEIGHT - top_margin - MAX_WALL) // maze.height))
    wall = min(MAX_WALL, max(2, cell // 6))

    img_w = maze.width * cell + wall
    img_h = maze.height * cell + wall
    # A fresh Surface is all black. With a real mlx image you must clear the
    # buffer yourself (ft_memset to 0) before drawing.
    img = pygame.Surface((img_w, img_h))

    for y in range(maze.height):
        for x in range(maze.width):
            px, py = x * cell, y * cell

            if maze.walls[y][x] == CLOSED:           # the '42' block
                _image_fill_rect(img, px, py, cell, cell, CLOSED_COLOR)

            # Each cell owns its top and left line (they are 'wall' thick
            # and 'cell + wall' long so corners join without gaps).
            if _wall_north(maze, x, y):
                _image_fill_rect(img, px, py, cell + wall, wall, WALL_COLOR)
            if _wall_west(maze, x, y):
                _image_fill_rect(img, px, py, wall, cell + wall, WALL_COLOR)

            # Only the last column / row also own their right / bottom line.
            if x == maze.width - 1 and maze.has_wall(x, y, EAST):
                _image_fill_rect(img, px + cell, py, wall, cell + wall,
                                 WALL_COLOR)
            if y == maze.height - 1 and maze.has_wall(x, y, SOUTH):
                _image_fill_rect(img, px, py + cell, cell + wall, wall,
                                 WALL_COLOR)

    ox = (WIDTH - img_w) // 2
    oy = top_margin + (HEIGHT - top_margin - img_h) // 2
    return MazeView(img, ox, oy, cell, wall)


def draw_maze(screen: pygame.Surface, view: MazeView) -> None:
    """Put the pre-rendered maze on the screen (mlx_put_image_to_window)."""
    screen.blit(view.image, (view.x, view.y))