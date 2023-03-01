from dataclasses import dataclass
from typing import List

COMBINED_FLEET_PAD = 6

class HITSTATUS:
    MISS = 0
    HIT = 1
    CRITICAL = 2

@dataclass
class HougekiAttack:
    attacker: int
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
    CUTIN = "api_sp_list"
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
    DEFENDER = "api_erai"
    DAMAGE = "api_eydam"
    HITSTATUS = "api_ecl"
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
    wave: int = None
    special_bomber: List[int] = None


class KOUKU_API_SIDE_FRIENDLY:
    DAMAGE = "api_edam"
    HITSTATUS = "api_ecl_flag"
    DIVE_BOMBING = "api_ebak_flag"
    TORPEDO_BOMBING = "api_erai_flag"
    SPECIAL_BOMBER = "api_e_sp_list"


class KOUKU_API_SIDE_ENEMY:
    DAMAGE = "api_fdam"
    HITSTATUS = "api_fcl_flag"
    DIVE_BOMBING = "api_fbak_flag"
    TORPEDO_BOMBING = "api_frai_flag"
    SPECIAL_BOMBER = "api_f_sp_list"

class SUPPORT_API:
    HOURAI = "api_support_hourai"
    KOUKU = "api_support_airatack"

class KOUKU_API:
    STAGE_FLAG = "api_stage_flag"
    STAGE3 = "api_stage3"
    STAGE3_COMBINED = "api_stage3_combined"