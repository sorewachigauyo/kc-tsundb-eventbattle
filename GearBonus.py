"""
This is too complicated and deserves its own module
With reference to https://github.com/KC3Kai/KC3Kai/blob/master/src/library/objects/GearBonus.js
"""
import json
import copy
from utils import fetch_equip_master, find_ship_origin, find_remodel_group

with open("./data/KC3GearBonus.json") as r:
    data = json.load(r)

bonus_gear_ids = list(data.keys())
country_ctype_map = data["countryCtypeMap"]

def calculate_bonus_gear_stats(ship):
    result = {
        "houg": 0,
        "souk": 0,
        "raig": 0,
        "houk": 0,
        "tyku": 0,
        "tais": 0,
        "saku": 0,
        "houm": 0,
        "leng": 0,
        "soku": 0,
        "baku": 0
    }

    # First fill up synergy gear pieces
    synergy = data["synergyGears"]
    synergy = fill_synergy(ship, synergy)

    # Then fill bonus data
    bonus_accum = fill_count(ship)

    # Afterwards, we check conditions and add stats
    for bonus in bonus_accum.values():
        add_bonus(bonus, result, ship, synergy)

    return result


def fill_synergy(ship, raw):
    synergy = copy.copy(raw)
    for equip_id in ship.equip:
        if equip_id == -1:
            continue
        master = fetch_equip_master(equip_id)
        for key in synergy.keys():
            if "Ids" in key:
                # Surface Radars
                if key == "surfaceRadarIds":
                    if master["api_type"][2] in [12, 13, 93] and master["api_saku"] > 4:
                        synergy["surfaceRadar"] += 1

                # Air Radars
                elif key == "airRadarIds":
                    if master["api_type"][2] in [12, 13, 93] and master["api_tyku"] > 1:
                        synergy["airRadar"] += 1

                # Rotorcraft
                elif key == "rotorcraftIds":
                    if master["api_type"][2] == 25:
                        synergy["rotorcraft"] += 1

                # AA MG
                elif key == "aaMachineGunIds":
                    if master["api_type"][2] == 21:
                        synergy["aaMachineGun"] += 1

                else:
                    base_key = key[0: -3]
                    if equip_id in synergy[key]:
                        synergy[base_key] += 1
                        nonexist = base_key + "Nonexist"
                        if nonexist in synergy.keys():
                            synergy[nonexist] = 0
    return synergy


def fill_count(ship):
    obj = {}

    for idx, equip_id in enumerate(ship.equip):
        if equip_id == -1:
            continue
        master = fetch_equip_master(equip_id)
        improvement = ship.stars[idx]

        if str(equip_id) in bonus_gear_ids:
            if equip_id not in obj.keys():
                obj[equip_id] = copy.copy(data[str(equip_id)])
            bonus = obj[equip_id]
            bonus["count"] += 1
            bonus = fill_stars(bonus, improvement)

        t2key = "t2_{}".format(master["api_type"][2])
        t3key = "t3_{}".format(master["api_type"][3])

        if t2key in bonus_gear_ids:
            if t2key not in obj.keys():
                obj[t2key] = copy.copy(data[t2key])
            bonus = obj[t2key]
            bonus["count"] += 1
            fill_stars(bonus, improvement)

        if t3key in bonus_gear_ids:
            if t3key not in obj.keys():
                obj[t3key] = copy.copy(data[t3key])
            bonus = obj[t3key]
            bonus["count"] += 1
            fill_stars(bonus, improvement)

    return obj


def fill_stars(bonus, improvement):
    if (improvement == -1):
        return bonus

    if "starsDist" in bonus.keys():
        if len(bonus["starsDist"]) == 0:
            bonus["starsDist"] = [0 for i in range(11)]

        bonus["starsDist"][improvement] += 1
    return bonus


def add_bonus(bonus, result, ship, synergy):
    ctype = ship.ctype
    if "byClass" in bonus and str(ctype) in bonus["byClass"].keys():
        bonus_definition = bonus["byClass"][str(ctype)]
        # Linked to another ctype
        if isinstance(bonus_definition, str):
            bonus_definition = bonus["byClass"][bonus_definition]

        if isinstance(bonus_definition, list):
            for bdef in bonus_definition:
                add_stats(bdef, ship, result, synergy, bonus)
        else:
            add_stats(bonus_definition, ship, result, synergy, bonus)

    if "byShip" in bonus:
        bonus_definition = bonus["byShip"]
        if isinstance(bonus_definition, list):
            for bdef in bonus_definition:
                add_stats(bdef, ship, result, synergy, bonus)
        else:
            add_stats(bonus_definition, ship, result, synergy, bonus)

    if "byNation" in bonus:
        nation_name = next(k for k, v in country_ctype_map.items() if ctype in v)
        bonus_definition = bonus["byNation"]

        # In case ctype map not updated yet
        if nation_name and nation_name in bonus_definition:
            bdef = bonus_definition[nation_name]

            if isinstance(bdef, str):
                if isinstance(bonus_definition[bdef], list):
                    bdef = bonus_definition[bdef]
                else:
                    add_stats(bonus_definition[bdef], ship, result, synergy, bonus)
                    return

            if isinstance(bdef, int):
                add_stats(bonus["byClass"][str(bdef)], ship, result, synergy, bonus)

            elif isinstance(bdef, list):
                for v in bdef:
                    add_stats(v, ship, result, synergy, bonus)
            else:
                add_stats(bdef, ship, result, synergy, bonus)


def add_stats(bonus_definition, ship, result, synergy, bonus):
    ctype = ship.ctype
    keys = bonus_definition.keys()
    origin = find_ship_origin(ship.id)
    remodel_group = find_remodel_group(ship.id)
    remodel_index = remodel_group.index(ship.id)

    if "ids" in keys and not (ship.id in bonus_definition["ids"]):
        return
    if "excludes" in keys and ship.id in bonus_definition["excludes"]:
        return
    if "origins" in keys and not(origin in bonus_definition["origins"]):
        return
    if "excludeOrigins" in keys and origin in bonus_definition["excludeOrigins"]:
        return
    if "classes" in keys and not(ctype in bonus_definition["classes"]):
        return
    if "excludeClasses" in keys and ctype in bonus_definition["excludeClasses"]:
        return
    if "stypes" in keys and not(ship.stype in bonus_definition["stypes"]):
        return
    if "excludeStypes" in keys and ship.stype in bonus_definition["excludeStypes"]:
        return
    if "remodel" in keys and remodel_index < bonus_definition["remodel"]:
        return
    if "remodelCap" in keys and remodel_index > bonus_definition["remodelCap"]:
        return

    count = bonus["count"]
    if "minStars" in keys:
        count = sum(bonus["starsDist"][bonus_definition["minStars"]:])
        if count == 0:
            return

    if "minCount" in keys and count < bonus_definition["minCount"]:
        return

    # We can finally add the stats together
    if "single" in keys:
        _add_stats(result, bonus_definition["single"])

    if "multiple" in keys:
        if "countCap" in keys:
            count = min(count, bonus_definition["countCap"])
        _add_stats(result, bonus_definition["multiple"], count)

    # Gear synergy
    if "synergy" in keys:
        synergy_bonuses = bonus_definition["synergy"]
        if not isinstance(synergy_bonuses, list):
            synergy_bonuses = [synergy_bonuses]

        for synergy_bonus in synergy_bonuses:
            flags = synergy_bonus["flags"]
            s_keys = synergy_bonus.keys()
            if all([synergy[flag] > 0 for flag in flags]):
                if "single" in s_keys:
                    _add_stats(result, synergy_bonus["single"])
                if "distinct" in s_keys:
                    flags_key = "_".join(flags) + "Applied"
                    if not (flags_key in synergy):
                        synergy[flags_key] = 0
                    synergy[flags_key] += 1
                    if synergy[flags_key] < 2:
                        _add_stats(result, synergy_bonus["distinct"])
                if "byCount" in s_keys:
                    gear_name = synergy_bonus["byCount"]["gear"]
                    if gear_name == "this":
                        gear_count = count
                    else:
                        gear_count = synergy[gear_name]
                    if str(gear_count) in synergy_bonus["byCount"]:
                        _add_stats(
                            result, synergy_bonus["byCount"][str(gear_count)])


def _add_stats(dict1, dict2, num=1):
    # Add values of dict2 into dict1
    for key, value in dict2.items():
        dict1[key] += value * num
