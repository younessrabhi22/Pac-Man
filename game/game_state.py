from enum import Enum
from typing import Any, Dict, List, Tuple
from game.entities import Direction, Ghost, Player
from game.level import Level
import time
from maze.maze import Maze

MIN_LEVELS = 10
GHOST_NAMES = ("blinky", "pinky", "inky", "clyde")


class GamePhase(Enum):
    """Where the game currently is."""

    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class GameState:
    """Everything about a running game; the UI reads it, never edits it."""

    def __init__(self, config: Dict[str, Any], maze: Maze) -> None:
        """Start a new game from a validated config.

        Args:
            config: the dict returned by the config parser.
        """
        self.maze = maze
        self.config = config
        self.total_levels = max(MIN_LEVELS, len(config["level"]))
        self.score = 0
        self.phase = GamePhase.PLAYING
        self.level_number = 1
        self.time_left = 0.0
        self.level: Level
        self.player: Player
        self.ghosts: List[Ghost]
        self.new_game()

    def new_game(self) -> None:
        """Reset the score and lives and start level 1."""
        self.score = 0
        self.phase = GamePhase.PLAYING
        self._start_level(1, self.config["lives"])

    def set_direction(self, direction: Direction) -> None:
        """Remember the direction the player asked for (UI command)."""
        if self.phase is GamePhase.PLAYING:
            self.player.next_direction = direction

    def toggle_pause(self) -> None:
        """Pause a running game, or resume a paused one (UI command)."""
        if self.phase is GamePhase.PLAYING:
            self.phase = GamePhase.PAUSED
            self.paused_at = time.monotonic()

        elif self.phase is GamePhase.PAUSED:
            self.phase = GamePhase.PLAYING
            self.start_time += time.monotonic() - self.paused_at
            self.paused_at = 0.0


    def update(self) -> None:
        if self.phase is not GamePhase.PLAYING:
                    return
        
        elapsed = time.monotonic() - self.start_time
        self.time_left = max(0.0, self.level.time_limit - elapsed)

        self._move_player()

    

    def _size_for(self, number: int) -> Tuple[int, int]:
        """Return (width, height) of a level; the last size is repeated."""
        sizes = self.config["level"]
        entry = sizes[min(number - 1, len(sizes) - 1)]
        return entry["width"], entry["height"]

    def _start_level(self, number: int, lives: int) -> None:
        """Build level `number` and place the player and the ghosts."""

        self.start_time = time.monotonic()
        self.paused_at: float = 0.0

        width, height = self._size_for(number)
        seed = self.config["seed"] if number == 1 else 0

        self.level = Level(number, width, height, seed, self.config["pacgum"], self.config["level_max_time"])
        px, py = self.level.player_spawn

        self.player = Player(px, py, lives)
        self.ghosts = [Ghost(gx, gy, name) for (gx, gy), name in zip(self.level.ghost_spawns, GHOST_NAMES)]
                       
        self.level_number = number
        self.time_left = float(self.level.time_limit)


    def _move_player(self) -> None:
        x = self.player.x
        y = self.player.y

        if self.player.next_direction is not None:
            nx = x + self.player.next_direction.dx
            ny = y + self.player.next_direction.dy
            if (
                not self.maze.has_wall(x, y, self.player.next_direction.wall)
                and self.maze.in_bounds(nx, ny)
            ):
                self.player.direction = self.player.next_direction

        if self.player.direction is not None:
            nx = x + self.player.direction.dx
            ny = y + self.player.direction.dy
            if (
                not self.maze.has_wall(x, y, self.player.direction.wall)
                and self.maze.in_bounds(nx, ny)
            ):
                self.player.x = nx
                self.player.y = ny