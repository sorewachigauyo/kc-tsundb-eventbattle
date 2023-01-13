from dataclasses import dataclass
from typing import List, Union, Dict

class COUNT_TYPE:
    SINGLE = "single"
    MULTIPLE = "multiple"
    DISTINCT = "distinct" # Used for synergy flags so that they are not re-appleid
    COUNT = "byCount"


@dataclass
class BonusDefinition:
    count: int = 0
    byShip: Union[Dict, List[Dict]] = None
    byClass: Union[Dict, List[Dict]] = None
    byNation: Union[Dict, List[Dict]] = None
    starsDist: List = None


SYNERGY_GEAR_KEY = "synergyGears"
COUNTRY_CTYPE_MAP_KEY = "countryCtypeMap"

@dataclass
class StatBonus:
    firepower: int = 0
    armor: int = 0
    torpedo: int = 0
    evasion: int = 0
    anti_air: int = 0
    anti_sub: int = 0
    line_of_sight: int = 0
    accuracy: int = 0
    range: int = 0
    speed: int = 0
    dive_bombing: int = 0

    def __add__(self, bonus):
        return StatBonus(
            firepower=self.firepower + bonus.firepower,
            armor=self.armor + bonus.armor,
            torpedo=self.torpedo + bonus.torpedo,
            evasion=self.evasion + bonus.evasion,
            anti_air=self.anti_air + bonus.anti_air,
            anti_sub=self.anti_sub + bonus.anti_sub,
            line_of_sight=self.line_of_sight + bonus.line_of_sight,
            accuracy=self.accuracy + bonus.accuracy,
            range=self.range + bonus.range,
            speed=self.speed + bonus.speed,
            dive_bombing=self.dive_bombing + bonus.dive_bombing
        )

@dataclass
class SynergyBonus(StatBonus):
    count_type: str = None
    flags: List[str] = None
    count_required: int = None



@dataclass
class GearBonus(StatBonus):
    count_type: str = None
    count_cap: int = 0

    required_ship_type: List[int] = None
    required_class_type: List[int] = None
    required_ship_id: List[int] = None
    required_ship_origin: List[int] = None
    required_nation: List[str] = None
    

    distinct_equip_id: List[int] = None
    excluded_ship_id: List[int] = None
    excluded_ship_type: List[int] = None
    excluded_class_type: List[int] = None
    excluded_ship_origin: List[int] = None

    minimum_count: int = 0
    minimum_stars: int = 0

    synergy_list: List[SynergyBonus] = []

    def generate_stats(self, count: int) -> StatBonus:

        if self.count_type == COUNT_TYPE.SINGLE:
            count = 1
        else:
            count = max(self.count_cap, count)

        return StatBonus(
            firepower=self.firepower * count,
            armor=self.armor * count,
            torpedo=self.torpedo * count,
            evasion=self.evasion * count,
            anti_air=self.anti_air * count,
            anti_sub=self.anti_sub * count,
            line_of_sight=self.line_of_sight * count,
            accuracy=self.accuracy * count,
            range=self.range * count,
            speed=self.speed * count,
            dive_bombing=self.dive_bombing * count
        )


class GEAR_BONUS_STAT_KEY:
    FIREPOWER = "houg"
    ARMOR = "souk"
    TORPEDO = "raig"
    EVASION = "houk"
    ANTI_AIR = "tyku"
    ANTI_SUB = "tais"
    LINE_OF_SIGHT = "saku"
    ACCURACY = "houm"
    RANGE = "leng"
    SPEED = "soku"
    DIVE_BOMBING = "baku"

class GEAR_BONUS_DEFINITION_KEY:
    COUNT_CAP = "countCap"

    REQUIRED_SHIP_TYPE = "stypes"
    REQUIRED_CLASS_TYPE = "classes"
    REQUIRED_SHIP_ID = "ids"
    REQUIRED_SHIP_ORIGIN = "origins"

    DISTINCT_EQUIP = "distinctGears"
    EXCLUDED_SHIP_ID = "excludes"
    EXCLUDED_SHIP_TYPE = "excludeStypes"
    EXCLUDED_CLASS_TYPE = "excludeClasses"
    EXCLUDED_SHIP_ORIGIN = "excludeOrigins"

    MINIMUM_COUNT = "minCount"
    MINIMUM_STARS = "minStars"
    SYNERGY = "synergy"

class SYNERGY_DEFINITION_KEY:
    FLAGS = "flags"