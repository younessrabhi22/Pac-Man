"""Draws one frame of the running game from a GameState (read only)."""

from typing import Dict, List, Tuple

import pygame

from game.game_state import GamePhase, GameState
from .draw_tools import HEIGHT, WIDTH, draw_image
from .hud import HUD_HEIGHT, draw_hud
from .maze_drawing import build_maze_view, draw_maze
from .sprites import build_ghost_sprites, build_pacman_sprites, build_pellet
from .text_rendering import draw_text, text_width

Cell = Tuple[int, int]

PELLET_COLOR = (255, 184, 174)
SUPER_COLOR = (255, 255, 255)
TITLE_COLOR = (254, 229, 20)
OVERLAYS: Dict[GamePhase, Tuple[str, str]] = {
    GamePhase.PAUSED: ("PAUSED", "P TO RESUME"),
    GamePhase.GAME_OVER: ("GAME OVER", "PRESS ANY KEY"),
    GamePhase.VICTORY: ("VICTORY", "PRESS ANY KEY"),
}


class GameView:
    """Everything graphical about a game: maze image, sprites, animation."""

    def __init__(self, game_state: GameState) -> None:
        self._bind(game_state)

    def _bind(self, game_state: GameState) -> None:
        """(Re)build the maze image and sprites for the current level."""
        self.level = game_state.level
        self.maze_view = build_maze_view(self.level.maze, HUD_HEIGHT)
        cell, wall = self.maze_view.cell, self.maze_view.wall
        size = max(6, cell - 2 * wall)
        self.pacman = build_pacman_sprites(size)
        self.ghosts = build_ghost_sprites(size)
        self.pellet = build_pellet(max(2, cell // 10), PELLET_COLOR)
        self.super_pellet = build_pellet(max(3, cell // 4), SUPER_COLOR)
        self.begin_step(game_state)

    def begin_step(self, game_state: GameState) -> None:
        """Call just BEFORE game_state.update(): remember where everyone was."""
        self.prev_player: Cell = game_state.player.position
        self.prev_ghosts: List[Cell] = [g.position for g in game_state.ghosts]

    # ---- helpers ----------------------------------------------------------

    def _between(self, prev: Cell, curr: Cell, t: float) -> Tuple[int, int]:
        """Pixel position t (0..1) of the way from cell prev to cell curr."""
        x0, y0 = self.maze_view.cell_center(*prev)
        x1, y1 = self.maze_view.cell_center(*curr)
        return int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)

    @staticmethod
    def _blit_centered(screen: pygame.Surface, sprite: dict,
                       cx: int, cy: int) -> None:
        draw_image(screen, sprite, cx - sprite["w"] // 2,
                   cy - sprite["h"] // 2)

    # ---- drawing ----------------------------------------------------------

    def draw(self, screen: pygame.Surface, game_state: GameState,
             tick: int, progress: float) -> None:
        """Draw the whole frame, back to front."""
        if game_state.level is not self.level:       # a new level started
            self._bind(game_state)
        draw_maze(screen, self.maze_view)
        self._draw_pellets(screen, game_state, tick)
        self._draw_ghosts(screen, game_state, progress)
        self._draw_player(screen, game_state, tick, progress)
        draw_hud(screen, game_state)
        self._draw_overlay(screen, game_state)

    def _draw_pellets(self, screen, game_state, tick) -> None:
        for cell in game_state.level.pacgums:
            cx, cy = self.maze_view.cell_center(*cell)
            self._blit_centered(screen, self.pellet, cx, cy)
        if (tick // 20) % 2 == 0:                    # super pellets blink
            for cell in game_state.level.super_pacgums:
                cx, cy = self.maze_view.cell_center(*cell)
                self._blit_centered(screen, self.super_pellet, cx, cy)

    def _draw_ghosts(self, screen, game_state, progress) -> None:
        for ghost, prev in zip(game_state.ghosts, self.prev_ghosts):
            sprite = self.ghosts[ghost.name][ghost.state]
            cx, cy = self._between(prev, ghost.position, progress)
            self._blit_centered(screen, sprite, cx, cy)

    def _draw_player(self, screen, game_state, tick, progress) -> None:
        player = game_state.player
        frame = self.pacman[player.direction][(tick // 6) % 2]
        cx, cy = self._between(self.prev_player, player.position, progress)
        self._blit_centered(screen, frame, cx, cy)

    def _draw_overlay(self, screen, game_state) -> None:
        texts = OVERLAYS.get(game_state.phase)
        if texts is None:
            return
        title, hint = texts
        mid = HEIGHT // 2
        screen.fill((0, 0, 0), (0, mid - 100, WIDTH, 170))
        for text, y, scale in ((title, mid - 80, 8), (hint, mid + 20, 3)):
            x = (WIDTH - text_width(text, scale)) // 2
            draw_text(screen, x, y, text, TITLE_COLOR, scale)