
"""Gameplay controller: events, state updates and rendering."""

import pygame

from game.entities import Direction
from game.game_state import GamePhase, GameState
from maze.maze import Maze
from maze.maze_loader import MazeError

from .game_view import GameView


FPS = 60
STEP_MS = 150
BACKGROUND = (0, 0, 0)

KEYS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}

def show_scores(input_json, screen):
    """Display the high-score leaderboard."""

    clock = pygame.time.Clock()
    scores = _load_scores(input_json)

    width, height = screen.get_size()

    title_font = pygame.font.SysFont("monospace", 48, bold=True)
    score_font = pygame.font.SysFont("monospace", 27, bold=True)
    info_font = pygame.font.SysFont("monospace", 18)

    running = True

    while running:
        event_result = _menu_screen_events()

        if event_result is False:
            return False

        if event_result is True:
            return True

        screen.fill(BACKGROUND)

        _draw_centered_text(
            screen, "HIGH SCORES", 75, title_font, (255, 220, 0)
        )

        if not scores:
            _draw_centered_text(
                screen, "NO SCORES YET", height // 2,
                score_font
            )
        else:
            # Display up to 10 entries.
            start_y = 160

            for index, entry in enumerate(scores[:10]):
                y = start_y + index * 42

                rank = f"{index + 1:>2}."
                name = f"{entry['name']:<10}"
                score = f"{entry['score']:>8}"

                line = f"{rank} {name} {score}"

                _draw_centered_text(
                    screen, line, y, score_font,
                    (255, 255, 255)
                )

        _draw_centered_text(
            screen,
            "PRESS ESC OR ENTER TO RETURN",
            height - 45,
            info_font,
            (150, 150, 150)
        )

        pygame.display.flip()
        clock.tick(FPS)

    return True


def instructions(input_json, screen):
    """Display the game instructions."""

    clock = pygame.time.Clock()

    width, height = screen.get_size()

    title_font = pygame.font.SysFont("monospace", 42, bold=True)
    text_font = pygame.font.SysFont("monospace", 23)
    info_font = pygame.font.SysFont("monospace", 18)

    instructions_list = [
        ("ARROW KEYS", "Move Pac-Man"),
        ("P", "Pause / Resume"),
        ("ESC", "Return to the main menu"),
        ("", ""),
        ("PAC-GUM", "Collect ordinary pellets to earn points"),
        ("SUPER GUM", "Collect special pellets for more points"),
        ("", ""),
        ("OBJECTIVE", "Collect all pellets to complete the level"),
        ("WARNING", "Avoid ghosts!"),
    ]

    while True:
        event_result = _menu_screen_events()

        if event_result is False:
            return False

        if event_result is True:
            return True

        screen.fill(BACKGROUND)

        _draw_centered_text(
            screen, "HOW TO PLAY", 65,
            title_font, (255, 220, 0)
        )

        start_y = 145
        line_height = 43

        for index, (key, description) in enumerate(instructions_list):
            y = start_y + index * line_height

            if not key:
                continue

            # Draw the key/action label.
            key_surface = text_font.render(
                key, True, (255, 220, 0)
            )

            screen.blit(
                key_surface,
                (width // 2 - 280, y)
            )

            # Draw its explanation.
            description_surface = text_font.render(
                description, True, (255, 255, 255)
            )

            screen.blit(
                description_surface,
                (width // 2 - 60, y)
            )

        _draw_centered_text(
            screen,
            "PRESS ESC OR ENTER TO RETURN",
            height - 45,
            info_font,
            (150, 150, 150)
        )

        pygame.display.flip()
        clock.tick(FPS)


def exit_game(input_json, screen):
    """Exit the application."""
    print("[game] Exiting Pac-Man...")
    return False



def _new_game_state(config):
    placeholder = Maze(1, 1, [[0]])
    return GameState(config, placeholder)


def update_game_state(game_state):
    """Perform exactly one gameplay update.

    This function is called at STEP_MS intervals, not every rendered frame.
    """

    if game_state.phase is not GamePhase.PLAYING:
        return

    # WORKAROUND for the existing GameState implementation.
    game_state.maze = game_state.level.maze

    # Let the peer's GameState handle the timer and player movement.
    game_state.update()

    # Collect ordinary pellets.
    player_position = game_state.player.position

    if player_position in game_state.level.pacgums:
        game_state.level.pacgums.remove(player_position)
        game_state.score += game_state.config["points_per_pacgum"]

    # Collect super pellets.
    if player_position in game_state.level.super_pacgums:
        game_state.level.super_pacgums.remove(player_position)
        game_state.score += game_state.config["points_per_super_pacgum"]

    # End the game if the time limit expires.
    if game_state.time_left <= 0:
        game_state.phase = GamePhase.GAME_OVER
        return

    # Move to the next level when all pellets have been collected.
    if not game_state.level.pacgums and not game_state.level.super_pacgums:
        if game_state.level_number >= game_state.total_levels:
            game_state.phase = GamePhase.VICTORY
            return

        next_level = game_state.level_number + 1

        # Preserve the player's remaining lives.
        remaining_lives = game_state.player.lives

        game_state._start_level(next_level, remaining_lives)

        # Synchronize the maze after generating the next level.
        game_state.maze = game_state.level.maze


def handle_game_event(event, game_state):
    """Translate a Pygame event into a GameState command.

    Returns:
        True: continue the gameplay loop.
        False: return to the menu or quit.
    """

    if event.type == pygame.QUIT:
        return False

    if event.type != pygame.KEYDOWN:
        return True

    # Escape always returns to the menu.
    if event.key == pygame.K_ESCAPE:
        return False

    # Any key after the game ends returns to the menu.
    if game_state.phase in (GamePhase.GAME_OVER, GamePhase.VICTORY):
        return False

    # Pause / resume.
    if event.key == pygame.K_p:
        game_state.toggle_pause()
        return True

    # Movement commands.
    direction = KEYS.get(event.key)

    if direction is not None:
        game_state.set_direction(direction)

    return True



def start_game(input_json, screen):
    """Run gameplay using one frame loop."""

    print("[game] Starting game...")

    try:
        game_state = _new_game_state(input_json)
    except MazeError as err:
        print(f"[game] Cannot start: {err}")
        return True

    view = GameView(game_state)
    clock = pygame.time.Clock()

    tick = 0
    running = True

    while running:

        # 1. EVENTS
        for event in pygame.event.get():

            running = handle_game_event(event, game_state)

            if not running:
                break

        if not running:
            break

        # 2. UPDATE
        delta_time = clock.tick(FPS) / 1000.0

        view.begin_step(game_state)

        # GameState controls EVERYTHING.
        game_state.update(delta_time)

        # 3. RENDER
        screen.fill(BACKGROUND)

        view.draw(
            screen,
            game_state,
            tick,
            1.0
        )

        pygame.display.flip()

        tick += 1

    return True

