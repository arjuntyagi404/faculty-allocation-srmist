import json
from pathlib import Path


CONFIG_DIR = Path(__file__).parent / "config"


def load_unified_timetable():

    file_path = CONFIG_DIR / "unified_timetable.json"

    with open(file_path, "r") as f:
        return json.load(f)