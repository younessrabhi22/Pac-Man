
from typing import Dict, List, Any


DEFAULT_SIZE = 20
MIN_SIZE = 5
MAX_SIZE = 100


class DataParsing:

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
        if (isinstance(value, bool) or not isinstance(value, int)
                or not MIN_SIZE <= value <= MAX_SIZE):
            print(f"[config] level {index}: '{key}' invalid, "
                  f"using {DEFAULT_SIZE}")
            return DEFAULT_SIZE
        return value
