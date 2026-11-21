from .schemas import Button
from .game_sections import start_game,show_scores, instructions, exit_game

WIDTH = 1700
HEIGHT = 900

bx = (WIDTH - 400) // 2  # centre the buttons horizontally
play_button = Button(bx, 330, 400, 90, (0, 255, 0), start_game, "Start")
scores_button = Button(bx, 440, 400, 90, (0, 255, 0), show_scores, "High Scores")
instructions_button = Button(bx, 550, 400, 90, (0, 255, 0), instructions, "Instructions")
exit_button = Button(bx, 660, 400, 90, (0, 255, 0), exit_game, "Exit")

BUTTONS = [play_button, scores_button, instructions_button, exit_button]
