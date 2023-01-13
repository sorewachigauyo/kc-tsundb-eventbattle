import json
import pathlib

data_folder = pathlib.Path(__file__).parent

def load_json(filepath: str):
    """Shortcut for loading a JSON
    """
    with open(filepath, encoding="utf-8") as r:
        return json.load(r)
