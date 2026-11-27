"""Pixel sprites built ONCE per level: Pac-Man, ghosts and pellets."""

import os
from typing import Any, Dict, List

from game.entities import Direction, GhostState
from .draw_tools import bake_image, flip_image, load_image, scale_image

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
PACMAN_FILES = ("pacman_open.png", "pacman_closed.png")

Image = Dict[str, Any]

CLEAR = (0, 0, 0, 0)
WHITE = (255, 255, 255, 255)
PUPIL = (20, 20, 200, 255)
EDIBLE_COLOR = (33, 33, 255, 255)
GHOST_COLORS = {
    "blinky": (255, 0, 0, 255),
    "pinky": (255, 184, 255, 255),
    "inky": (0, 255, 255, 255),
    "clyde": (255, 184, 82, 255),
}


# --- Pac-Man ---------------------------------------------------------------

def rotate_cw(img: Image) -> Image:
    """Rotate 90 degrees clockwise (facing right -> facing down)."""
    h, w = img["h"], img["w"]
    pixels = [[img["pixels"][h - 1 - x][y] for x in range(h)]
              for y in range(w)]
    return {"w": h, "h": w, "pixels": pixels}


def rotate_ccw(img: Image) -> Image:
    """Rotate 90 degrees counter-clockwise (facing right -> facing up)."""
    h, w = img["h"], img["w"]
    pixels = [[img["pixels"][x][w - 1 - y] for x in range(h)]
              for y in range(w)]
    return {"w": h, "h": w, "pixels": pixels}


def build_pacman_sprites(size: int) -> Dict[Direction, List[Image]]:
    """{direction: [mouth open, mouth closed]}. The PNGs face right."""
    frames = [scale_image(load_image(os.path.join(IMAGES_DIR, name)),
                          size, size) for name in PACMAN_FILES]
    oriented = {
        Direction.RIGHT: frames,
        Direction.LEFT: [flip_image(f) for f in frames],
        Direction.DOWN: [rotate_cw(f) for f in frames],
        Direction.UP: [rotate_ccw(f) for f in frames],
    }
    return {d: [bake_image(f) for f in fs] for d, fs in oriented.items()}


# --- ghosts ----------------------------------------------------------------

def _ghost_pixels(size: int, body: tuple, mode: str) -> List[List[tuple]]:
    """RGBA grid of a ghost. mode: 'normal', 'edible' or 'eyes' (only eyes)."""
    r = size / 2
    eye_r = max(1.5, size / 8)
    pupil_r = max(1.0, size / 16)
    eyes = ((size * 0.32, size * 0.38), (size * 0.68, size * 0.38))
    skirt_y = size - max(2, size // 5)

    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            px, py = x + 0.5, y + 0.5
            color = CLEAR
            if mode != "eyes":
                dx, dy = px - r, py - r
                inside = dx * dx + dy * dy <= r * r if dy < 0 else abs(dx) <= r
                if y >= skirt_y and (x * 5 // size) % 2 == 1:
                    inside = False                      # wavy bottom
                if inside:
                    color = body
            for ex, ey in eyes:
                d2 = (px - ex) ** 2 + (py - ey) ** 2
                if mode == "edible":
                    if d2 <= pupil_r ** 2:
                        color = WHITE
                elif d2 <= eye_r ** 2:
                    color = PUPIL if d2 <= pupil_r ** 2 else WHITE
            row.append(color)
        pixels.append(row)
    return pixels


def _bake_ghost(size: int, body: tuple, mode: str) -> Image:
    return bake_image({"w": size, "h": size,
                       "pixels": _ghost_pixels(size, body, mode)})


def build_ghost_sprites(size: int) -> Dict[str, Dict[GhostState, Image]]:
    """{ghost name: {state: sprite}}."""
    sprites = {}
    for name, color in GHOST_COLORS.items():
        sprites[name] = {
            GhostState.CHASE: _bake_ghost(size, color, "normal"),
            GhostState.EDIBLE: _bake_ghost(size, EDIBLE_COLOR, "edible"),
            GhostState.RESPAWNING: _bake_ghost(size, color, "eyes"),
        }
    return sprites


# --- pellets ---------------------------------------------------------------

def build_pellet(radius: int, color: tuple) -> Image:
    """A filled circle sprite."""
    size = radius * 2 + 1
    pixels = [[(*color, 255)
               if (x - radius) ** 2 + (y - radius) ** 2 <= radius ** 2
               else CLEAR
               for x in range(size)] for y in range(size)]
    return bake_image({"w": size, "h": size, "pixels": pixels})