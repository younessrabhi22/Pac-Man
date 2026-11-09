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
