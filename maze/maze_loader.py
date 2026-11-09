from maze.mazegenerator import MazeGenerator
from maze.maze import Maze, MazeError

PERFECT = False

def load_maze(width: int, height: int, seed: int = 0) -> Maze:
    """Generate a maze with the assigned package and convert it.

    Args:
        width: number of columns.
        height: number of rows.
        seed: above 0 gives a fixed maze, 0 gives a random one.

    Returns:
        A validated Maze.

    Raises:
        MazeError: if the generator fails or returns an invalid grid.
    """
    try:
        generator = MazeGenerator(size=(width, height), perfect=PERFECT,
                                  seed=seed)
        grid = generator.maze
    except Exception as err:
        raise MazeError(f"maze generation failed: {err}") from err
    return Maze.from_grid(grid, width, height)
