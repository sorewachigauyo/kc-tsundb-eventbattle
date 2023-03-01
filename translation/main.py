import pathlib


from data.utils import load_json

TL_FILEPATH = pathlib.Path(__file__).parent / "idTL.json"
TL_JP = "jp"
TL_EN = "en"

raw = load_json(TL_FILEPATH)

def fetch_ship_translation(ship_id: int, lang=TL_EN) -> str:
    return raw["ships"][str(ship_id)][lang]

def fetch_equip_translation(equip_id: int, lang=TL_EN) -> str:
    return raw["equip"][str(equip_id)][lang]
