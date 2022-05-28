import json
from typing import List, Union
from functools import reduce
import numpy as np

#lang = "en"
FIGHTER_BOMBER_ID = [60, 154, 219, 447]
SEC_GUN_FILTER = [11, 134, 135]
T2_FP_LIST = [1, 2, 18, 19, 21, 24, 29, 42, 36, 37, 39, 46]
BOMBER_TYPE2_ID = [7, 8, 11, 41, 47, 53, 57, 58]

# Data loading
def lookup_table(raw):
    table = {}
    for obj in raw:
        table[obj["api_id"]] = obj
    return table

with open("./data/api_mst_ship.json", encoding="utf-8") as r:
    ship_master_lookup = lookup_table(json.load(r))

with open("./data/api_mst_slotitem.json", encoding="utf-8") as r:
    equip_master_lookup = lookup_table(json.load(r))

with open("./data/KC3RemodelDB.json", encoding="utf-8") as r:
    remodel_db = json.load(r)

with open("./data/idTL.json", encoding="utf-8") as r:
    id_tl = json.load(r)

def fetch_ship_master(ship_id: int) -> "dict[str, int]":
    return ship_master_lookup[ship_id]

def fetch_equip_master(equip_id: int) -> "dict[str, int]":
    return equip_master_lookup[equip_id]

def find_ship_origin(ship_id: int) -> int:
    return remodel_db["originOf"][str(ship_id)]

def find_remodel_group(ship_id: int) -> int:
    original_id = find_ship_origin(ship_id)
    return remodel_db["remodelGroups"][str(original_id)]["group"]

def calculate_equip_stat(equip_id: int, api_stat: str) -> int:
    if equip_id == -1:
        return 0
    master = fetch_equip_master(equip_id)
    return master["api_" + api_stat]

def calculate_all_equipment_stat(equip_list: List[int], api_stat: str) -> int:
    num = 0
    for equip_id in equip_list:
        num += calculate_equip_stat(equip_id, api_stat)
    return num

def get_gear_improvement_stats(ship):
    result = {
        "fp": 0,
        "asw": 0,
        "tp": 0,
        "yasen": 0
    }
    for idx, equip_id in enumerate(ship.equip):
        improvement = ship.stars[idx]
        if equip_id == -1 or improvement <= 0:
            continue
        master = fetch_equip_master(equip_id)
        type2 = master["api_type"][2]

        # FP
        # Large Gun
        if type2 == 3:
            result["fp"] += 1.5 * np.sqrt(improvement)
        # Secondary Gun
        elif type2 == 4:
            if equip_id in SEC_GUN_FILTER:
                result["fp"] += np.sqrt(improvement)
                result["yasen"] += np.sqrt(improvement)
            else:
                mod = 0.2 if master["api_type"][3] == 16 else 0.3
                result["fp"] += mod * improvement
                result["yasen"] += mod * improvement
        # F/B and Jet F/B
        elif (type2 == 7 or type2 == 57) and equip_id in FIGHTER_BOMBER_ID:
            result["fp"] += 0.5 * np.sqrt(improvement)
        # TB and Jet TB
        elif type2 == 8 or type2 == 58:
            result["fp"] += 0.2 * improvement
        # Sonar and large sonar
        elif type2 == 14 or type2 == 40:
            result["fp"] += 0.75 * np.sqrt(improvement)
        # Depth Charge Projector
        elif type2 == 15 and not equip_id in [226, 227]:
            result["fp"] += 0.75 * np.sqrt(improvement)
        elif type2 in T2_FP_LIST:
            result["fp"] += np.sqrt(improvement)
        
        # TP
        if type2 in [5, 21, 32]:
            result["tp"] += 1.2 * np.sqrt(improvement)

        # ASW
        if type2 in [14, 15, 40]:
            result["asw"] += np.sqrt(improvement)
        elif (type2 == 7 or type2 == 57) and equip_id not in FIGHTER_BOMBER_ID:
            result["asw"] += 0.2 * improvement
        elif type2 == 8 or type2 == 58:
            result["asw"] += 0.2 * improvement
        elif type2 == 25:
            mod = 0.3 if master["api_tais"] > 10 else 0.2
            result["asw"] += mod * improvement

        # Yasen
        if type2 in [1, 2, 3, 5, 19, 22, 24, 29, 32, 36, 37, 38, 42, 46]:
            result["yasen"] += np.sqrt(improvement)
        elif type2 in [7, 8, 57, 58]:
            result["yasen"] += np.sqrt(improvement)

    return result

def fetch_ship_translation(ship_id: int, lang: str = "en") -> str:
    return id_tl["ships"][str(ship_id)][lang]

def fetch_equip_translation(equip_id: int, lang: str ="en") -> str:
    return id_tl["equip"][str(equip_id)][lang]
