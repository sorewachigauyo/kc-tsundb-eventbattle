from .static import SIDE, FLEETTYPE, FLEETORDER
from .Ship import PlayerShip, EnemyShip, FriendShip


class PlayerFleet:
    """Player side fleet object
    """
    def __init__(self, playerformation, shipobj_array, fParam_array, nowhp_array, maxhp_array, fleettype, is_main=True):
        self.ships = [PlayerShip(nowhp_array[idx], maxhp_array[idx], fParam_array[idx], ship_obj, self) for idx, ship_obj in enumerate(shipobj_array)]
        self.formation = playerformation
        self.order = FLEETORDER.MAIN if is_main else FLEETORDER.ESCORT
        self.side = SIDE.PLAYER
        self.fleet_type = fleettype

class EnemyFleet:
    def __init__(self, formation, ship_ke, ship_lv, eParam, eSlot, nowhp, maxhp, is_main=True, is_combined=False):
        self.ships = [EnemyShip(nowhp[idx], maxhp[idx], eParam[idx], eSlot[idx],
                                ship_lv[idx], ship_id, self) for idx, ship_id in enumerate(ship_ke)]
        self.formation = formation
        self.order = FLEETORDER.MAIN if is_main else FLEETORDER.ESCORT
        self.side = SIDE.ENEMY
        self.fleet_type = FLEETTYPE.SINGLE if not is_combined else FLEETTYPE.ENEMYCOMBINED

class FriendFleet:
    def __init__(self, playerformation, api_ship_id, api_ship_lv, api_nowhps, api_maxhps, api_Slot, api_slot_ex, api_Param, **kwargs):
        self.ships = [FriendShip(api_nowhps[idx], api_maxhps[idx], api_Param[idx], api_Slot[idx] + [api_slot_ex[idx]],
                                 api_ship_lv[idx], ship_id, self) for idx, ship_id in enumerate(api_ship_id)]
        self.formation = playerformation
