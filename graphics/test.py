import pygame

def load_image(path):
    """PNG file -> plain 2D list of (r, g, b, a). Done ONCE, never per frame."""
    surf = pygame.image.load(path)
    w, h = surf.get_size()
    pixels = [[tuple(surf.get_at((x, y))) for x in range(w)] for y in range(h)]
    return {"w": w, "h": h, "pixels": pixels}

load_image("/home/achahi/Desktop/pacwork/graphics/images/pacman_open.png")