from .draw_tools import draw_rounded_rect
from .text_rendering import text_width, text_height, draw_text

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
            return self.callback()
