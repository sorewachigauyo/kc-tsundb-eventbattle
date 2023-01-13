from data.static_battle import SPECIAL_ATTACKS, SPECIAL_ATTACK_ATTACKER_MAPPING, PHASE
from data.static import SIDE

def is_special_attack(cutin_id: int) -> bool:
    return cutin_id in SPECIAL_ATTACKS

def get_special_attack_attacker_index(cutin_id: int, attack_index: int) -> int:
    return SPECIAL_ATTACK_ATTACKER_MAPPING[cutin_id][attack_index]

def is_friendly_fleet_attack(phase: str, side: int) -> bool:
    return phase == PHASE.FRIENDLY_SHELLING and side == SIDE.PLAYER
