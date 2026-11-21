import math
import pygame

WIDTH = 1700
HEIGHT = 900

def put_pixel(screen, x, y, color):
    """Same bounds check you must do yourself in C before writing a pixel."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        screen.set_at((x, y), color)

def scale_image(img, new_w, new_h):
    """Nearest-neighbour resize (no smoothscale in MiniLibX)."""
    pixels = []
    for y in range(new_h):
        src_row = img["pixels"][y * img["h"] // new_h]
        pixels.append([src_row[x * img["w"] // new_w] for x in range(new_w)])
    return {"w": new_w, "h": new_h, "pixels": pixels}


def flip_image(img):
    """Mirror left <-> right (for a Pac-Man going the other way)."""
    return {"w": img["w"], "h": img["h"], "pixels": [row[::-1] for row in img["pixels"]]}

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


def draw_image(screen, img, x, y):
    for px, py, color in img["visible"]:
        put_pixel(screen, x + px, y + py, color)


def load_image(path):
    """PNG file -> plain 2D list of (r, g, b, a). Done ONCE, never per frame."""
    print(f"this is the path: {path}")

    surf = pygame.image.load(path)
    w, h = surf.get_size()
    pixels = [[tuple(surf.get_at((x, y))) for x in range(w)] for y in range(h)]
    return {"w": w, "h": h, "pixels": pixels}


def draw_rounded_rect(screen, x, y, width, height, color, radius=20):
    radius = min(radius, width // 2, height // 2)

    for i in range(height):
        if i < radius:
            dy = radius - (i + 0.5)
        elif i >= height - radius:
            dy = (i + 0.5) - (height - radius)
        else:
            dy = 0

        if dy > 0:
            inset = round(radius - math.sqrt(radius * radius - dy * dy))
        else:
            inset = 0

        screen.fill(color, (x + inset, y + i, width - 2 * inset, 1))