from dataclasses import dataclass
from functools import reduce
from typing import List, Union
from utils import fetch_equip_master
from GearBonus import calculate_bonus_gear_stats
from objects.static import SIDE, STYPE


@dataclass
class Ship:
    """Base ship class object
    """
    lvl = 1
    id = 1
    morale = 49
    hp = [0, 0]
    fp = 0
    tp = 0
    ar = 0
    aa = 0
    asw = 0
    lk = 0
    stype = 1
    ctype = 1
    equip = [-1, -1, -1, -1, -1]
    proficiency = [0, 0, 0, 0, 0, 0]
    stars = [0, 0, 0, 0, 0, 0]
    slot = [0, 0, 0, 0, 0, 0]
    fleet = None
    side = SIDE.PLAYER
    fuel = 100
    ammo = 100

    def is_carrier(self):
        """Checks the stype if ship is a carrier.
        """
        return self.stype == STYPE.CVL or self.stype == STYPE.CV or self.stype == STYPE.CVB

    def is_submarine(self):
        """Checks the stype if ship is a submarine.
        """
        return self.stype == STYPE.SS or self.stype == STYPE.SSV

    def fetch_equipment_total_stats(self, stat_name: str, use_visible_bonus=False, included_types=None,
                                    included_ids=None, excluded_types=None, excluded_ids=None,
                                    return_visible_bonus_only=False):
        num = 0
        num2 = 0
        for equip_id in self.equip:

            if equip_id == -1:
                continue

            if included_ids:
                if not equip_id in included_ids:
                    continue

            if excluded_ids:
                if equip_id in excluded_ids:
                    continue

            master = fetch_equip_master(equip_id)

            if included_types:
                if not master.get("api_type")[2] in included_types:
                    continue

            if excluded_types:
                if master.get("api_type")[2] in excluded_types:
                    continue

            num += master.get("api_" + stat_name)

        if use_visible_bonus and self.side != SIDE.ENEMY:
            r = calculate_bonus_gear_stats(self)
            num2 += r.get(stat_name, 0)

        if return_visible_bonus_only:
            return num2
        return num + num2

    def count_equip(self, equip_id: Union[int, List[int]]):
        if isinstance(equip_id, int):
            return reduce(lambda x, y: x + (y == equip_id), self.equip, 0)
        elif isinstance(equip_id, list):
            return reduce(lambda x, y: x + (y in equip_id), self.equip, 0)

    def count_equip_by_type(self, equip_type: Union[int, List[int]], type_filter: int):
        if isinstance(equip_type, int):
            return reduce(lambda x, y: x + (fetch_equip_master(y)["api_type"][type_filter] == equip_type if y > 0 else 0), self.equip, 0)
        elif isinstance(equip_type, list):
            return reduce(lambda x, y: x + (fetch_equip_master(y)["api_type"][type_filter] in equip_type if y > 0 else 0), self.equip, 0)

    def has_equip(self, equip_id: Union[int, List[int]]):
        if isinstance(equip_id, int):
            return equip_id in self.equip
        elif isinstance(equip_id, list):
            return bool(next((eq_id for eq_id in self.equip if eq_id in equip_id), False))

    def has_equip_type(self, equip_type: Union[int, List[int]], type_filter: int):
        if isinstance(equip_type, int):
            return next((eq_id for eq_id in self.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][type_filter] == equip_type), False)
        elif isinstance(equip_type, list):
            return next((eq_id for eq_id in self.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][type_filter] in equip_type), False)
