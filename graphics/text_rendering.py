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


def _draw_centered_text(screen, text, y, font, color=(255, 255, 255)):
    """Draw text horizontally centered on the screen."""
    surface = font.render(str(text), True, color)
    rect = surface.get_rect(center=(screen.get_width() // 2, y))
    screen.blit(surface, rect)


def _load_scores(input_json):
    """Load and sort saved high scores."""
    filename = input_json.get("highscore_filename", "highscore.json")

    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = data.get("scores", data.get("high_scores", []))

        if not isinstance(data, list):
            return []

        scores = []

        for entry in data:
            if not isinstance(entry, dict):
                continue

            try:
                scores.append({
                    "name": str(entry.get("name", "PLAYER"))[:10],
                    "score": int(entry.get("score", 0))
                })
            except (ValueError, TypeError):
                continue

        return sorted(scores, key=lambda item: item["score"], reverse=True)

    except (OSError, json.JSONDecodeError):
        return []


def _menu_screen_events():
    """
    Handle events for secondary menu screens.

    Returns False when the application should quit.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True

    return None