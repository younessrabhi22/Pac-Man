import pygame

pygame.init()

WIDTH = 1700
HEIGHT = 900

def draw_rect(screen, x, y, width, height, color):
    for i in range(height):
        for j in range(width):
            screen.set_at((x + j, y + i), color)



FONT = {
    'P': [
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000"
    ],
    'A': [
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001"
    ],
    'C': [
        "01111",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "01111"
    ],
    'M': [
        "10001",
        "11011",
        "10101",
        "10101",
        "10001",
        "10001",
        "10001"
    ],
    'N': [
        "10001",
        "11001",
        "10101",
        "10011",
        "10001",
        "10001",
        "10001"
    ],
    '-': [
        "00000",
        "00000",
        "00000",
        "11111",
        "00000",
        "00000",
        "00000"
    ]
}


def draw_text(screen, text, x, y, scale, color):
    cursor_x = x

    for char in text:
        if char not in FONT:
            cursor_x += 6 * scale
            continue

        bitmap = FONT[char]

        for row in range(len(bitmap)):
            for col in range(len(bitmap[row])):
                if bitmap[row][col] == '1':
                    draw_rect(
                        screen,
                        cursor_x + col * scale,
                        y + row * scale,
                        scale,
                        scale,
                        color
                    )

        cursor_x += 6 * scale







def draw_menu(screen):
    title = "PAC-MAN"
    scale= 15
    title_width = len(title) * 6 * scale - scale
    x = (1700 - title_width) // 2
    y = 40

    draw_text(screen, title, x, y, scale, (255, 255, 255))


    draw_rect(screen,700,360,250,70, (255, 255, 0))
    draw_rect(screen, 700, 460, 250, 70, (255, 255, 0))
    draw_rect(screen, 700, 560, 250, 70, (255, 255, 0))

    pygame.display.flip()

if __name__ == "__main__":
    running=True

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    current_page = "menu"
    while running:
        screen.fill((25,25,166))
        if current_page == "menu":
            draw_menu(screen)



            pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False





