from functools import reduce
from utils import count_equip
from .Fleet import PlayerFleet, EnemyFleet, FriendFleet
from .static import BATTLETYPE, FLEETTYPE
from .Ship import EnemyShip, PlayerShip

class Battle:
    """Class representing a battle.
    """
    def __init__(self, apiname: str, rawapi: dict, playerformation: int, resupplyused: bool, fleet: dict, **kwargs):
        self.battletype = apiname
        self.engagement = rawapi["api_formation"][2]

        self.ecombined = "api_ship_ke_combined" in rawapi.keys()
        self.fcombined = fleet["fleettype"]
        self.fship_mapping: dict[int, PlayerShip] = {}
        self.eship_mapping: dict[int, EnemyShip] = {}

        self.player_fleet = PlayerFleet(playerformation, fleet["fleet1"], rawapi["api_fParam"], rawapi["api_f_nowhps"],
                                       rawapi["api_f_maxhps"], self.fcombined)
        
        for idx, ship in self.player_fleet.ships:
            self.fship_mapping[idx] = ship

        self.enemy_fleet = EnemyFleet(rawapi["api_formation"][1], rawapi["api_ship_ke"], rawapi["api_ship_lv"], rawapi["api_eParam"],
                                      rawapi["api_eSlot"], rawapi["api_e_nowhps"], rawapi["api_e_maxhps"], is_combined=self.ecombined)

        for idx, ship in self.enemy_fleet.ships:
            self.eship_mapping[idx] = ship

        if self.fcombined != FLEETTYPE.SINGLE:
            self.player_escort_fleet = PlayerFleet(playerformation, fleet["fleet2"], rawapi["api_fParam_combined"],
                                                   rawapi["api_f_nowhps_combined"], rawapi["api_f_maxhps_combined"],
                                                   self.fcombined, False)

            for idx, ship in self.player_escort_fleet:
                self.fship_mapping[idx + 6] = ship

        if self.ecombined:
            self.enemy_escort_fleet = EnemyFleet(rawapi["api_formation"][1], rawapi["api_ship_ke_combined"],
                                                 rawapi["api_ship_lv_combined"], rawapi["api_eParam_combined"],
                                                 rawapi["api_eSlot_combined"], rawapi["api_e_nowhps_combined"],
                                                 rawapi["api_e_maxhps_combined"], False, self.ecombined)

            for idx, ship in self.enemy_escort_fleet:
                self.eship_mapping[idx + 6] = ship

        if "api_friendly_info" in rawapi:
            self.friendly_fleet = FriendFleet(playerformation=playerformation, **rawapi["api_friendly_info"])

        if resupplyused:
            self.resupply_fleet(self.fcombined != FLEETTYPE.SINGLE)

        # Get night contact plane if battle is at night
        self.contact = -1
        self.active_deck = [1, 1]
        if self.battletype in [BATTLETYPE.NIGHT, BATTLETYPE.NIGHT_START, BATTLETYPE.COMBINED_NIGHT,
            BATTLETYPE.COMBINED_NIGHT_START, BATTLETYPE.SINGLE_VS_COMBINED_NIGHT, BATTLETYPE.SINGLE_VS_COMBINED_NIGHT_TO_DAY]:
            self.contact = rawapi["api_touch_plane"][0]
            self.active_deck = rawapi["api_active_deck"]

    def resupply_fleet(self, combined: bool):
        num, numc = 0.125, 0.025 if combined else 0.11, 0.14
        rcount = reduce(lambda x, y: x + count_equip(y.equip, 146), self.fship_mapping.values(), 0)

        f = lambda x: PlayerShip.resupply(x, num * min(rcount, 3) + numc)
        map(f, self.fship_mapping.values())
