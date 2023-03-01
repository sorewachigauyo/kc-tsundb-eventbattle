from typing import List, Union
from api_parsing.static import HougekiAttack, KoukuAttack, MidnightAttack, RaigekiAttack


from battle.static import PHASE, BattleAttack
from battle.ship import Ship
from data.static import FLEET_TYPE, SIDE

class Battle:
    def __init__(self, rawapi: dict, battle_type: str, player_formation: int, fleet: dict):

        self.player_formation = player_formation
        self.ecombined = bool("api_ship_ke_combined" in rawapi)
        self.fcombined = fleet["fleettype"]
        self.engagement = rawapi["api_formation"][2]

        self.player_fleet = {position: Ship(
            id=ship_object["id"],
            level=ship_object["lvl"],
            equipment=ship_object["equips"],
            firepower=ship_object["stats"]["fp"],
            torpedo=ship_object["stats"]["tp"],
            anti_air=ship_object["stats"]["aa"],
            armor=ship_object["stats"]["ar"],
            improvement=ship_object["improvements"],
            ammo=ship_object["ammo"],
            starting_hp=current_hp,
            max_hp=max_hp
        ) for position, (ship_object, current_hp, max_hp) in enumerate(zip(
            fleet["fleet1"],
            rawapi["api_f_nowhps"],
            rawapi["api_f_maxhps"]
        ))}
        self.main_fleet = [ship.id for ship in self.player_fleet.values()]

        if self.fcombined != FLEET_TYPE.SINGLE:
            ef = {position + 6: Ship(
                id=ship_object["id"],
                level=ship_object["lvl"],
                equipment=ship_object["equips"],
                firepower=ship_object["stats"]["fp"],
                torpedo=ship_object["stats"]["tp"],
                anti_air=ship_object["stats"]["aa"],
                armor=ship_object["stats"]["ar"],
                improvement=ship_object["improvements"],
                ammo=ship_object["ammo"],
                starting_hp=current_hp,
                max_hp=max_hp
            ) for position, (ship_object, current_hp, max_hp) in enumerate(zip(
                fleet["fleet2"],
                rawapi["api_f_nowhps_combined"],
                rawapi["api_f_maxhps_combined"]
            ))}
            self.player_fleet.update(ef)
            self.escort_fleet = [ship.id for ship in ef.values()]

        self.enemy_fleet = {
            position: Ship(
                id=ship_id,
                level=level,
                equipment=equipment,
                firepower=stats[0],
                torpedo=stats[1],
                anti_air=stats[2],
                armor=stats[3],
                starting_hp=current_hp,
                max_hp=max_hp
            ) for position, (ship_id, level, stats, equipment, current_hp, max_hp) in enumerate(zip(
                rawapi["api_ship_ke"],
                rawapi["api_ship_lv"],
                rawapi["api_eParam"],
                rawapi["api_eSlot"],
                rawapi["api_e_nowhps"],
                rawapi["api_e_maxhps"]
            ))
        }

        if self.ecombined:
            self.enemy_fleet.update({
                position + 6: Ship(
                    id=ship_id,
                    level=level,
                    equipment=equipment,
                    firepower=stats[0],
                    torpedo=stats[1],
                    anti_air=stats[2],
                    armor=stats[3],
                    starting_hp=current_hp,
                    max_hp=max_hp
                ) for position, (ship_id, level, stats, equipment, current_hp, max_hp) in enumerate(zip(
                    rawapi["api_ship_ke_combined"],
                    rawapi["api_ship_lv_combined"],
                    rawapi["api_eParam_combined"],
                    rawapi["api_eSlot_combined"],
                    rawapi["api_e_nowhps_combined"],
                    rawapi["api_e_maxhps_combined"]
                ))
            })

        self.friendly_fleet = {}
        if "api_friendly_info" in rawapi:
            ff_info = rawapi["api_friendly_info"]
            self.friendly_fleet = {position: Ship(
                id=ship_id,
                level=level,
                equipment=equipment + [exslot],
                firepower=stats[0],
                torpedo=stats[1],
                anti_air=stats[2],
                armor=stats[3],
                starting_hp=current_hp,
                max_hp=max_hp
            ) for position, (ship_id, level, current_hp, max_hp, equipment, exslot, stats) in enumerate(zip(
                ff_info["api_ship_id"],
                ff_info["api_ship_lv"],
                ff_info["api_nowhps"],
                ff_info["api_maxhps"],
                ff_info["api_Slot"],
                ff_info["api_slot_ex"],
                ff_info["api_Param"]
            ))}


    def hp_snapshot(self):
        return {position: ship.starting_hp for position, ship in self.player_fleet.items()
                }, {position: ship.starting_hp for position, ship in self.enemy_fleet.items()
                    }, {position: ship.starting_hp for position, ship in self.friendly_fleet.items()}
    
    def iterate_over_attacks(self, attacks: List[Union[HougekiAttack, RaigekiAttack, KoukuAttack, MidnightAttack]]):
        player_hp, enemy_hp, ff_hp = self.hp_snapshot()
        ret: List[BattleAttack] = []

        for attack in attacks:

            if attack.side == SIDE.PLAYER and (isinstance(attack, HougekiAttack) or isinstance(attack, MidnightAttack)) and attack.attacker is not None:
                ret.append(
                    BattleAttack(
                        attacker=self.player_fleet[attack.attacker],
                        defender=self.enemy_fleet[attack.defender],
                        attacker_hp=player_hp[attack.attacker],
                        defender_hp=enemy_hp[attack.defender],
                        attack=attack
                    )
                )

            if attack.side != SIDE.ENEMY:
                enemy_hp[attack.defender] -= int(attack.damage)
            else:
                if attack.phase in {PHASE.FRIENDLY_AIRBATTLE, PHASE.FRIENDLY_SHELLING}:
                    ff_hp[attack.defender] -= int(attack.damage)
                else:
                    player_hp[attack.defender] -= int(attack.damage)

        return ret