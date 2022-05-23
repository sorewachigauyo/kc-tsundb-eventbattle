from dataclasses import dataclass
from functools import reduce
from typing import List, Union
from objects.static import SIDE, STYPE
from objects.BaseShip import Ship
from utils import fetch_equip_master, fetch_ship_master

@dataclass()
class PlayerShip(Ship):
    """Player side ship object
    """
    def __init__(self, nowhp, maxhp, fParam, ship_obj, fleet):
        self.hp = [nowhp, maxhp]
        self.fp = ship_obj["stats"]["fp"]
        self.tp = fParam[1]
        self.aa = fParam[2]
        self.ar = fParam[3]
        self.id = ship_obj["id"]
        self.lvl = ship_obj["lvl"]
        self.morale = ship_obj["morale"]
        self.equip = ship_obj["equips"]
        self.visible_stats = ship_obj["stats"]
        self.proficiency = ship_obj["proficiency"]
        self.stars = ship_obj["improvements"]
        self.slot = ship_obj["slots"]
        self.fuel = ship_obj["fuel"]
        self.ammo = ship_obj["ammo"]
        self.side = SIDE.PLAYER
        self.fleet = fleet
        
        master = fetch_ship_master(self.id)
        self.stype = master["api_stype"]
        self.ctype = master["api_ctype"]
        self.speed = master["api_soku"]

    
    def resupply(self, amount):
        master = fetch_ship_master(self.id)
        fuel_max = master["api_fuel_max"]
        ammo_max = master["api_bull_max"]

        self.fuel = min(int(self.fuel + fuel_max * amount), fuel_max)
        self.ammo = min(int(self.ammo + ammo_max * amount), ammo_max)

    def uses_carrier_shelling(self):
        """Checks if the ship uses carrier shelling.
        """
        if self.is_carrier():
            return True
        if self.id == 717 or self.id == 352: # Yamashio Maru or Hayasui use carrier shelling if they have a non-zeroed bomber 
            for idx, equip_id in enumerate(self.equip):
                if equip_id == -1:
                    pass
                master = fetch_equip_master(equip_id)
                if master.get("api_type")[2] in [7, 8] and self.slot[idx] > 0:
                    return True
        return False

    def uses_carrier_asw_shelling(self):
        """Checks if the ship uses aerial attack when attacking submarines.
        """
        if self.is_carrier() or self.stype == STYPE.CAV or self.stype == STYPE.AV or self.stype == STYPE.LHA or self.stype == STYPE.BBV:
            return True
        
        return False


@dataclass()
class EnemyShip(Ship):
    """Enemy side ship object
    """
    def __init__(self, nowhp, maxhp, eParam, eSlot, ship_lv, id, fleet):
        self.hp = [nowhp, maxhp]
        self.fp = eParam[0]
        self.tp = eParam[1]
        self.aa = eParam[2]
        self.ar = eParam[3]
        self.id = id
        self.fleet = fleet
        self.equip = eSlot
        self.lvl = ship_lv
        self.side = SIDE.ENEMY

        master = fetch_ship_master(self.id)
        self.stype = master["api_stype"]
        self.speed = master["api_soku"]

@dataclass()
class FriendShip(Ship):
    """Friendly fleet ship object
    """
    def __init__(self, nowhp, maxhp, fParam, fSlot, ship_lv, id, fleet):
        self.hp = [nowhp, maxhp]
        self.fp = fParam[0]
        self.tp = fParam[1]
        self.aa = fParam[2]
        self.ar = fParam[3]
        self.id = id
        self.fleet = fleet
        self.equip = fSlot
        self.lvl = ship_lv
        self.side = SIDE.FRIEND
        self.fleet = fleet

        master = fetch_ship_master(self.id)
        self.stype = master.get("api_stype", 0)
        self.speed = master.get("api_soku", 0)
        self.ctype = master.get("api_ctype", 0)
        self.slot = master.get("api_maxeq", [0, 0, 0, 0, 0])
        self.fuel = master.get("api_fuel_max", 100)
        self.ammo = master.get("api_bull_max", 100)
