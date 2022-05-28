import numpy as np
from battle.Hougeki import apply_postcap_target_special_modifier, determine_combined_fleet_factor
from battle.static import DAMAGE_MODIFIER_RAIGEKI, ENGAGEMENT_MODIFIERS, HITSTATUS, RAIGEKI_CAP, RAIGEKI_FORMATION_MODIFIER, RaigekiAttack
from objects.Battle import Battle
from objects.Ship import EnemyShip, PlayerShip
from objects.static import SIDE
from utils import get_gear_improvement_stats

def Raigeki(rawapi: dict, phase: str):
    return [
        RaigekiAttack(
            attacker=idx,
            defender=defender,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.PLAYER
        ) for idx, (defender, damage, hitstatus) in enumerate(zip(
            rawapi["api_frai"],
            rawapi["api_fydam"],
            rawapi["api_fcl"]
        )) if defender > -1
    ] + [
        RaigekiAttack(
            attacker=idx,
            defender=defender,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.ENEMY
        ) for idx, (defender, damage, hitstatus) in enumerate(zip(
            rawapi["api_erai"],
            rawapi["api_eydam"],
            rawapi["api_ecl"]
        )) if defender > -1
    ]

def process_raigeki(attack: RaigekiAttack, battle: Battle):
    attacker = battle.fship_mapping[attack.attacker]
    defender = battle.eship_mapping[attack.defender]

    num = calculate_base_attack_power(attacker, defender)

    # Engagement mod
    engagement_modifier = ENGAGEMENT_MODIFIERS[battle.engagement]
    num *= engagement_modifier

    # Formation mod
    formation_modifier = RAIGEKI_FORMATION_MODIFIER[attacker.fleet.formation]
    num *= formation_modifier

    # Damage mod
    hpercent = attacker.hp[0] / attacker.hp[1]
    if hpercent == 1:
        damage_modifier = DAMAGE_MODIFIER_RAIGEKI[4]
    elif hpercent <= 0.25:
        damage_modifier = DAMAGE_MODIFIER_RAIGEKI[0]
    elif hpercent <= 0.5:
        damage_modifier = DAMAGE_MODIFIER_RAIGEKI[1]
    else:
        damage_modifier = DAMAGE_MODIFIER_RAIGEKI[2]
    num *= damage_modifier

    # Apply damage cap
    if num > RAIGEKI_CAP:
        num = RAIGEKI_CAP + np.sqrt(num - RAIGEKI_CAP)

    # Apply enemy special modifiers if needed
    num = apply_postcap_target_special_modifier(int(num), attacker, defender)

    # Critical
    if attack.hitstatus == HITSTATUS.CRITICAL:
        num *= 1.5

    return attacker, defender, int(num)

def calculate_base_attack_power(attacker: PlayerShip, defender: EnemyShip):
    cf_factor = determine_combined_fleet_factor(attacker, defender)
    return attacker.visible_stats["tp"] + cf_factor + get_gear_improvement_stats(attacker)["tp"] + 5
