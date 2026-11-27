
from enum import Enum
from collections import deque
from typing import Any, Dict, List, Tuple, Optional
import time

from game.entities import Direction, Ghost, Player, GhostState
from game.level import Level
from maze.maze import Maze


MIN_LEVELS = 10
GHOST_NAMES = ("blinky", "pinky", "inky", "clyde")

PLAYER_MOVE_INTERVAL = 0.15
GHOST_MOVE_INTERVAL = 1
GHOST_EDIBLE_DURATION = 7.0
GHOST_RESPAWN_DURATION = 1.0


class GamePhase(Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class GameState:
    """The single source of truth for the entire gameplay simulation."""

    def __init__(self, config: Dict[str, Any], maze: Maze) -> None:
        self.config = config
        self.maze = maze

        self.total_levels = max(MIN_LEVELS, len(config["level"]))

        self.score = 0
        self.phase = GamePhase.PLAYING
        self.level_number = 1
        self.time_left = 0.0

        self.level: Level
        self.player: Player
        self.ghosts: List[Ghost]

        self._player_timer = 0.0
        self._edible_timer = 0.0
        self._last_update = time.monotonic()

        self.new_game()

    # ---------------------------------------------------------
    # GAME INITIALIZATION
    # ---------------------------------------------------------

    def new_game(self) -> None:
        self.score = 0
        self.phase = GamePhase.PLAYING
        self._start_level(1, self.config["lives"])

    def _size_for(self, number: int) -> Tuple[int, int]:
        sizes = self.config["level"]
        entry = sizes[min(number - 1, len(sizes) - 1)]

        return entry["width"], entry["height"]

    def _start_level(self, number: int, lives: int) -> None:

        width, height = self._size_for(number)

        seed = self.config["seed"] if number == 1 else 0

        self.level = Level(
            number,
            width,
            height,
            seed,
            self.config["pacgum"],
            self.config["level_max_time"]
        )

        self.maze = self.level.maze

        px, py = self.level.player_spawn

        self.player = Player(px, py, lives)

        self.ghosts = [
            Ghost(gx, gy, name)
            for (gx, gy), name in zip(
                self.level.ghost_spawns,
                GHOST_NAMES
            )
        ]

        for ghost in self.ghosts:
            ghost._move_timer = 0.0

        self.level_number = number
        self.time_left = float(self.level.time_limit)

        self._player_timer = 0.0
        self._edible_timer = 0.0
        self._last_update = time.monotonic()

    # ---------------------------------------------------------
    # PLAYER INPUT
    # ---------------------------------------------------------

    def set_direction(self, direction: Direction) -> None:
        if self.phase is GamePhase.PLAYING:
            self.player.next_direction = direction

    def toggle_pause(self) -> None:

        if self.phase is GamePhase.PLAYING:
            self.phase = GamePhase.PAUSED

        elif self.phase is GamePhase.PAUSED:
            self.phase = GamePhase.PLAYING
            self._last_update = time.monotonic()

    # ---------------------------------------------------------
    # MAIN UPDATE
    # ---------------------------------------------------------

    def update(self, delta_time: Optional[float] = None) -> None:
        """Update every gameplay system.

        Called continuously by the application loop.
        """

        if self.phase is not GamePhase.PLAYING:
            return

        now = time.monotonic()

        if delta_time is None:
            delta_time = now - self._last_update

        self._last_update = now

        # Prevent large updates after a lag spike.
        delta_time = min(max(delta_time, 0.0), 0.1)

        # 1. Update timer.
        self.time_left = max(0.0, self.time_left - delta_time)

        if self.time_left <= 0:
            self.phase = GamePhase.GAME_OVER
            return

        # 2. Update power-up timer.
        if self._edible_timer > 0:
            self._edible_timer = max(
                0.0,
                self._edible_timer - delta_time
            )

            if self._edible_timer == 0:
                for ghost in self.ghosts:
                    if ghost.state == GhostState.EDIBLE:
                        ghost.state = GhostState.CHASE

        # 3. Update player movement.
        self._player_timer += delta_time

        if self._player_timer >= PLAYER_MOVE_INTERVAL:
            self._player_timer -= PLAYER_MOVE_INTERVAL
            self._move_player()

        # 4. Detect collisions immediately after player movement.
        self._check_collisions()

        if self.phase is not GamePhase.PLAYING:
            return

        # 5. Collect pellets.
        self._collect_pellets()

        # 6. Update every ghost.
        for ghost in self.ghosts:
            self._update_ghost(ghost, delta_time)

        # 7. Detect collisions after ghost movement.
        self._check_collisions()

    # ---------------------------------------------------------
    # MOVEMENT HELPERS
    # ---------------------------------------------------------

    def _can_move(self, entity, direction: Direction) -> bool:

        nx = entity.x + direction.dx
        ny = entity.y + direction.dy

        return (
            self.maze.in_bounds(nx, ny)
            and self.maze.is_walkable(nx, ny)
            and not self.maze.has_wall(
                entity.x,
                entity.y,
                direction.wall
            )
        )

    def _move_player(self) -> None:

        player = self.player

        # First try the requested direction.
        if player.next_direction is not None:

            if self._can_move(player, player.next_direction):
                player.direction = player.next_direction

        # Continue moving in the current direction.
        if self._can_move(player, player.direction):

            player.x += player.direction.dx
            player.y += player.direction.dy

    # ---------------------------------------------------------
    # GHOST PATHFINDING
    # ---------------------------------------------------------

    def _get_valid_neighbors(self, x: int, y: int):

        directions = (
            Direction.UP,
            Direction.RIGHT,
            Direction.DOWN,
            Direction.LEFT
        )

        for direction in directions:

            nx = x + direction.dx
            ny = y + direction.dy

            if (
                self.maze.in_bounds(nx, ny)
                and self.maze.is_walkable(nx, ny)
                and not self.maze.has_wall(x, y, direction.wall)
            ):
                yield nx, ny, direction

    def _find_chase_direction(self, ghost):

        start = ghost.position
        target = self.player.position

        if start == target:
            return None

        queue = deque([start])

        first_direction = {
            start: None
        }

        while queue:

            x, y = queue.popleft()

            for nx, ny, direction in self._get_valid_neighbors(x, y):

                next_position = (nx, ny)

                if next_position in first_direction:
                    continue

                if (x, y) == start:
                    first_direction[next_position] = direction
                else:
                    first_direction[next_position] = (
                        first_direction[(x, y)]
                    )

                if next_position == target:
                    return first_direction[next_position]

                queue.append(next_position)

        return None

    # ---------------------------------------------------------
    # GHOST MOVEMENT
    # ---------------------------------------------------------

    def _update_ghost(self, ghost, delta_time):

        # A ghost that was eaten waits before returning.
        if ghost.state == GhostState.RESPAWNING:

            ghost.respawn_timer -= delta_time

            if ghost.respawn_timer <= 0:
                ghost.respawn()
                ghost.state = GhostState.CHASE
                ghost._move_timer = 0.0

            return

        ghost._move_timer += delta_time

        if ghost._move_timer < GHOST_MOVE_INTERVAL:
            return

        ghost._move_timer -= GHOST_MOVE_INTERVAL

        direction = self._find_chase_direction(ghost)

        if direction is None:
            return

        if not self._can_move(ghost, direction):
            return

        ghost.x += direction.dx
        ghost.y += direction.dy
        ghost.direction = direction

    # ---------------------------------------------------------
    # PELLET COLLECTION
    # ---------------------------------------------------------

    def _collect_pellets(self):

        position = self.player.position

        if position in self.level.pacgums:

            self.level.pacgums.remove(position)

            self.score += self.config["points_per_pacgum"]

        if position in self.level.super_pacgums:

            self.level.super_pacgums.remove(position)

            self.score += self.config["points_per_super_pacgum"]

            self._edible_timer = GHOST_EDIBLE_DURATION

            for ghost in self.ghosts:
                if ghost.state == GhostState.CHASE:
                    ghost.state = GhostState.EDIBLE

    # ---------------------------------------------------------
    # COLLISIONS AND LIVES
    # ---------------------------------------------------------

    def _check_collisions(self):

        for ghost in self.ghosts:

            # Same cell means collision.
            if ghost.position != self.player.position:
                continue

            if ghost.state == GhostState.EDIBLE:

                self.score += self.config["points_per_ghost"]

                ghost.state = GhostState.RESPAWNING
                ghost.respawn_timer = GHOST_RESPAWN_DURATION

                continue

            if ghost.state == GhostState.CHASE:

                self._lose_life()
                return

    def _lose_life(self):

        self.player.lives -= 1

        if self.player.lives <= 0:

            self.player.lives = 0
            self.phase = GamePhase.GAME_OVER

            return

        # Respawn Pac-Man.
        self.player.respawn()

        self.player.direction = Direction.LEFT
        self.player.next_direction = None

        # Reset ghosts.
        for ghost in self.ghosts:

            ghost.respawn()
            ghost.state = GhostState.CHASE
            ghost.respawn_timer = 0.0
            ghost._move_timer = 0.0

        self._player_timer = 0.0
        self._edible_timer = 0.0

    # ---------------------------------------------------------
    # LEVEL PROGRESSION
    # ---------------------------------------------------------

    def _check_level_completion(self):

        if self.level.pacgums or self.level.super_pacgums:
            return

        if self.level_number >= self.total_levels:

            self.phase = GamePhase.VICTORY
            return

        remaining_lives = self.player.lives

        self._start_level(
            self.level_number + 1,
            remaining_lives
        )

    # =========================================================
    # NEW GAMEPLAY SYSTEMS
    # =========================================================
    # The following systems are now controlled by GameState:
    #
    # 1. Ghost BFS pathfinding.
    # 2. Independent ghost movement timers.
    # 3. Player / ghost collision detection.
    # 4. Life deduction and player respawning.
    # 5. Ghost eating and respawning.
    # 6. Super-pellet power duration.
    # 7. Automatic game-over detection.
    # 8. Pellet collection and scoring.
    # 9. Automatic level progression.
    # 10. Centralized game timer.
    #
    # The rendering layer must never modify these systems.
    # =========================================================
