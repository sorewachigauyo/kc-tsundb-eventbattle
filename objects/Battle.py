from .Fleet import PlayerFleet, EnemyFleet, FriendFleet
from .static import FLEETTYPE
from .Ship import EnemyShip, PlayerShip

class Battle:
    """Class representing a battle.
    """
    def __init__(self, apiname, rawapi, playerformation, resupplyused, fleet, **kwargs):
        self.battletype = apiname
        self.engagement = rawapi["api_formation"][2]

        ecombined = "api_ship_ke_combined" in rawapi
        fcombined = fleet["fleettype"]
        self.fship_mapping: dict[int, PlayerShip] = {}
        self.eship_mapping: dict[int, EnemyShip] = {}

        self.player_fleet = PlayerFleet(playerformation, fleet["fleet1"], rawapi["api_fParam"], rawapi["api_f_nowhps"],
                                       rawapi["api_f_maxhps"], fcombined)
        
        for idx, ship in self.player_fleet.ships:
            self.fship_mapping[idx] = ship

        self.enemy_fleet = EnemyFleet(rawapi["api_formation"][1], rawapi["api_ship_ke"], rawapi["api_ship_lv"], rawapi["api_eParam"],
                                      rawapi["api_eSlot"], rawapi["api_e_nowhps"], rawapi["api_e_maxhps"], is_combined=ecombined)

        for idx, ship in self.enemy_fleet.ships:
            self.eship_mapping[idx] = ship

        if fcombined != FLEETTYPE.SINGLE:
            self.player_escort_fleet = PlayerFleet(playerformation, fleet["fleet2"], rawapi["api_fParam_combined"],
                                                   rawapi["api_f_nowhps_combined"], rawapi["api_f_maxhps_combined"],
                                                   fcombined, False)

            for idx, ship in self.player_escort_fleet:
                self.fship_mapping[idx + 6] = ship

        if ecombined:
            self.enemy_escort_fleet = EnemyFleet(rawapi["api_formation"][1], rawapi["api_ship_ke_combined"],
                                                 rawapi["api_ship_lv_combined"], rawapi["api_eParam_combined"],
                                                 rawapi["api_eSlot_combined"], rawapi["api_e_nowhps_combined"],
                                                 rawapi["api_e_maxhps_combined"], False, ecombined)

            for idx, ship in self.enemy_escort_fleet:
                self.eship_mapping[idx + 6] = ship

        if "api_friendly_info" in rawapi:
            self.friendly_fleet = FriendFleet(playerformation=playerformation, **rawapi["api_friendly_info"])

        if resupplyused:
            self.resupply_fleet(fcombined != FLEETTYPE.SINGLE)

    def resupply_fleet(self, combined):
        num = 1.15 if combined else 1.25
        f = lambda x: PlayerShip.resupply(x, num)
        map(f, self.fship_mapping.values())


        


        

