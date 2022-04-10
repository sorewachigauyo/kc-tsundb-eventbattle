from typing import Union
from battle.Hougeki import Hougeki
from battle.Kouku import Kouku, LBKouku
from battle.Raigeki import Raigeki
from battle.Yasen import Yasen
from battle.static import HougekiAttack, KoukuAttack, KoukuAttackLB, RaigekiAttack, YasenAttack
from objects.Battle import Battle
from objects.Ship import EnemyShip, PlayerShip
from objects.static import BATTLEORDER, PHASE, SIDE
from utils import fetch_ship_master

def calculate_damage_range(attacker: PlayerShip, defender: EnemyShip, num: float):
    armor = defender.ar + defender.fetch_equipment_total_stats("souk")
    ammo_percent = attacker.ammo / fetch_ship_master(attacker.id)["api_bull_max"]
    ram = 1 if ammo_percent >= 0.5 else ammo_percent * 2

    min_val = int((num - armor * 0.7) * ram)
    max_val = int((num - armor * 0.7 - (armor - 1) * 0.6) * ram)
    return min_val, max_val

def is_scratch(defender: EnemyShip, damage: float):
    return damage >= int(defender.hp[0] * 0.06 + (defender.hp[0] - 1) * 0.08)

def handle_attack(attack: Union[HougekiAttack, RaigekiAttack, KoukuAttack, KoukuAttackLB], battle):
    defenders = (battle.eship_mapping if attack.side == SIDE.ENEMY else battle.fship_mapping)[attack.defender]

    if isinstance(attack, HougekiAttack):
        for idx, defender_id in enumerate(attack.defender):
            defenders[defender_id].hp[0] -= attack.damage[idx]
    else:
        defenders[attack.defender].id -= attack.damage

o = {
    PHASE.LAND_BASE_JET: LBKouku,
    PHASE.JET: Kouku,
    PHASE.LAND_BASE: LBKouku,
    PHASE.FRIENDLY_AIRBATTLE: Kouku,
    PHASE.AIRBATTLE: Kouku,
    PHASE.AIRBATTLE2: Kouku,
    PHASE.SUPPORT: Hougeki,
    PHASE.OPENING_ASW: Hougeki,
    PHASE.OPENING_TORPEDO: Raigeki,
    PHASE.SHELLING: Hougeki,
    PHASE.SHELLING2: Hougeki,
    PHASE.SHELLING3: Hougeki,
    PHASE.CLOSING_TORPEDO: Raigeki,

    PHASE.FRIENDLY_SHELLING: Yasen,
    PHASE.NIGHT_SUPPORT: Hougeki,
    PHASE.NIGHT_SHELLING: Yasen,
    PHASE.NIGHT_SHELLING2: Yasen,
}

def handle_battle(battle: Battle, rawapi: dict):
    phases = BATTLEORDER.get(battle.type)
    attacks = [

    ]

class PHASE:
    # Day
    LAND_BASE_JET = "api_air_base_injection"
    JET = "api_injection_kouku"
    LAND_BASE = "api_air_base_attack"
    FRIENDLY_AIRBATTLE = "api_friendly_kouku"
    AIRBATTLE = "api_kouku"
    AIRBATTLE2 = "api_kouku2"
    SUPPORT = "api_support_info"
    OPENING_ASW = "api_opening_taisen"
    OPENING_TORPEDO = "api_opening_atack"
    SHELLING = "api_hougeki1"
    SHELLING2 = "api_hougeki2"
    SHELLING3 = "api_hougeki3"
    CLOSING_TORPEDO = "api_raigeki"

    # Night
    FRIENDLY_SHELLING = "api_friendly_battle"
    NIGHT_SUPPORT = "api_n_support_info"
    NIGHT_SHELLING = "api_hougeki"
    NIGHT_SHELLING1 = "api_n_hougeki1"
    NIGHT_SHELLING2 = "api_n_hougeki2"