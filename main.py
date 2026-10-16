import sys
import json
from typing import Dict
from game.config_loader import data_parsing






if __name__   == "__main__":

    default_param: Dict = {}
    data: str = ""
    input_json: Dict = {}


    default_param["highscore_filename"] = "highscore.json"
    default_param["level"] =  [{"width": 28, "height": 31}]
    default_param["lives"] = 20
    default_param["pacgum"] = 42
    default_param["points_per_pacgum"] = 10
    default_param["points_per_super_pacgum"] = 50
    default_param["points_per_ghost"] = 200
    default_param["seed"] = 42
    default_param["level_max_time"] = 90


    if len(sys.argv) != 2:
        print("invalid argements number!")
        exit(1)

    try:
        with open(sys.argv[1], "r") as file:

            for line in file.readlines():
                if line.strip().startswith("#") or line.strip().startswith("//"):
                    continue
                data += line
    except FileNotFoundError:
        print("file not found")

    try:
        input_json = json.loads(data)
    except json.JSONDecodeError:
        print("invalid json")

    parser = data_parsing()

    if not input_json:
        parser.load_json(default_param)
    else:
        parser.load_json(input_json)
