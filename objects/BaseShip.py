from dataclasses import dataclass
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
    proficiency = [-1, -1, -1, -1, -1]
    stars = [-1, -1, -1, -1, -1]
    slot = [0, 0, 0, 0, 0]
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
    
    def fetch_equipment_total_stats(self, stat_name: str, use_visible_bonus = False, included_types = None,
                                          included_ids = None, excluded_types = None, excluded_ids = None,
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

