import numpy as np
from typing import List, Union
from battle.Hougeki import Hougeki
from battle.Kouku import Kouku, LBKouku
from battle.Raigeki import Raigeki
from battle.Midnight import Midnight
from battle.Support import SupportHourai, SupportKouku
from battle.static import HougekiAttack, HouraiAttackSupport, KoukuAttack, KoukuAttackLB, KoukuAttackSupport, RaigekiAttack, MidnightAttack
from objects.Battle import Battle
from objects.Ship import EnemyShip, PlayerShip
from objects.static import BATTLEORDER, PHASE, SIDE, STYPE
from utils import fetch_ship_master


def calculate_damage_range(attacker: PlayerShip, defender: EnemyShip, num: float):
    armor = defender.ar + defender.fetch_equipment_total_stats("souk")
    ammo_percent = attacker.ammo / \
        fetch_ship_master(attacker.id)["api_bull_max"]
    ram = 1 if ammo_percent >= 0.5 else ammo_percent * 2

    if defender.is_submarine():
        de_bonus = 1 if attacker.stype == STYPE.DE else 0

        # Type 95 DC
        if attacker.has_equip(226):
            armor -= np.sqrt(2) + de_bonus

        # Type 2 DC
        if attacker.has_equip(227):
            armor -= np.sqrt(5) + de_bonus

        armor = max(armor, 1)

    min_val = int((num - armor * 0.7) * ram)
    max_val = int((num - armor * 0.7 - (armor - 1) * 0.6) * ram)
    return max_val, min_val


def reversed_attack_power(attacker: PlayerShip, defender: EnemyShip, actual_damage: int):
    armor = defender.ar + defender.fetch_equipment_total_stats("souk")
    ammo_percent = attacker.ammo / \
        fetch_ship_master(attacker.id)["api_bull_max"]
    ram = 1 if ammo_percent >= 0.5 else ammo_percent * 2

    if defender.is_submarine():
        de_bonus = 1 if attacker.stype == STYPE.DE else 0

        # Type 95 DC
        if attacker.has_equip(226):
            armor -= np.sqrt(2) + de_bonus

        # Type 2 DC
        if attacker.has_equip(227):
            armor -= np.sqrt(5) + de_bonus

        armor = max(armor, 1)

    min_pow = int(int(actual_damage / ram) + armor * 0.7)
    max_pow = int(int(actual_damage / ram) + armor * 0.7 + (armor - 1) * 0.6)

    return min_pow, max_pow


def is_scratch(defender: EnemyShip, damage: int):
    hp = max(defender.hp[0], 0)
    return damage <= int(hp * 0.06 + (hp - 1) * 0.08)


def handle_attack(attack: HougekiAttack, battle: Battle):
    defender = (battle.eship_mapping if attack.side != SIDE.ENEMY else battle.fship_mapping if attack.side ==
                SIDE.PLAYER else battle.friendly_fleet.ships)[attack.defender]
    defender.hp[0] -= int(attack.damage)


def handle_battle(battle: Battle, rawapi: dict) -> List[Union[HougekiAttack, HouraiAttackSupport, KoukuAttack, KoukuAttackLB, KoukuAttackSupport, RaigekiAttack, MidnightAttack]]:
    phases = BATTLEORDER.get(battle.battletype)
    attacks = [
        attack for phase_attacks in ([phase_handlers[phase](rawapi.get(phase), phase, battle) for phase in phases]) for attack in phase_attacks
    ]
    return attacks


def lb_handler(rawapi: Union[dict, list, None], phase: str, battle: Battle) -> List[KoukuAttackLB]:
    res = []

    if rawapi is None:
        return res

    # Normal LB wave
    if isinstance(rawapi, list):
        res = [
            LBKouku(
                rawapi=wave_raw["api_stage3"],
                phase=phase,
                wave=wave_idx
            ) for wave_idx, wave_raw in enumerate(rawapi) if wave_raw.get("api_stage3") is not None
        ]
        if battle.ecombined:
            res += [
                LBKouku(
                    rawapi=wave_raw["api_stage3_combined"],
                    phase=phase,
                    wave=wave_idx,
                    combined=True
                ) for wave_idx, wave_raw in enumerate(rawapi) if wave_raw.get("api_stage3_combined") is not None
            ]
        return [attack for wave_attacks in res for attack in wave_attacks]

    # Jet phase
    else:
        if rawapi.get("api_stage3") is not None:
            res += LBKouku(
                rawapi=rawapi["api_stage3"],
                phase=phase,
                wave=-1
            )

            if rawapi.get("api_stage3_combined") is not None:
                res += LBKouku(
                    rawapi=rawapi["api_stage3_combined"],
                    phase=phase,
                    wave=-1,
                    combined=True
                )
        return res


def kouku_handler(rawapi: Union[dict, None], phase: str, battle: Battle) -> List[KoukuAttack]:
    res = []

    if rawapi is None:
        return res
    if rawapi.get("api_stage3"):

        if phase == PHASE.FRIENDLY_AIRBATTLE:
            res += Kouku(rawapi["api_stage3"], phase, side=SIDE.FRIEND)
            if battle.ecombined:
                res += Kouku(rawapi["api_stage3_combined"],
                             phase, side=SIDE.FRIEND)

        res += Kouku(rawapi["api_stage3"], phase, side=SIDE.PLAYER)
        res += Kouku(rawapi["api_stage3"], phase, side=SIDE.ENEMY)

        if battle.ecombined:
            res += Kouku(rawapi["api_stage3_combined"],
                         phase, side=SIDE.PLAYER)

        if battle.fcombined:
            res += Kouku(rawapi["api_stage3_combined"], phase, side=SIDE.ENEMY)

    return res


def support_handler(rawapi: Union[dict, None], phase: str, battle: Battle):

    if rawapi is None:
        return []

    if rawapi.get("api_support_hourai"):
        return SupportHourai(rawapi["api_support_hourai"], phase=phase)
    else:
        if rawapi["api_support_airatack"]["api_stage_flag"][2] == 1:
            return SupportKouku(rawapi["api_support_airatack"]["api_stage3"], phase)
        else:
            return []


def hougeki_handler(rawapi: Union[dict, None], phase: str, battle: Battle):
    if rawapi is None:
        return []

    return Hougeki(rawapi, phase)


def raigeki_handler(rawapi: Union[dict, None], phase: str, battle: Battle):
    if rawapi is None:
        return []

    return Raigeki(rawapi, phase)


def midnight_handler(rawapi: Union[dict, None], phase: str, battle: Battle):
    if rawapi is None:
        return []
    if phase == PHASE.FRIENDLY_SHELLING:
        rawapi = rawapi["api_hougeki"]
    return Midnight(rawapi, phase)


phase_handlers = {
    PHASE.LAND_BASE_JET: lb_handler,
    PHASE.JET: kouku_handler,
    PHASE.LAND_BASE: lb_handler,
    PHASE.FRIENDLY_AIRBATTLE: kouku_handler,
    PHASE.AIRBATTLE: kouku_handler,
    PHASE.AIRBATTLE2: kouku_handler,
    PHASE.SUPPORT: support_handler,
    PHASE.OPENING_ASW: hougeki_handler,
    PHASE.OPENING_TORPEDO: raigeki_handler,
    PHASE.SHELLING: hougeki_handler,
    PHASE.SHELLING2: hougeki_handler,
    PHASE.SHELLING3: hougeki_handler,
    PHASE.CLOSING_TORPEDO: raigeki_handler,

    PHASE.FRIENDLY_SHELLING: midnight_handler,
    PHASE.NIGHT_SUPPORT: support_handler,
    PHASE.NIGHT_SHELLING: midnight_handler,
    PHASE.NIGHT_SHELLING2: midnight_handler,
}
