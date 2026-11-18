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
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font.json")


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


def draw_menu(screen, buttons):
    title = "PAC-MAN"
    scale = 12
    x = (WIDTH - text_width(title, scale)) // 2
    draw_text(screen, x, 70, title, (254, 229, 0), scale)

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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    button.handle_click(*event.pos)

        screen.fill((25, 25, 166))
        if current_page == "menu":
            draw_menu(screen, buttons)

        pygame.display.flip()

    pygame.quit()