import pygame
import os
from .constants import WIDTH, HEIGHT
from .draw_tools import draw_image, scale_image, flip_image
from .text_rendering import draw_text, text_width


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
FONT_PATH = os.path.join(BASE_DIR, "font.json")


class BackgroundPacman:
    def __init__(self, x, y, speed, frames):
        self.x = x
        self.y = y
        self.speed = speed
        self.frames = frames[1 if speed > 0 else -1]
        self.w = self.frames[0]["w"]
    def update(self):
        self.x += self.speed
        if self.speed > 0 and self.x > WIDTH:
            self.x = -self.w
        elif self.speed < 0 and self.x < -self.w:
            self.x = WIDTH

    def draw(self, screen, tick):
        frame = self.frames[(tick // 8) % len(self.frames)]   # mouth open / closed
        draw_image(screen, frame, self.x, self.y)


def load_image(path):
    """PNG file -> plain 2D list of (r, g, b, a). Done ONCE, never per frame."""
    surf = pygame.image.load(path)
    w, h = surf.get_size()
    pixels = [[tuple(surf.get_at((x, y))) for x in range(w)] for y in range(h)]
    return {"w": w, "h": h, "pixels": pixels}


def make_background_pacmans(frames, count=10):
    pacmans = []
    for i in range(count):
        y = 30 + i * (HEIGHT - 120) // count
        speed = (1 + i % 3) * (1 if i % 2 == 0 else -1)
        x = (i * 337) % WIDTH
        pacmans.append(BackgroundPacman(x, y, speed, frames))
    return pacmans

def draw_menu(screen, buttons):
    title = "PAC-MAN"
    scale = 12
    x = (WIDTH - text_width(title, scale)) // 2
    draw_text(screen, x, 70, title, (254, 229, 20), scale)

    for button in buttons:
        button.draw(screen)


def bake_image(img, brightness=100, alpha_threshold=128):
    """Keep only the visible pixels, as (x, y, (r, g, b)).

    XPM/MLX transparency is all-or-nothing, so a pixel is either drawn or
    skipped. brightness < 100 darkens the sprite (good for a background).
    """
    img["visible"] = [
        (x, y, (r * brightness // 100, g * brightness // 100, b * brightness // 100))
        for y, row in enumerate(img["pixels"])
        for x, (r, g, b, a) in enumerate(row)
        if a >= alpha_threshold
    ]
    return img




# ---------------------------------------------------------------------------
# Pac-Men drifting across the menu background
# ---------------------------------------------------------------------------
def build_pacman_frames(size, brightness=60):
    """Returns {1: [frames facing right], -1: [frames facing left]}."""
    names = ("pacman_open.png", "pacman_closed.png")
    base = [load_image(os.path.join(IMAGES_DIR, n)) for n in names]
    right = [bake_image(scale_image(img, size, size), brightness) for img in base]
    left = [bake_image(flip_image(img), brightness) for img in right]
    return {1: right, -1: left}
