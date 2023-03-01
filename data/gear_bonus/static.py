from dataclasses import dataclass
from typing import List, Union, Dict

class COUNT_TYPE:
    """Equip item count specifier for applying bonus.
    """
    SINGLE = "single"     # Bonus is applied only once.
    MULTIPLE = "multiple" # Bonus is applied for each equipment.
    DISTINCT = "distinct" # Synergy only. Bonus is applied only once for specified synergy.
    COUNT = "byCount"     # Synergy only. Bonus is only applied if the specific number of equipment is reached.


@dataclass
class BonusDefinition:
    """Describes each equip item in KC3GearBonus.json.
    """
    count: int = 0                              # This is used by KC3 to describe the number of equipped item for later calculations. Not used.
    byShip: Union[Dict, List[Dict]] = None      # Bonus instances that are only applied per ship id. Can be either an object or a list of objects.
    byClass: Union[Dict, List[Dict]] = None     # Bonus instances that are only applied by ship class. E.g. Fubuki-class. Can be either an object or a list of objects.
    byNation: Union[Dict, List[Dict]] = None    # Bonus instances that are only applied by ship nation. Can be either an object or a list of objects.
    starsDist: List = None                      # This is used by KC3 to describe the distribution of improvements of the equipped item. Not used.


SYNERGY_GEAR_KEY = "synergyGears"
COUNTRY_CTYPE_MAP_KEY = "countryCtypeMap"

@dataclass
class StatBonus:
    """General class for holding the visible stat bonuses to be applied.
    """
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
    """Describes the synergy bonus for the attached equip item.
    """
    count_type: str = None      # Specifier for how the bonus is to be applied. @see COUNT_TYPE.
    flags: List[str] = None     # Flags that specify the condition for the synergy to activate.
    count_required: int = None  # Required number of synergy items for synergy to activate.



@dataclass
class GearBonus(StatBonus):
    """Describes the 
    """
    count_type: str = None                  # Specifier for how the bonus is to be applied. @see COUNT_TYPE.
    count_cap: int = 0                      # Restricts the maximum amount of bonus application for COUNT_TYPE.multiple.

    required_ship_type: List[int] = None    # Required ship types, e.g. CL, DD, to apply this equip item bonus.
    required_class_type: List[int] = None   # Required ship class, e.g. Fubuki-class, to apply this equip item bonus.
    required_ship_id: List[int] = None      # Required ship ID to apply this equip item bonus.
    required_ship_origin: List[int] = None  # Required ship ID of the base form (no remodels) to apply this equip item bonus.
    required_nation: List[str] = None       # Required ship nation to apply this equip item bonus.
    required_remodel_level: int = None      # Required remodel level to apply this equip item bonus. e.g. 2 for Kai Ni.

    distinct_equip_id: List[int] = None     # Bonus is not applied if certain equip bonuses have been applied. Basically a shared group of equip items.
    excluded_ship_id: List[int] = None      # Bonus excludes certain ship IDs. E.g. Kagerou K2 remodels but not Isokaze/Hamakaze B Kai.
    excluded_ship_type: List[int] = None    # Bonus excludes certain ship types.
    excluded_class_type: List[int] = None   # Bonus excludes certain ship classes.
    excluded_ship_origin: List[int] = None  # Bonus excludes certain ship base IDs.

    minimum_count: int = 0                  # Bonus requires a minimum amount of equip items.
    minimum_stars: int = 0                  # Bonus requires a minimum improvement level.

    synergy_list: List[SynergyBonus] = []   # Array of associated equipment synergies.

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
    """API definitions for each stat.
    """
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
    REQUIRED_REMODEL_LEVEL = "remodel"

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