import json
import math
import os

import pygame

pygame.init()

WIDTH = 1700
HEIGHT = 900

# ---------------------------------------------------------------------------
# Font loading (font.json lives next to this file)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "font.json")
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def load_font(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_font_data = load_font(FONT_PATH)
FONT = _font_data["glyphs"]
GLYPH_HEIGHT = _font_data["height"]
LETTER_SPACING = _font_data["letter_spacing"]
SPACE_WIDTH = _font_data["space_width"]


def get_glyph(char):
    """Bitmap for a character. The font is single-case, so 'a' uses 'A'."""
    return FONT.get(char) or FONT.get(char.upper())


def glyph_width(char):
    bitmap = get_glyph(char)
    return len(bitmap[0]) if bitmap else SPACE_WIDTH


def text_width(text, scale=1):
    """Pixel width of a single line of text (for centering / right-aligning)."""
    if not text:
        return 0
    columns = sum(glyph_width(c) for c in text) + LETTER_SPACING * (len(text) - 1)
    return columns * scale


def text_height(scale=1):
    return GLYPH_HEIGHT * scale


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
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


def draw_text(screen, x, y, text, color, scale=3):
    """Draw text with the bitmap font. '\\n' starts a new line."""
    cursor_x = x
    line_height = (GLYPH_HEIGHT + LETTER_SPACING) * scale

    for char in text:
        if char == "\n":
            cursor_x = x
            y += line_height
            continue

        bitmap = get_glyph(char)
        if bitmap is None:
            cursor_x += (SPACE_WIDTH + LETTER_SPACING) * scale
            continue

        for row, line in enumerate(bitmap):
            col = 0
            while col < len(line):
                if line[col] == "1":
                    # merge consecutive pixels into one rectangle
                    start = col
                    while col < len(line) and line[col] == "1":
                        col += 1
                    screen.fill(
                        color,
                        (
                            cursor_x + start * scale,
                            y + row * scale,
                            (col - start) * scale,
                            scale,
                        ),
                    )
                else:
                    col += 1

        cursor_x += (len(bitmap[0]) + LETTER_SPACING) * scale


# ---------------------------------------------------------------------------
# Image helpers: only things that exist in MiniLibX
#
#   put_pixel    ->  mlx_pixel_put (or writing into the mlx_get_data_addr buffer)
#   load_image   ->  mlx_xpm_file_to_image + mlx_get_data_addr (read the pixels)
#   draw_image   ->  a double loop over the image, writing each pixel
# ---------------------------------------------------------------------------
def put_pixel(screen, x, y, color):
    """Same bounds check you must do yourself in C before writing a pixel."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        screen.set_at((x, y), color)


def load_image(path):
    """PNG file -> plain 2D list of (r, g, b, a). Done ONCE, never per frame."""
    surf = pygame.image.load(path)
    w, h = surf.get_size()
    pixels = [[tuple(surf.get_at((x, y))) for x in range(w)] for y in range(h)]
    return {"w": w, "h": h, "pixels": pixels}


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


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, color, callback, text, radius=25, text_scale=3):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.callback = callback
        self.text = text
        self.radius = radius
        self.text_scale = text_scale

    def draw(self, screen):
        draw_rounded_rect(
            screen, self.x, self.y, self.width, self.height, self.color, self.radius
        )

        tw = text_width(self.text, self.text_scale)
        th = text_height(self.text_scale)
        text_x = self.x + (self.width - tw) // 2
        text_y = self.y + (self.height - th) // 2
        draw_text(screen, text_x, text_y, self.text, (255, 255, 255), self.text_scale)

    def contains(self, mouse_x, mouse_y):
        return (
            self.x <= mouse_x <= self.x + self.width
            and self.y <= mouse_y <= self.y + self.height
        )

    def handle_click(self, mouse_x, mouse_y):
        if self.contains(mouse_x, mouse_y):
            self.callback()


def start_game():
    print("Starting game!")


def show_scores():
    print("Showing high scores!")


def instructions():
    print("instructions!")


def exit_game():
    print("Exiting game!")


if __name__ == "__main__":
    running = True

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")

    bx = (WIDTH - 400) // 2  # centre the buttons horizontally
    play_button = Button(bx, 330, 400, 90, (0, 255, 0), start_game, "Start")
    scores_button = Button(bx, 440, 400, 90, (0, 255, 0), show_scores, "High Scores")
    instructions_button = Button(bx, 550, 400, 90, (0, 255, 0), instructions, "Instructions")
    exit_button = Button(bx, 660, 400, 90, (0, 255, 0), exit_game, "Exit")

    buttons = [play_button, scores_button, instructions_button, exit_button]
    current_page = "menu"

    pacman_frames = build_pacman_frames(64)
    pacmans = make_background_pacmans(pacman_frames)
    tick = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    button.handle_click(*event.pos)

        screen.fill((0,0,60))
        if current_page == "menu":
            for pm in pacmans:          # background first, UI on top
                pm.update()
                pm.draw(screen, tick)
            draw_menu(screen, buttons)
        tick += 1

        pygame.display.flip()

    pygame.quit()