import requests
import json


from data.static import SHIP_MASTER_FILENAME, EQUIP_MASTER_FILENAME, WCTF_DB_FILENAME
from data.utils import data_folder

filenames = [SHIP_MASTER_FILENAME, EQUIP_MASTER_FILENAME]

for fn in filenames:
    r = requests.get(f"https://raw.githubusercontent.com/Tibowl/api_start2/master/parsed/{fn}")
    with open(data_folder / fn, "wb+") as w:
        w.write(r.content)

# WCTF
wctf_db = {}
r = requests.get("https://raw.githubusercontent.com/KC3Kai/KC3Kai/master/src/data/WhoCallsTheFleet_ships.nedb")
for line in r.text.splitlines():
    if line == "" or line is None:
        break
    raw = json.loads(line)
    wctf_db[raw["id"]] = {
        "asw_base": raw["stat"]["asw"],
        "asw_max": raw["stat"]["asw_max"],
        "evasion_base": raw["stat"]["evasion"],
        "evasion_max": raw["stat"]["evasion_max"],
        "los_base": raw["stat"]["los"],
        "los_max": raw["stat"]["los_max"],
        }

with open(data_folder / WCTF_DB_FILENAME, "w+") as w:
    json.dump(wctf_db, w, indent=4)
