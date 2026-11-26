from typing import Dict, Any, List

from game.level import Level

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


config = {'highscore_filename': 'highscore.json', 'level': [{'width': 90, 'height': 50}, {'width': 30, 'height': 35}], 'lives': 5, 'pacgum': 42, 'points_per_pacgum': 10, 'points_per_super_pacgum': 50, 'points_per_ghost': 200, 'seed': 42, 'level_max_time': 90}
my_levels = initialize_levels(config)


print(my_levels[0].maze.width)