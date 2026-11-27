"""Draw score, level, time and hearts in the band above the maze."""

from .draw_tools import WIDTH, put_pixel
from .text_rendering import draw_text, text_height, text_width

HUD_HEIGHT = 80          # the maze is built with top_margin=HUD_HEIGHT
HUD_MARGIN = 40
TEXT_SCALE = 3
HEART_SCALE = 3
HEART_GAP = 6
TEXT_COLOR = (255, 255, 255)
HEART_COLOR = (255, 0, 0)

HEART = [
    "0110110",
    "1111111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]
HEART_W = len(HEART[0]) * HEART_SCALE
HEART_H = len(HEART) * HEART_SCALE


def _draw_heart(screen, x, y):
    for row, line in enumerate(HEART):
        for col, bit in enumerate(line):
            if bit != "1":
                continue
            for dy in range(HEART_SCALE):
                for dx in range(HEART_SCALE):
                    put_pixel(screen, x + col * HEART_SCALE + dx,
                              y + row * HEART_SCALE + dy, HEART_COLOR)


def _draw_centered(screen, cx, y, text):
    x = cx - text_width(text, TEXT_SCALE) // 2
    draw_text(screen, x, y, text, TEXT_COLOR, TEXT_SCALE)


def draw_hud(screen, game_state):
    """Score on the left, level and time in the middle, hearts on the right."""
    y = (HUD_HEIGHT - text_height(TEXT_SCALE)) // 2

    draw_text(screen, HUD_MARGIN, y, f"SCORE {game_state.score}",
              TEXT_COLOR, TEXT_SCALE)
    _draw_centered(screen, WIDTH * 2 // 5, y,
                   f"LEVEL {game_state.level_number}")
    _draw_centered(screen, WIDTH * 3 // 5, y,
                   f"TIME {int(game_state.time_left)}")

    lives = max(0, game_state.player.lives)
    total = lives * HEART_W + max(0, lives - 1) * HEART_GAP
    x = WIDTH - HUD_MARGIN - total
    hy = (HUD_HEIGHT - HEART_H) // 2
    for _ in range(lives):
        _draw_heart(screen, x, hy)
        x += HEART_W + HEART_GAP