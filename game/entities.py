from enum import Enum
from typing import Tuple
from maze.maze import EAST, NORTH, SOUTH, WEST


class Direction(Enum):
    """A move direction: step on each axis and the wall bit it crosses."""

    UP = (0, -1, NORTH)
    RIGHT = (1, 0, EAST)
    DOWN = (0, 1, SOUTH)
    LEFT = (-1, 0, WEST)

    def __init__(self, dx: int, dy: int, wall: int) -> None:
        """Store the x step, the y step and the matching wall bit."""
        self.dx = dx
        self.dy = dy
        self.wall = wall


class Entity:   
    """Base class for the player and the ghosts: a cell and a facing."""

    def __init__(self, x: int, y: int, direction: Direction = Direction.LEFT) -> None:
        """Place the entity on cell (x, y), which is also its spawn cell."""
        self.x = x
        self.y = y
        self.direction = direction
        self._spawn = (x, y)

    @property
    def position(self) -> Tuple[int, int]:
        """Return the current cell as an (x, y) pair."""
        return self.x, self.y

    def respawn(self) -> None:
        """Put the entity back on its spawn cell."""
        self.x, self.y = self._spawn


class GhostState(Enum):
    """What a ghost is currently doing."""

    CHASE = "chase"
    EDIBLE = "edible"
    RESPAWNING = "respawning"


class Player(Entity):
    """The player: an entity with lives and a requested next move."""

    def __init__(self, x: int, y: int, lives: int) -> None:
        """Place the player on its spawn cell with the given lives."""
        super().__init__(x, y)
        self.lives = lives
        self.next_direction: Optional[Direction] = None


class Ghost(Entity):
    """A ghost: an entity with a name, a state and a respawn timer."""

    def __init__(self, x: int, y: int, name: str) -> None:
        """Place the ghost on its home corner, chasing."""
        super().__init__(x, y)
        self.name = name
        self.state = GhostState.CHASE
        self.respawn_timer = 0.0
