"""Visible equipment bonus handler.
In game, this is handled via hardcoded conditionals in main.js, but it is difficult to maintain/automate the stat calculation.
We borrow KC3's GearExplicitBonus table for a standard way to check and apply bonuses.
"""

import pathlib
from collections import Counter
from typing import List, Union, Dict


import numpy as np


from data.master import fetch_equip_master
from data.gear_bonus.static import (GearBonus, StatBonus, SynergyBonus, BonusDefinition, COUNT_TYPE, GEAR_BONUS_STAT_KEY, GEAR_BONUS_DEFINITION_KEY, SYNERGY_DEFINITION_KEY)
from data.utils import load_json, search_item_in_array_exists

master_table = {
    "t2": {},
    "t3": {}
}

synergy_table = {}

def check_valid_bonus(ship_id: int,  gear_bonus: GearBonus):
    if gear_bonus.required_ship_id is not None and search_item_in_array_exists(gear_bonus.required_ship_id, ship_id):
        return False

    

class GearTotalBonus:
    def __init__(self, equipment: List[int], improvement: List[int]):
        eq: np.ndarray = np.array(equipment)
        imprv: np.ndarray = np.maximum(improvement[eq > -1], 0)
        eq = eq[eq > -1]
        count = Counter(eq)
        unique_ids = set(eq)
        type2_ids = set([fetch_equip_master(equip_id).type_2 for equip_id in unique_ids])
        type3_ids = set([fetch_equip_master(equip_id).type_3 for equip_id in unique_ids])

def init_bonus():
    from data.gear_bonus.static import COUNTRY_CTYPE_MAP_KEY, SYNERGY_GEAR_KEY

    raw: dict[str, dict] = load_json(pathlib.Path(__file__).parent / "KC3GearBonus.json")
    synergy_gears = raw.pop(SYNERGY_GEAR_KEY)
    synergy_flag_map = load_synergy(synergy_gears)
    country_ctype_map = raw.pop(COUNTRY_CTYPE_MAP_KEY)

    for gear_id, bonus_obj in raw.items():
        if gear_id[0] == "t":
            category, type_id = gear_id.split("_")
            type_id = int(type_id)
            
def load_synergy(synergy_gears: Dict[str, Union[int, List[int]]]) -> Dict[str, List[int]]:
    synergy_flag_ids = {}

    for synergy_flag, gear_ids in synergy_gears.items():
        if "Ids" not in synergy_flag:
            continue
        flag = synergy_flag[:-3]
        synergy_flag_ids[flag] = gear_ids

    return synergy_flag_ids

def load_gear_bonus(bonus_definition: Dict) -> List[GearBonus]:
    ret = []
    bdef = BonusDefinition(**bonus_definition)
    if bdef.byShip is not None:
        by_ship = bdef.byShip
        if isinstance(by_ship, dict):
            by_ship = [by_ship]

        for gear_bonus_definition in by_ship:
            pass

def load_gear_bonus_definiition(gear_bonus_definition: Dict) -> GearBonus:
    if COUNT_TYPE.SINGLE in gear_bonus_definition:
        count_type = COUNT_TYPE.SINGLE
    elif COUNT_TYPE.MULTIPLE in gear_bonus_definition:
        count_type = COUNT_TYPE.MULTIPLE
    else:
        count_type = COUNT_TYPE.DISTINCT

    stats: Dict[str, int] = gear_bonus_definition[count_type]
    synergy = gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.SYNERGY)
    synergy_list = []

    if synergy is not None:
        if isinstance(synergy, dict):
            synergy_list += load_synergy(synergy)
        elif isinstance(synergy, list):
            for synergy_definition in synergy:
                synergy_list += load_synergy(synergy_definition)

    return GearBonus(
        firepower=stats.get(GEAR_BONUS_STAT_KEY.FIREPOWER, 0),
        armor=stats.get(GEAR_BONUS_STAT_KEY.ARMOR, 0),
        torpedo=stats.get(GEAR_BONUS_STAT_KEY.TORPEDO, 0),
        evasion=stats.get(GEAR_BONUS_STAT_KEY.EVASION, 0),
        anti_air=stats.get(GEAR_BONUS_STAT_KEY.ANTI_AIR, 0),
        anti_sub=stats.get(GEAR_BONUS_STAT_KEY.ANTI_SUB, 0),
        line_of_sight=stats.get(GEAR_BONUS_STAT_KEY.LINE_OF_SIGHT, 0),
        accuracy=stats.get(GEAR_BONUS_STAT_KEY.ACCURACY, 0),
        range=stats.get(GEAR_BONUS_STAT_KEY.RANGE, 0),
        speed=stats.get(GEAR_BONUS_STAT_KEY.SPEED, 0),
        dive_bombing=stats.get(GEAR_BONUS_STAT_KEY.DIVE_BOMBING, 0),

        count_type=count_type,
        count_cap=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.COUNT_CAP),
        required_ship_type=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.REQUIRED_SHIP_TYPE),
        required_class_type=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.REQUIRED_CLASS_TYPE),
        required_ship_id=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.REQUIRED_SHIP_ID),
        required_ship_origin=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.REQUIRED_SHIP_ORIGIN),

        distinct_equip_id=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.DISTINCT_EQUIP),
        excluded_ship_id=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.EXCLUDED_SHIP_ID),
        excluded_ship_type=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.EXCLUDED_SHIP_TYPE),
        excluded_class_type=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.EXCLUDED_CLASS_TYPE),
        excluded_ship_origin=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.EXCLUDED_SHIP_ORIGIN),

        minimum_count=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.MINIMUM_COUNT),
        minimum_stars=gear_bonus_definition.get(GEAR_BONUS_DEFINITION_KEY.MINIMUM_STARS),

        synergy_list=synergy_list
    )

def load_synergy(synergy_definition: dict) -> List[SynergyBonus]:
    if COUNT_TYPE.SINGLE in synergy_definition:
        count_type = COUNT_TYPE.SINGLE
    elif COUNT_TYPE.MULTIPLE in synergy_definition:
        count_type = COUNT_TYPE.MULTIPLE
    elif COUNT_TYPE.DISTINCT in synergy_definition:
        count_type = COUNT_TYPE.DISTINCT
    else:
        count_type = COUNT_TYPE.COUNT

    if count_type == COUNT_TYPE.COUNT:
        count_stat_map: Dict[str, Dict] = synergy_definition[count_stat_map]

        return [SynergyBonus(
            firepower=stats.get(GEAR_BONUS_STAT_KEY.FIREPOWER, 0),
            armor=stats.get(GEAR_BONUS_STAT_KEY.ARMOR, 0),
            torpedo=stats.get(GEAR_BONUS_STAT_KEY.TORPEDO, 0),
            evasion=stats.get(GEAR_BONUS_STAT_KEY.EVASION, 0),
            anti_air=stats.get(GEAR_BONUS_STAT_KEY.ANTI_AIR, 0),
            anti_sub=stats.get(GEAR_BONUS_STAT_KEY.ANTI_SUB, 0),
            line_of_sight=stats.get(GEAR_BONUS_STAT_KEY.LINE_OF_SIGHT, 0),
            accuracy=stats.get(GEAR_BONUS_STAT_KEY.ACCURACY, 0),
            range=stats.get(GEAR_BONUS_STAT_KEY.RANGE, 0),
            speed=stats.get(GEAR_BONUS_STAT_KEY.SPEED, 0),
            dive_bombing=stats.get(GEAR_BONUS_STAT_KEY.DIVE_BOMBING, 0),

            count_type=count_type,
            flags=synergy_definition[SYNERGY_DEFINITION_KEY.FLAGS],
            count_required=int(count)
            ) for count, stats in count_stat_map.items()]

    stats: Dict[str, int] = synergy_definition[count_type]

    return [SynergyBonus(
        firepower=stats.get(GEAR_BONUS_STAT_KEY.FIREPOWER, 0),
        armor=stats.get(GEAR_BONUS_STAT_KEY.ARMOR, 0),
        torpedo=stats.get(GEAR_BONUS_STAT_KEY.TORPEDO, 0),
        evasion=stats.get(GEAR_BONUS_STAT_KEY.EVASION, 0),
        anti_air=stats.get(GEAR_BONUS_STAT_KEY.ANTI_AIR, 0),
        anti_sub=stats.get(GEAR_BONUS_STAT_KEY.ANTI_SUB, 0),
        line_of_sight=stats.get(GEAR_BONUS_STAT_KEY.LINE_OF_SIGHT, 0),
        accuracy=stats.get(GEAR_BONUS_STAT_KEY.ACCURACY, 0),
        range=stats.get(GEAR_BONUS_STAT_KEY.RANGE, 0),
        speed=stats.get(GEAR_BONUS_STAT_KEY.SPEED, 0),
        dive_bombing=stats.get(GEAR_BONUS_STAT_KEY.DIVE_BOMBING, 0),

        flags=synergy_definition[SYNERGY_DEFINITION_KEY.FLAGS],
        count_type=count_type
    )]
