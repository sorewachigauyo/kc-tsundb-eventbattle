import json
import pathlib


import numpy as np

data_folder = pathlib.Path(__file__).parent

def load_json(filepath: str):
    """Shortcut for loading a JSON
    """
    with open(filepath, encoding="utf-8") as r:
        return json.load(r)

def search_item_in_array_exists(array, item):
    for idx, val in np.ndenumerate(array):
        if val == item:
            return idx
    return None
