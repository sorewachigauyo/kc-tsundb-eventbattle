from dataclasses import dataclass
from typing import List

COMBINED_FLEET_PAD = 6

@dataclass
class HougekiAttack:
    attack: int
    defender: int
    damage: float
    hitstatus: int
    phase: str
    cutin: int
    cutin_equips: List[int]
    side: int


class HOUGEKI_API:
    ATTACKER = "api_at_list"
    DEFENDER = "api_df_list"
    DAMAGE = "api_damage"
    HITSTATUS = "api_cl_list"
    CUTIN = "api_at_type"
    CUTIN_EQUIP = "api_si_list"
    SIDE = "api_at_eflag"


@dataclass
class MidnightAttack:
    attacker: int
    defender: int
    damage: float
    hitstatus: int
    phase: str
    night_carrier: int
    cutin: int
    cutin_equips: list
    side: int


class MIDNIGHT_API:
    ATTACKER = "api_at_list"
    DEFENDER = "api_df_list"
    DAMAGE = "api_damage"
    HITSTATUS = "api_cl_list"
    NIGHT_CARRIER = "api_n_mother_list"
    CUTIN = "api_sp_type"
    CUTIN_EQUIP = "api_si_list"
    SIDE = "api_at_eflag"


@dataclass
class RaigekiAttack:
    attacker: int
    defender: int
    damage: float
    hitstatus: int
    phase: str
    side: int


class RAIGEKI_API_SIDE_PLAYER:
    DEFENDER = "api_frai"
    DAMAGE = "api_fydam"
    HITSTATUS = "api_fcl"
    DAMAGE_TAKEN = "api_fdam"


class RAIGEKI_API_SIDE_ENEMY:
    DEFENDER = "api_frai"
    DAMAGE = "api_fydam"
    HITSTATUS = "api_fcl"
    DAMAGE_TAKEN = "api_edam"


@dataclass
class KoukuAttack:
    defender: int
    damage: float
    hitstatus: int
    phase: str
    db: bool
    tb: bool
    side: int


class KOUKU_API_SIDE_FRIENDLY:
    DAMAGE