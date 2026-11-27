import sys
import json
from typing import Dict
from game.config_loader import DataParsing



def get_arrow_direction(event):

    if event.type != pygame.KEYDOWN:
        return None

    directions = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }

    return directions.get(event.key)

if __name__   == "__main__":

    default_param: Dict = {}
    data: str = ""
    input_json: Dict = {}


    default_param["highscore_filename"] = "highscore.json"
    default_param["level"] =  [{"width": 40, "height": 40}]
    default_param["lives"] = 3
    default_param["pacgum"] = 42
    default_param["points_per_pacgum"] = 10
    default_param["points_per_super_pacgum"] = 50
    default_param["points_per_ghost"] = 200
    default_param["seed"] = 42
    default_param["level_max_time"] = 90


    if len(sys.argv) != 2:
        print("\n[Config] Error: Invalid argument number!"
        f"Usage: python3 pac-man.py config.json")
        exit(1)

    try:
        with open(sys.argv[1], "r") as file:
            for line in file.readlines():
                if line.strip().startswith("#") or line.strip().startswith("//"):
                    continue
                data += line

        if data.strip():
            input_json = json.loads(data)

    except FileNotFoundError:
        print("\n[Config] Warning: Configuration file not found."
        f" Loading safe default parameters.")
    except json.JSONDecodeError:
        print("\n[Config] Warning: Invalid JSON format."
        f"Loading safe default parameters.")


    parser = DataParsing()
    input_json = parser.parse_config(input_json, default_param)
    print(input_json)


####################################################################################################################
    #game loop

    # ---------------------------------------------------------
    # APPLICATION / MENU
    # ---------------------------------------------------------
    import pygame
    from graphics.movement import (
        build_pacman_frames,
        make_background_pacmans,
        draw_menu
    )
    from graphics.constants import WIDTH, HEIGHT, BUTTONS
    from enum import Enum, auto
    from graphics.game_sections import _new_game_state , GameView, GamePhase, handle_game_event, BACKGROUND

    class AppScreen(Enum):
        MENU = auto()
        GAME = auto()
        SCORES = auto()
        INSTRUCTIONS = auto()

    pygame.init()

    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()

    pacman_frames = build_pacman_frames(64)
    pacmans = make_background_pacmans(pacman_frames, 10)

    running = True
    tick = 0

    current_screen = AppScreen.MENU

    while running:

        delta_time = clock.tick(FPS) / 1000.0

        # 1. EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                break

            if current_screen == AppScreen.GAME:
                running = handle_game_event(event, game_state)

                if not running:
                    current_screen = AppScreen.MENU
                    running = True

            elif current_screen == AppScreen.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    for button in BUTTONS:
                        if button.contains(*event.pos):

                            if button.text == "Start":
                                game_state = _new_game_state(input_json)
                                game_view = GameView(game_state)
                                current_screen = AppScreen.GAME

                            elif button.text == "High Scores":
                                current_screen = AppScreen.SCORES

                            elif button.text == "Instructions":
                                current_screen = AppScreen.INSTRUCTIONS

                            elif button.text == "Exit":
                                running = False

                            break

            elif current_screen in (AppScreen.SCORES, AppScreen.INSTRUCTIONS):
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        current_screen = AppScreen.MENU

        if not running:
            break

        # 2. UPDATE
        if current_screen == AppScreen.GAME:
            if game_state.phase == GamePhase.PLAYING:
                game_view.begin_step(game_state)
                game_state.update(delta_time)

        # 3. DRAW
        if current_screen == AppScreen.GAME:
            screen.fill(BACKGROUND)
            game_view.draw(screen, game_state, tick, 1.0)

        elif current_screen == AppScreen.MENU:
            screen.fill((0, 0, 60))

            for pacman in pacmans:
                pacman.update()
                pacman.draw(screen, tick)

            draw_menu(screen, BUTTONS)

        elif current_screen == AppScreen.SCORES:
            draw_scores_screen(screen, input_json)

        elif current_screen == AppScreen.INSTRUCTIONS:
            draw_instructions_screen(screen)

        pygame.display.flip()
        tick += 1

    pygame.quit()
    sys.exit()