from typing import List

from data.static import SIDE
from battle.static import PHASE
from api_parsing.utils import is_special_attack, get_special_attack_attacker_index, is_friendly_fleet_attack
from api_parsing.static import (HOUGEKI_API, HougekiAttack, MIDNIGHT_API, MidnightAttack, RaigekiAttack,
    RAIGEKI_API_SIDE_ENEMY, RAIGEKI_API_SIDE_PLAYER, KoukuAttack, COMBINED_FLEET_PAD, KOUKU_API_SIDE_FRIENDLY,
    KOUKU_API_SIDE_ENEMY, HITSTATUS, SUPPORT_API, KOUKU_API)

def parse_hougeki(rawapi: dict, phase: str) -> List[HougekiAttack]:
    """Parses the hougeki shelling API into an array of attacks.

    Each field of the raw API is an array corresponding to each attack.
    Some fields contain arrays (see below comments) for multi-hit attacks.
    
    For special attacks, the attacker has to be re-mapped.
    """
    return [
        HougekiAttack(
            # Splice attack into correct attackers for special attacks
            attacker=attacker if not is_special_attack(cutin) else get_special_attack_attacker_index(cutin, idx),
            defender=defender[idx],
            damage=damage,
            hitstatus=hitstatus[idx],
            phase=phase,
            cutin=cutin,
            cutin_equips=cutin_equips,
            side=side
        ) for attacker, defender, damage_array, hitstatus, cutin, cutin_equips, side in zip(
            rawapi[HOUGEKI_API.ATTACKER],    # Attacker
            rawapi[HOUGEKI_API.DEFENDER],    # Defender array
            rawapi[HOUGEKI_API.DAMAGE],      # Damage array
            rawapi[HOUGEKI_API.HITSTATUS],   # Hitstatus array
            rawapi[HOUGEKI_API.CUTIN],       # Cutin ID
            rawapi[HOUGEKI_API.CUTIN_EQUIP], # Cutin equip array
            rawapi[HOUGEKI_API.SIDE],        # Attacker side
        # We iterate over the damage array to seperate multiple defenders and hitstatus for each attack
        ) for idx, damage in enumerate(damage_array)
    ]

def parse_midnight(rawapi: dict, phase: str) -> List[MidnightAttack]:
    """Parses the night battle shelling API into an array of attacks.

    Each field of the raw API is an array corresponding to each attack.
    Some fields contain arrays (see below comments) for multi-hit attacks.

    For special attacks, the attacker has to be re-mapped.

    The night carrier flag is true if the attacker uses the night fighter/bomber attack.
    The damage array becomes [actual_hit, -1, -1] in this case, so the -1 entries have to be removed.
    """
    if phase == PHASE.FRIENDLY_SHELLING:
        rawapi = rawapi[PHASE.NIGHT_SHELLING]
    return [
        MidnightAttack(
            attacker=attacker if not is_special_attack(cutin) else get_special_attack_attacker_index(cutin, idx),
            defender=defender,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            night_carrier=night_carrier,
            cutin=cutin,
            cutin_equips=cutin_equips,
            side=side if not is_friendly_fleet_attack(phase, side) else SIDE.FRIEND
        ) for attacker, defender_array, damage_array, hitstatus_array, night_carrier, cutin, cutin_equips, side in zip(
            rawapi[MIDNIGHT_API.ATTACKER],      # Attacker
            rawapi[MIDNIGHT_API.DEFENDER],      # Defender array
            rawapi[MIDNIGHT_API.DAMAGE],        # Damage array
            rawapi[MIDNIGHT_API.HITSTATUS],     # Hitstatus array
            rawapi[MIDNIGHT_API.NIGHT_CARRIER], # Night carrier flag
            rawapi[MIDNIGHT_API.CUTIN],         # Cutin ID
            rawapi[MIDNIGHT_API.CUTIN_EQUIP],   # Cutin equip array
            rawapi[MIDNIGHT_API.SIDE]           # Attacker side
        # -1 may appear in the damage array with carrier night attacks, so filter those out
        ) for defender, damage, hitstatus in zip(defender_array, damage_array, hitstatus_array) if damage > -1
    ]

def parse_raigeki(rawapi: dict, phase: str) -> List[RaigekiAttack]:
    """Parses the torpedo phase API into an array of attacks.

    Each field of the raw API is an array with indices corresponding to the ship in the fleet.
    E.g. rawapi[RAIGEKI_API_SIDE_PLAYER.DEFENDER][0] points to the defender being attacked by the first player ship.
    There are no inner arrays in the field value, aka no multi-hit torpedoes.

    The fields are repeated for each side.
    If the defender value is -1, it means that the attacker did not participate in this torpedo phase.
    """
    return [
        RaigekiAttack(
            attacker=idx,
            defender=defender,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.PLAYER
        ) for idx, (defender, damage, hitstatus) in enumerate(zip(
            rawapi[RAIGEKI_API_SIDE_PLAYER.DEFENDER],
            rawapi[RAIGEKI_API_SIDE_PLAYER.DAMAGE],
            rawapi[RAIGEKI_API_SIDE_PLAYER.HITSTATUS]
        )) if defender > -1 # Defender value -1 means for this attacker index, the attacker does not take part in the torpedo phase.
    ] + [
        RaigekiAttack(
            attacker=idx,
            defender=defender,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.ENEMY
        ) for idx, (defender, damage, hitstatus) in enumerate(zip(
            rawapi[RAIGEKI_API_SIDE_ENEMY.DEFENDER],
            rawapi[RAIGEKI_API_SIDE_ENEMY.DAMAGE],
            rawapi[RAIGEKI_API_SIDE_ENEMY.HITSTATUS]
        )) if defender > -1
    ]

def parse_kouku(rawapi: dict, phase: str, wave=None):
    ret = []
    if KOUKU_API.STAGE_FLAG in rawapi and rawapi[KOUKU_API.STAGE_FLAG][2] == 1:
        ret += parse_kouku_friendly(rawapi[KOUKU_API.STAGE3], phase, wave, False)
        if KOUKU_API_SIDE_ENEMY.DAMAGE in rawapi[KOUKU_API.STAGE3]:
            ret += parse_kouku_enemy(rawapi[KOUKU_API.STAGE3], phase, wave, False)

        if KOUKU_API.STAGE3_COMBINED in rawapi:
            if KOUKU_API_SIDE_FRIENDLY.DAMAGE in rawapi[KOUKU_API.STAGE3_COMBINED]:
                ret += parse_kouku_friendly(rawapi[KOUKU_API.STAGE3_COMBINED], phase, wave, True)
            if KOUKU_API_SIDE_ENEMY.DAMAGE in rawapi[KOUKU_API.STAGE3_COMBINED]:
                ret += parse_kouku_enemy(rawapi[KOUKU_API.STAGE3_COMBINED], phase, wave, True)

    return ret

def parse_kouku_friendly(rawapi: dict, phase: str, wave=None, combined=False):
    return [
        KoukuAttack(
            defender=ship_index + (COMBINED_FLEET_PAD if combined else 0),
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if hitstatus_critical else HITSTATUS.HIT,
            phase=phase,
            db=db_flag,
            tb=tb_flag,
            side=SIDE.PLAYER if phase != PHASE.FRIENDLY_AIRBATTLE else SIDE.FRIEND,
            wave=wave,
            special_bomber=special_bomber
        ) for ship_index, (damage, hitstatus_critical, db_flag, tb_flag, special_bomber) in enumerate(zip(
            rawapi[KOUKU_API_SIDE_FRIENDLY.DAMAGE],
            rawapi[KOUKU_API_SIDE_FRIENDLY.HITSTATUS],
            rawapi[KOUKU_API_SIDE_FRIENDLY.DIVE_BOMBING],
            rawapi[KOUKU_API_SIDE_FRIENDLY.TORPEDO_BOMBING],
            rawapi[KOUKU_API_SIDE_FRIENDLY.SPECIAL_BOMBER])
        ) if db_flag or tb_flag
    ]

def parse_kouku_enemy(rawapi: dict, phase: str, wave=None, combined=False):
    return [
        KoukuAttack(
            defender=ship_index + (COMBINED_FLEET_PAD if combined else 0),
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if hitstatus_critical else HITSTATUS.HIT,
            phase=phase,
            db=db_flag,
            tb=tb_flag,
            side=SIDE.ENEMY,
            wave=wave,
            special_bomber=special_bomber,
        ) for ship_index, (damage, hitstatus_critical, db_flag, tb_flag, special_bomber) in enumerate(zip(
            rawapi[KOUKU_API_SIDE_ENEMY.DAMAGE],
            rawapi[KOUKU_API_SIDE_ENEMY.HITSTATUS],
            rawapi[KOUKU_API_SIDE_ENEMY.DIVE_BOMBING],
            rawapi[KOUKU_API_SIDE_ENEMY.TORPEDO_BOMBING],
            rawapi[KOUKU_API_SIDE_ENEMY.SPECIAL_BOMBER])
        ) if db_flag or tb_flag
    ]

def parse_support_kouku(rawapi: dict, phase: str):
    if not (KOUKU_API.STAGE_FLAG in rawapi and rawapi[KOUKU_API.STAGE_FLAG][2] == 1):
        return []
    rawapi = rawapi[KOUKU_API.STAGE3]

    return [
        KoukuAttack(
            defender=ship_index,
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if hitstatus_critical else HITSTATUS.HIT,
            phase=phase,
            db=db_flag,
            tb=tb_flag,
            side=SIDE.PLAYER if phase != PHASE.FRIENDLY_AIRBATTLE else SIDE.FRIEND,
            wave=None,
            special_bomber=[]
        ) for ship_index, (damage, hitstatus_critical, db_flag, tb_flag) in enumerate(zip(
            rawapi[KOUKU_API_SIDE_FRIENDLY.DAMAGE],
            rawapi[KOUKU_API_SIDE_FRIENDLY.HITSTATUS],
            rawapi[KOUKU_API_SIDE_FRIENDLY.DIVE_BOMBING],
            rawapi[KOUKU_API_SIDE_FRIENDLY.TORPEDO_BOMBING])
        ) if db_flag or tb_flag
    ]


def parse_support_hougeki(rawapi: dict, phase: str):
    return [HougekiAttack(
            attacker=None,
            defender=ship_idx,
            damage=damage,
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.PLAYER,
            cutin=None,
            cutin_equips=None,
        ) for ship_idx, (damage, hitstatus) in enumerate(zip(rawapi[HOUGEKI_API.DAMAGE], rawapi[HOUGEKI_API.HITSTATUS]))
        if hitstatus > 0
    ]


def parse_support(rawapi: dict, phase: str):
    if SUPPORT_API.HOURAI in rawapi and rawapi[SUPPORT_API.HOURAI]:
        return parse_support_hougeki(rawapi[SUPPORT_API.HOURAI], phase)
    elif SUPPORT_API.KOUKU in rawapi and rawapi[SUPPORT_API.KOUKU]:
        return parse_support_kouku(rawapi[SUPPORT_API.KOUKU], phase)
    return []
