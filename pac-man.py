import sys
import json
from typing import Dict
from game.config_loader import DataParsing


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
    from graphics.movement import build_pacman_frames, make_background_pacmans, draw_menu
    import pygame
    from graphics.constants import WIDTH, HEIGHT, BUTTONS


    pygame.init()
    FPS=60
    pacman_frames = build_pacman_frames(64)  #build_pac_game add it to graphics


    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()


    pacmans = make_background_pacmans(pacman_frames, 10)

    state = {"running" : True,
            "current_page" : "menu"
             }
    tick = 0

    while state["running"]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["running"] = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in BUTTONS:
                    state["running"]=button.handle_click(*event.pos, input_json, screen)

        screen.fill((0,0,60))
        if state["current_page"] == "menu":
            for pm in pacmans:          # background first, UI on top
                pm.update()
                pm.draw(screen, tick)
            draw_menu(screen, BUTTONS)
        tick += 1
        pygame.display.flip()

    pygame.quit()
    sys.exit()
