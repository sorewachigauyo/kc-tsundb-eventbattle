from dataclasses import dataclass

ANTI_LAND_BOMBER_IDS = [64,148,233,277,305,306,319,320,391,392,420,421]
BOMBER_TYPE2_IDS = [7, 8, 11, 41, 57, 58]
PROFICIENCY_MODIFIER = [0, 1, 2, 3, 4, 7, 7, 10]
PROFICIENCY_EXPERIENCE = [9, 24, 39, 54, 69, 84, 99, 120]

PT_IMP_IDS = [1637, 1638, 1639, 1640]
PT_IMP_SMALL_GUN_MODIFIER = [1, 1.4, 2.1]
PT_IMP_SECONDARY_GUN_MODIFIER = 1.3
PT_IMP_BOMBER_MODIFIER = [1, 1.4, 1.82]
PT_IMP_SEAPLANE_MODIFIER = 1.2
PT_IMP_AA_GUN_MODIFIER = [1, 1.2, 1.44]
PT_IMP_LOOKOUT_MODIFIER = 1.1
PT_IMP_BOAT_MODIFIER = [1, 1.2, 1.32]

SUMMER_BATTLESHIP_PRINCESS_IDS = [1696, 1697, 1698]
SUMMER_BATTLESHIP_SEAPLANE_MODIFIER = 1.1
SUMMER_BATTLESHIP_AP_MODIFIER = 1.2

SUMMER_HEAVY_CRUISER_PRINCESS_IDS = [1705, 1706, 1707]
SUMMER_HEAVY_CRUISER_PRINCESS_SEAPLANE_MODIFIER = 1.15
SUMMER_HEAVY_CRUISER_AP_MODIFIER = 1.1

SDH_IDS = [
        1653, 1654, 1655,       # Base
        1656, 1657, 1658,       # Damaged
        1809, 1810, 1811,       # Vacation
        1812, 1813, 1814,       # Vacation Damaged
        1921, 1922, 1923,       # B
        1924, 1925, 1926,       # B damaged
        1933, 1934, 1935,       # B landing mode
        1936, 1937, 1938,       # B landing mode damaged
        1994,                   # B
        1995,                   # B Damaged
        2015, 2016, 2017, 2018, # B vacation
        2019, 2020, 2021, 2022, # B vacation damaged
        2084, 2086, 2088,       # C
        2085, 2087, 2089,       # C damaged
]
SDH_WG42_MODIFIER = [1, 1.25, 1.625]
SDH_TYPE4_ROCKET_MODIFIER = [1, 1.2, 1.68]
SDH_MORTAR_MODIFIER = [1, 1.15, 1.38]
SDH_DAIHATSU_MODIFIER = 1.7
SDH_TOKU_DAIHATSU_MODIFIER = 1.2
SDH_HONI_T89_MODIFIER = [1, 1.3, 2.08]
SDH_M4A1_MODIFIER = 1.2
SDH_KAMI_MODIFIER = [1, 1.7, 2.55]
SDH_PANZER_MODIFIER = 1.3
SDH_AB_ARMED_DAIHATSU_MODIFIER = [1, 1.5, 1.65]

HOUGEKI_CAP = 220
YASEN_CAP = 360
RAIGEKI_CAP = 180
DEFAULT_CAP = 170

HOUGEKI_FORMATION_MODIFIER = [0, 1.0, 0.8, 0.7, 0.75, 0.6, 1, 0, 0, 0, 0, 0.8, 1.0, 0.7, 1.1]
HOUGEKI_FORMATION_MODIFIER_ASW = [0, 0.6, 0.8, 1.2, 1.1 , 1.3, 1, 0, 0, 0, 0, 1.3, 1.1, 1.0, 0.7]
HOUGEKI_CUTIN_MODIFIER = {
    0: 1,
    2: 1.2,
    3: 1.1,
    4: 1.2,
    5: 1.3,
    6: 1.5,
    7: 1.15,
    100: 2,
    101: 1.4,
    102: 1.4,
    103: 1.3,
    200: 1.35,
    201: 1.3,
    300: 1.2,
    301: 1.2,
    302: 1.2
}

DEFAULT_DAMAGE_MODIFIER = [0.4, 0.7, 1, 1, 1]

class HITSTATUS:
    MISS = 0
    HIT = 1
    CRITICAL = 2

class ATTACKERSIDE:
    PLAYER = 0
    ENEMY = 1

class ENGAGEMENT:
    PARALLEL = 1
    HEAD_ON = 2
    GREEN_T = 3
    RED_T = 4

ENGAGEMENT_MODIFIERS = [0, 1, 0.8, 1.2, 0.6]

class HOUGEKI_CUTIN:
    SINGLE_ATTACK = 0
    LASER = 1
    DOUBLE_HougekiAttack = 2
    MAIN_SECONDARY = 3
    MAIN_RADAR = 4
    MAIN_AP = 5
    MAIN_MAIN = 6
    CARRIER_CUTIN = 7
    NELSON_TOUCH = 100
    NAGATO_SPECIAL = 101
    MUTSU_SPECIAL = 102
    COLORADO_SPECIAL = 103
    ZUIUN_MULTI_ANGLE = 200
    AIR_SEA_MULTI_ANGLE = 201
    SUBFLEET_SPECIAL_1 = 300
    SUBFLEET_SPECIAL_2 = 301
    SUBFLEET_SPECIAL_3 = 302


@dataclass
class HougekiAttack:
    attacker: int
    defender: list
    damage: list
    hitstatus: int
    phase: str
    cutin: int
    cutin_equips: list
    side: int
