import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "font.json")

def load_font(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

_font_data = load_font(FONT_PATH)
FONT = _font_data["glyphs"]
GLYPH_HEIGHT = _font_data["height"]
LETTER_SPACING = _font_data["letter_spacing"]
SPACE_WIDTH = _font_data["space_width"]



def load_font(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
