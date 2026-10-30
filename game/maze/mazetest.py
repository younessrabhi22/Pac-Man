import matplotlib.pyplot as plt
import random

from maze_loader import MazeGenerator


def display_maze(maze_generator):
    maze = maze_generator.maze

    height = len(maze)
    width = len(maze[0])

    fig, ax = plt.subplots(figsize=(10, 10))

    # Draw maze walls
    for y in range(height):
        for x in range(width):

            cell = maze[y][x]

            # North wall
            if cell & 1:
                ax.plot([x, x + 1], [height - y, height - y],
                        color="black", linewidth=2)

            # East wall
            if cell & 2:
                ax.plot([x + 1, x + 1], [height - y, height - y - 1],
                        color="black", linewidth=2)

            # South wall
            if cell & 4:
                ax.plot([x, x + 1], [height - y - 1, height - y - 1],
                        color="black", linewidth=2)

            # West wall
            if cell & 8:
                ax.plot([x, x], [height - y, height - y - 1],
                        color="black", linewidth=2)

            # Highlight the 42 pattern
            if cell == 15:
                ax.add_patch(plt.Rectangle(
                    (x, height - y - 1),
                    1, 1,
                    color="lightblue"
                ))

    # Entry and exit
    entry_x, entry_y = maze_generator.maze_entry
    exit_x, exit_y = maze_generator.maze_exit

    ax.text(entry_x + 0.5, height - entry_y - 0.5,
            "S", color="green", fontsize=12,
            ha="center", va="center", fontweight="bold")

    ax.text(exit_x + 0.5, height - exit_y - 0.5,
            "E", color="red", fontsize=12,
            ha="center", va="center", fontweight="bold")

    ax.set_aspect("equal")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    plt.title("Random Maze Generator")
    plt.show()


if __name__ == "__main__":

    maze_generator = MazeGenerator(
        size=(25, 25),
        perfect=False,
        entry_cell=(0, 0),
        exit_cell=(-1, -1),
        seed=100
    )   
    maze = maze_generator.maze
    # print("Entry:", maze_generator.maze_entry)
    # print("Exit:", maze_generator.maze_exit)
    # print("Shortest path:", maze_generator.shortest_path)
    print(maze)
