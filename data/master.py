from dataclasses import dataclass
from typing import List, Dict


from data.utils import load_json, data_folder
from data.static import SHIP_MASTER_FILENAME, EQUIP_MASTER_FILENAME, MST_SHIP_KEYS, MST_EQUIP_KEYS, WCTF_DB_FILENAME, ABYSSAL_SHIP_ID_CUTOFF


@dataclass
class ShipMaster:
    """Master record for the ship.
    Some entries are ignored for the sake 
    """
    id: int
    ship_type: int
    class_type: int
    remodel_next_id: int
    max_ammo: int
    max_fuel: int
    asw_base: int
    asw_max: int

    def estimate_asw(self, level):
        """Estimates the ship ASW based on the level of the ship.
        """
        if self.asw_max == 0:
            return 0

        return self.asw_base + int((self.asw_max - self.asw_base) * level / 99)

@dataclass
class EquipMaster:
    id: int
    firepower: int
    torpedo: int
    armor: int
    anti_air: int
    anti_sub: int
    los: int
    dive_bombing: int
    type_1: int # General Category ID
    type_2: int # Picture Book ID
    type_3: int # Specialized Category ID
    type_4: int # Equipment Icon ID
    type_5: int # Aircraft ID

master_initialized = False
ship_master_table: dict[int, ShipMaster] = {}
equip_master_table: dict[int, EquipMaster] = {}

def is_abyssal(ship_id: int) -> bool:
    return ship_id >= ABYSSAL_SHIP_ID_CUTOFF

def init_master():
    """Initializes the master records from the api data.
    """
    ship_master_raw: List[Dict] = load_json(data_folder / SHIP_MASTER_FILENAME)
    wctf_db: Dict[str, Dict] = load_json(data_folder / WCTF_DB_FILENAME)

    for mst_ship in ship_master_raw:
        ship_id = mst_ship[MST_SHIP_KEYS.ID]

        ship_master_table[ship_id] = ShipMaster(
            id=ship_id,
            ship_type=mst_ship[MST_SHIP_KEYS.SHIP_TYPE],
            class_type=mst_ship[MST_SHIP_KEYS.CLASS_TYPE],
            asw_base=wctf_db[str(ship_id)]["asw_base"] if not is_abyssal(ship_id) else 0,
            asw_max=wctf_db[str(ship_id)]["asw_max"] if not is_abyssal(ship_id) else 0,
            remodel_next_id=mst_ship[MST_SHIP_KEYS.REMODEL_NEXT_ID] if not is_abyssal(ship_id) else 0,
            max_ammo=mst_ship[MST_SHIP_KEYS.MAX_AMMO] if not is_abyssal(ship_id) else 0,
            max_fuel=mst_ship[MST_SHIP_KEYS.MAX_FUEL] if not is_abyssal(ship_id) else 0
        )

    equip_master_raw: List[Dict] = load_json(data_folder / EQUIP_MASTER_FILENAME)

    for mst_slotitem in equip_master_raw:
        equip_id = mst_slotitem[MST_EQUIP_KEYS.ID]
        equip_type = mst_slotitem[MST_EQUIP_KEYS.TYPE]
        equip_master_table[equip_id] = EquipMaster(
            id=equip_id,
            firepower=mst_slotitem[MST_EQUIP_KEYS.FIREPOWER],
            torpedo=mst_slotitem[MST_EQUIP_KEYS.TORPEDO],
            armor=mst_slotitem[MST_EQUIP_KEYS.ARMOR],
            anti_air=mst_slotitem[MST_EQUIP_KEYS.ANTI_AIR],
            anti_sub=mst_slotitem[MST_EQUIP_KEYS.ANTI_SUBMARINE],
            los=mst_slotitem[MST_EQUIP_KEYS.LINE_OF_SIGHT],
            dive_bombing=mst_slotitem[MST_EQUIP_KEYS.DIVE_BOMBING],
            type_1=equip_type[0],
            type_2=equip_type[1],
            type_3=equip_type[2],
            type_4=equip_type[3],
            type_5=equip_type[4]
        )

    master_initialized = True

def fetch_ship_master(ship_id: int) -> ShipMaster:
    """Fetches the master record for the specified ship id.
    """
    return ship_master_table[ship_id]

def fetch_equip_master(equip_id: int) -> EquipMaster:
    """Fetches the master record for the specified equip id.
    """
    return equip_master_table[equip_id]
