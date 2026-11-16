import pygame

pygame.init()

WIDTH = 1700
HEIGHT = 900

def draw_rect(screen, x, y, width, height, color):
    for i in range(height):
        for j in range(width):
            screen.set_at((x + j, y + i), color)


GLYPH_HEIGHT = 10
LETTER_SPACING = 2   # blank columns between glyphs
SPACE_WIDTH = 5      # width of a ' ' in columns

FONT = {
    "P": [
        "0111100",
        "1111110",
        "1100110",
        "1100110",
        "1111110",
        "1111100",
        "1100000",
        "1100000",
        "1100000",
        "1100000",
    ],
    "A": [
        "0011100",
        "0111110",
        "1110111",
        "1100011",
        "1100011",
        "1111111",
        "1111111",
        "1100011",
        "1100011",
        "1100011",
    ],
    "C": [
        "0111110",
        "1111111",
        "1100011",
        "1100000",
        "1100000",
        "1100000",
        "1100000",
        "1100011",
        "1111111",
        "0111110",
    ],
    "M": [
        "11000011",
        "11100111",
        "11111111",
        "11111111",
        "11011011",
        "11011011",
        "11000011",
        "11000011",
        "11000011",
        "11000011",
    ],
    "N": [
        "11000011",
        "11100011",
        "11110011",
        "11111011",
        "11011111",
        "11001111",
        "11000111",
        "11000011",
        "11000011",
        "11000011",
    ],
    "-": [
        "0000000",
        "0000000",
        "0000000",
        "0000000",
        "0111110",
        "0111110",
        "0000000",
        "0000000",
        "0000000",
        "0000000",
    ],
}


def glyph_width(char):
    """Width of a glyph in columns (SPACE_WIDTH for spaces/unknown chars)."""
    bitmap = FONT.get(char)
    return len(bitmap[0]) if bitmap else SPACE_WIDTH


def text_width(text, scale=1):
    """Total pixel width of a string (useful for centering/right-aligning)."""
    if not text:
        return 0
    columns = sum(glyph_width(c) for c in text) + LETTER_SPACING * (len(text) - 1)
    return columns * scale

def draw_text (screen, x, y, text, color, scale=3):
    cursor_x = x

    for char in text:
        draw_char(screen, cursor_x, y, char, color, scale)
        cursor_x += 6 * scale


def draw_title(screen, text, x, y, scale, color):
    cursor_x = x
    line_height = (GLYPH_HEIGHT + LETTER_SPACING) * scale

    for char in text:
        if char == "\n":
            cursor_x = x
            y += line_height
            continue

        bitmap = FONT.get(char) or FONT.get(char.upper())
        if bitmap is None:
            # Space or unsupported character
            cursor_x += (SPACE_WIDTH + LETTER_SPACING) * scale
            continue

        for row, line in enumerate(bitmap):
            col = 0
            while col < len(line):
                if line[col] == "1":
                    # Merge consecutive '1's into a single rectangle (fewer draw calls)
                    start = col
                    while col < len(line) and line[col] == "1":
                        col += 1
                    draw_rect(
                        screen,
                        cursor_x + start * scale,
                        y + row * scale,
                        (col - start) * scale,
                        scale,
                        color,
                    )
                else:
                    col += 1

        cursor_x += (len(bitmap[0]) + LETTER_SPACING) * scale

def draw_char(screen, x, y, char, color, scale=3):
    bitmap = FONT.get(char.upper())

    if not bitmap:
        return

    for row, line in enumerate(bitmap):
        for col, pixel in enumerate(line):
            if pixel == "1":
                draw_rect(
                    screen,
                    x + col * scale,
                    y + row * scale,
                    scale,
                    scale,
                    color
                )



def draw_menu(screen, buttons):
    title = "PAC-MAN"
    scale= 12
    title_width = len(title) * 6 * scale - scale
    x = (1400 - title_width) // 2
    y = 70

    draw_title(screen, title, x, y, scale, (255, 255, 255))
    for button in buttons:
        button.draw(screen)



class Button:
    def __init__(self, x, y, width, height, color, callback, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.callback = callback
        self.text = text

    def draw(self, screen):
        draw_rect(
            screen,
            self.x,
            self.y,
            self.width,
            self.height,
            self.color,
        )

        text_width = len(self.text) * 4 * 2
        text_height = 4 * 2

        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - text_height) // 2
        draw_text(
            screen,
            text_x,
            text_y,
            self.text,
            (255, 255, 255),
            3
        )


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

    running=True

    play_button = Button(700, 360, 250, 70, (0, 255, 0), start_game, "Start")
    scores_button = Button(700, 450, 250, 70, (0, 255, 0), show_scores, "High Scores")
    exit_button = Button(700, 630, 250, 70, (0, 255, 0), exit_game, "Exit")
    instructions_button = Button(700,540, 250, 70, (0, 255, 0), instructions, "Instructions")

    buttons = [play_button, scores_button, instructions_button, exit_button]
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    current_page = "menu"

    while running:
        screen.fill((25,25,166))
        if current_page == "menu":
            draw_menu(screen, buttons)
            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        button.handle_click(*event.pos)
        pygame.display.flip()




