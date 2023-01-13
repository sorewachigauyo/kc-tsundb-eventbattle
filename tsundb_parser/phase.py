from typing import List

from data.static import SIDE
from tsundb_parser.utils import is_special_attack, get_special_attack_attacker_index, is_friendly_fleet_attack
from tsundb_parser.static import (HOUGEKI_API, HougekiAttack, MIDNIGHT_API, MidnightAttack, RaigekiAttack,
    RAIGEKI_API_SIDE_ENEMY, RAIGEKI_API_SIDE_PLAYER, KoukuAttack, COMBINED_FLEET_PAD)

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
    return [
        MidnightAttack(
            attacker=attacker if not is_special_attack(cutin) else get_special_attack_attacker_index(cutin, idx),
            defender=defender[idx],
            damage=damage,
            hitstatus=hitstatus[idx],
            phase=phase,
            night_carrier=night_carrier,
            cutin=cutin,
            cutin_equips=cutin_equips,
            side=side if not is_friendly_fleet_attack(phase, side) else SIDE.FRIEND
        ) for attacker, defender, damage_array, hitstatus, night_carrier, cutin, cutin_equips, side in zip(
            rawapi[MIDNIGHT_API.ATTACKER],      # Attacker
            rawapi[MIDNIGHT_API.DEFENDER],      # Defender array
            rawapi[MIDNIGHT_API.DAMAGE],        # Damage array
            rawapi[MIDNIGHT_API.HITSTATUS],     # Hitstatus array
            rawapi[MIDNIGHT_API.NIGHT_CARRIER], # Night carrier flag
            rawapi[MIDNIGHT_API.CUTIN],         # Cutin ID
            rawapi[MIDNIGHT_API.CUTIN_EQUIP],   # Cutin equip array
            rawapi[MIDNIGHT_API.SIDE]           # Attacker side
        # -1 may appear in the damage array with carrier night attacks, so filter those out
        ) for idx, damage in enumerate(damage_array) if damage > -1
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

def parse_kouku(rawapi: dict, phase: str, side: int, combined=False):
    dmg_key, critical_key, bak_flag_key, rai_flag_key = KOUKU_SIDE_TERMS[side]
    return [
        KoukuAttack(
            defender=ship_idx + (COMBINED_FLEET_PAD if combined else 0),
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if rawapi[critical_key][ship_idx] else HITSTATUS.HIT,
            phase=phase,
            db=rawapi[bak_flag_key][ship_idx] == 1,
            tb=rawapi[rai_flag_key][ship_idx] == 1,
            side=side
        ) for ship_idx, damage in enumerate(rawapi[dmg_key])
        if rawapi[rai_flag_key][ship_idx] or rawapi[bak_flag_key][ship_idx]
    ]
