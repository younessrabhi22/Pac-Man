
from typing import Dict, List, Any


DEFAULT_SIZE = 20
MIN_SIZE = 5
MAX_SIZE = 100


class DataParsing:

    def parse_config(self, input_json: Dict[str, Any], default_para: Dict[str, Any]) -> Dict[str, Any]:

        validated_levels = self.parse_level(input_json, default_para)

        clean_config = {
            "highscore_filename": self.parse_string(input_json, default_para, "highscore_filename"),
            "level": validated_levels,

            "lives": self.parse_int(input_json, default_para, "lives", 1, 10),
            "pacgum": self.parse_int(input_json, default_para, "pacgum", 10, 100),
            "points_per_pacgum": self.parse_int(input_json, default_para, "points_per_pacgum", 1, 100),
            "points_per_super_pacgum": self.parse_int(input_json, default_para, "points_per_super_pacgum", 10, 500),
            "points_per_ghost": self.parse_int(input_json, default_para, "points_per_ghost", 50, 1000),
            "seed": self.parse_int(input_json, default_para, "seed", 0, 99999),
            "level_max_time": self.parse_int(input_json, default_para, "level_max_time", 30, 600)
        }
        return clean_config


    def parse_level(self, input_json: Dict, default_para: Dict) -> List:

        levels = input_json.get("level")

        if not isinstance(levels, list) or not levels:
            print("[config] 'level' missing or invalid, using default")
            return default_para["level"]

        result: List[Dict] = []

        for index, item in enumerate(levels):
            if not isinstance(item, dict):
                print(f"[config] level {index} is not an object, skipped")
                continue

            result.append({
                "width": self.parse_dimension(item, "width", index),
                "height": self.parse_dimension(item, "height", index),
            })

        if not result:
            print("[config] no valid level, using default")
            return default_para["level"]

        return result

    def parse_dimension(self, item: Dict[str, Any], key: str,
                        index: int) -> int:

        value = item.get(key)
        if (not isinstance(value, int)
                or not MIN_SIZE <= value <= MAX_SIZE):
            print(f"[config] level {index}: '{key}' invalid, "
                  f"using {DEFAULT_SIZE}")
            return DEFAULT_SIZE
        return value

    def parse_int(self, input_json: Dict[str, Any], default_para: Dict[str, Any],
              key: str, min_val: int, max_val: int) -> int:
        """Validate one integer parameter, or return its default."""
        default = default_para[key]
        value = input_json.get(key)
        if (isinstance(value, bool) or not isinstance(value, int)
                or not min_val <= value <= max_val):
            print(f"[config] '{key}' missing or invalid, using {default}")
            return default
        return value

    def parse_string(self, input_json: Dict[str, Any], default_para: Dict[str, Any], key: str) -> str:
        """Validate one string parameter, ensuring it is a non-empty string."""
        default = default_para[key]
        value = input_json.get(key)

        if not isinstance(value, str) or not value.strip():
            print(f"[config] '{key}' missing or invalid, using '{default}'")
            return default

        return value
