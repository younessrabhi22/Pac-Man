from typing import List, Any, Dict
import pygame

from game.level import Level
from graphics.maze_drawing import build_maze_view, draw_maze
from game.config_loader import DataParsing

data_parser  = DataParsing()

#I added this initial levels

def initialize_levels(config: Dict[str, Any]) -> List[Level]:
    """Create all levels from the validated configuration."""

    levels: List[Level] = []

    for index, level_config in enumerate(config["level"]):

        level = Level(
            number=index + 1,
            width=level_config["width"],
            height=level_config["height"],
            seed=config["seed"] + index,
            pacgum_count=config["pacgum"],
            time_limit=config["level_max_time"]
        )

        levels.append(level)

    return levels



def start_game(input_json, screen):
    print("Starting game!")
    levels = initialize_levels(input_json)
    maze_view = build_maze_view(levels[0].maze, top_margin=80)
    running = True
    screen.fill((0, 0, 60))
    while running:
        draw_maze(screen, maze_view)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    return True

def show_scores(input_json, screen):
    print("Showing high scores!")
    return True

def instructions(input_json, screen):
    print("instructions!")
    return True

def exit_game(input_json, screen):
    print("Exiting game!")
    return False