
from collections import deque
from game.tempurary_used import update_ghost
from game.entities import Direction, GhostState


# How long a ghost waits before moving to the next tile.
GHOST_MOVE_INTERVAL = 0.25


def get_valid_neighbors(maze, x, y):
    """Return all neighboring cells the ghost can legally enter."""

    directions = [
        Direction.UP,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.LEFT,
    ]

    neighbors = []

    for direction in directions:
        nx = x + direction.dx
        ny = y + direction.dy

        if not maze.in_bounds(nx, ny):
            continue

        if not maze.is_walkable(nx, ny):
            continue

        # Check that there is no wall between the current cell
        # and the neighboring cell.
        if maze.has_wall(x, y, direction.wall):
            continue

        neighbors.append((nx, ny, direction))

    return neighbors


def find_chase_direction(maze, ghost, player):
    """
    Use BFS to find the shortest path from a ghost to Pac-Man.

    Returns the first Direction the ghost should take.
    Returns None if no path exists.
    """

    start = ghost.position
    target = player.position

    if start == target:
        return None

    queue = deque([start])

    # Store the first direction to take from the starting position.
    first_direction = {start: None}

    while queue:
        x, y = queue.popleft()

        for nx, ny, direction in get_valid_neighbors(maze, x, y):
            next_position = (nx, ny)

            if next_position in first_direction:
                continue

            # If this is the first step, remember its direction.
            if (x, y) == start:
                first_direction[next_position] = direction
            else:
                first_direction[next_position] = first_direction[(x, y)]

            if next_position == target:
                return first_direction[next_position]

            queue.append(next_position)

    return None


def update_ghost(maze, ghost, player, delta_time):
    """
    Update one ghost.

    The ghost moves one tile every GHOST_MOVE_INTERVAL seconds.
    """

    if ghost.state != GhostState.CHASE:
        return

    # Each ghost has its own movement timer.
    if not hasattr(ghost, "_move_timer"):
        ghost._move_timer = 0.0

    ghost._move_timer += delta_time

    if ghost._move_timer < GHOST_MOVE_INTERVAL:
        return

    # Keep any extra accumulated time for consistent movement.
    ghost._move_timer -= GHOST_MOVE_INTERVAL

    direction = find_chase_direction(maze, ghost, player)

    if direction is None:
        return

    nx = ghost.x + direction.dx
    ny = ghost.y + direction.dy

    # Final safety check before moving.
    if (
        maze.in_bounds(nx, ny)
        and maze.is_walkable(nx, ny)
        and not maze.has_wall(ghost.x, ghost.y, direction.wall)
    ):
        ghost.x = nx
        ghost.y = ny
        ghost.direction = direction
