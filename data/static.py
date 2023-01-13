"""Constants regarding KC data and values related to this project.
"""

SHIP_MASTER_FILENAME = "api_mst_ship.json"
EQUIP_MASTER_FILENAME = "api_mst_slotitem.json"
WCTF_DB_FILENAME = "wctf_db.json"
ABYSSAL_SHIP_ID_CUTOFF = 1500

class MST_SHIP_KEYS:
    """Keys for api_mst_ship. Order in alphabetical order of the keys.
    """
    REMODEL_FUEL = "api_afterbull"
    REMODEL_AMMO = "api_afterfuel"
    REMODEL_LEVEL = "api_afterlv"
    REMODEL_NEXT_ID = "api_aftershipid"
    RARITY = "api_backs"
    SCRAP_VALUE = "api_broken"
    CONSTRUCTION_TIME = "api_buildtime"
    MAX_AMMO = "api_bull_max"
    CLASS_TYPE = "api_ctype"
    MAX_FUEL = "api_fuel_max"
    INTRODUCTION_MESSAGE = "api_getmes"
    FIREPOWER = "api_houg"
    ID = "api_id"
    RANGE = "api_leng"
    LUCK = "api_luck"
    SLOT_SIZES = "api_maxeq"
    NAME = "api_name"
    MODERNIZATION_VALUE = "api_powup"
    TORPEDO = "api_raig"
    NUMBER_OF_SLOTS = "api_slot_num"
    SPEED = "api_soku"
    SORT_ID = "api_sort_id"
    PICTURE_BOOK_ID = "api_sortno"
    ARMOR = "api_souk"
    SHIP_TYPE = "api_stype"
    HP = "api_taik"
    ANTI_SUB = "api_tais"
    ANTI_AIR = "api_tyku"
    VOICE_FLAG = "api_voicef"
    YOMI = "api_yomi"



class MST_EQUIP_KEYS:
    """Keys for api_mst_slotitem. Order is in alphabetical order of the keys.
    """
    ATAP = "api_atap" # Atap is used in KC Vita for WG42 calc. Unused so far?
    DIVE_BOMBING_EVASION = "api_bakk"
    DIVE_BOMBING = "api_baku"
    SCRAP_VALUE = "api_broken"
    FIREPOWER = "api_houg"
    EVASION = "api_houk"
    ACCURACY = "api_houm"
    ID = "api_id"
    RANGE = "api_leng"
    LUCK = "api_luck"
    NAME = "api_name"
    TORPEDO = "api_raig"
    TORPEDO_EVASION = "api_raik"
    TORPEDO_ACCURACY = "api_raim"
    RARITY = "api_rare"
    LINE_OF_SIGHT_OBSTRUCTION = "api_sakb"
    LINE_OF_SIGHT = "api_saku"
    SPEED = "api_soku"
    SORT_ID = "api_sortno"
    ARMOR = "api_souk"
    HP = "api_taik"
    ANTI_SUBMARINE = "api_tais"
    ANTI_AIR = "api_tyku"
    TYPE = "api_type"
    USEBULL = "api_usebull" # ???


class SIDE:
    PLAYER = 0
    ENEMY = 1
    FRIEND = 2


class FLEET_TYPE:
    SINGLE = 0
    CTF = 1
    STF = 2
    TCF = 3
    ENEMY_COMBINED = 10


class FLEETORDER:
    MAIN = 0
    ESCORT = 1


class SPEED:
    NONE = 0
    SLOW = 5
    FAST = 10
    FAST_PLUS = 15
    FASTEST = 20


class SHIP_TYPE:
    DE = 1
    DD = 2
    CL = 3
    CLT = 4
    CA = 5
    CAV = 6
    CVL = 7
    FBB = 8
    BB = 9
    BBV = 10
    CV = 11
    XBB = 12
    SS = 13
    SSV = 14
    AP = 15
    AV = 16
    LHA = 17
    CVB = 18
    AR = 19
    AS = 20
    CT = 21
    AO = 22


class EQUIP_TYPE_0:
    """General category.
    """
    GUN = 1
    TORPEDO = 2
    CARRIER_AIRCRAFT = 3
    ANTI_AIR_MG_AND_SHELL = 4
    RECON_AIRCRAFT_AND_RADAR = 5
    UPGRADE = 6 # Bulge
    ANTI_SUBMARINE_GEAR = 7
    LANDING_CRAFT_AND_SEARCHLIGHT = 8
    TRANSPORTATION_PARTS = 9 # Drum Canister
    REPAIR_FACILITY = 10
    FLARE = 11 # Star Shell
    FLEET_COMMAND_FACILITY = 12
    AVIATION_PERSONNEL = 13 # SCAMP-like
    ANTI_AIR_FIRE_DETECTOR = 14
    ANTI_INSTALLATION = 15
    SHIP_PERSONNEL = 16 # Skilled lookouts
    LARGE_FLYING_BOAT = 17
    COMBAT_RATIONS = 18
    MARITIME_RESUPPLY = 19
    AMPHIBIOUS_TANK = 20
    LAND_BASED_BOMBER = 21
    LAND_BASED_FIGHTER = 22
    TRANSPORT_EQUIPMENT = 23
    SUBMARINE_EQUIPMENT = 24
    LAND_BASED_RECON = 25
    LARGE_LAND_BASED_BOMBER = 26


class EQUIP_TYPE_1:
    """Picture book IDs.
    """
    MAIN_GUN = 1
    SECONDARY_GUN = 2
    TORPEDO = 3
    MIDGET_SUBMARINE = 4
    CARRIER_AIRCRAFT = 5
    ANTI_AIR_GUN = 6
    RECON_AIRCRAFT = 7
    RADAR = 8
    UPGRADE = 9
    SONAR = 10
    LANDING_CRAFT = 14
    AUTOGYRO = 15
    ANTI_SUBMARINE_PATROL = 16
    BULGE = 17
    SEARCHLIGHT = 18
    TRANSPORTATION_PARTS = 19 # Drum Canister
    REPAIR_FACILITY = 20
    FLARE = 21
    FLEET_COMMAND_FACILITY = 22
    AVIATION_PERSONNEL = 23
    ANTI_AIR_FIRE_DETECTOR = 24
    AP_SHELL = 25
    ROCKET_ARTILLERY = 26
    SHIP_PERSONNEL = 27
    ANTI_AIR_SHELL = 28
    ANTI_AIR_ROCKET = 29
    DAMAGE_CONTROL = 30
    ENGINE = 31
    DEPTH_CHARGE = 32
    LARGE_FLYING_BOAT = 33
    RATION = 34
    MARITIME_RESUPPLY = 35
    SEAPLANE_FIGHTER = 36
    AMPHIBIOUS_TANK = 37
    LAND_BASED_BOMBER = 38
    LAND_BASED_FIGHTER = 39
    JET_FIGHTER_BOMBER = 40
    TRANSPORT_MATERIALS = 41 # Disassembled Saiun
    SUBMARINE_EQUIPMENT = 42
    SEAPLANE_BOMBER = 43
    HELICOPTOR = 44
    DD_TANK = 45
    LARGE_LAND_BASED_BOMBER = 46
    ARMED_BOAT = 47


class EQUIP_TYPE_2:
    """Specialized category ID.
    """
    SMALL_CALIBER_GUN = 1
    MEDIUM_CALIBER_GUN = 2
    LARGE_CALIBER_GUN = 3
    SECONDARY_GUN = 4
    TORPEDO = 5
    CARRIER_FIGHTER = 6
    CARRIER_DIVE_BOMBER = 7
    CARRIER_TORPEDO_BOMBER = 8
    CARRIER_RECON = 9
    SEAPLANE_RECON = 10
    SEAPLANE_BOMBER = 11
    SMALL_RADAR = 12
    LARGE_RADAR = 13
    SONAR = 14
    DEPTH_CHARGE = 15
    BULGE = 16
    ENGINE = 17
    ANTI_AIR_SHELL = 18
    AP_SHELL = 19
    VT_FUZE = 20
    ANTI_AIR_MACHINE_GUN = 21
    MIDGET_SUBMARINE = 22
    DAMAGE_CONTROL = 23
    LANDING_CRAFT = 24
    AUTOGYRO = 25
    ANTI_SUBMARINE_PATROL = 26
    MEDIUM_BULGE = 27
    LARGE_BULGE = 28
    SEARCHLIGHT = 29
    TRANSPORTATION_PARTS = 30 # Drums
    REPAIR_FACILITY = 31
    SUBMARINE_TORPEDO = 32
    FLARE = 33
    FLEET_COMMAND_FACILITY = 34
    AVIATION_PERSONNEL = 35
    HIGH_ANGLE_GUN = 36
    ANTI_GROUND = 37
    LARGE_GUN_II = 38
    SHIP_PERSONNEL = 39
    LARGE_SONAR = 40
    LARGE_FLYING_BOAT = 41
    LARGE_SEARCHLIGHT = 42
    COMBAT_RATION = 43
    MARITIME_RESUPPLY = 44
    SEAPLANE_FIGHTER = 45
    AMPHIBIOUS_TANK = 46
    LAND_BASED_BOMBER = 47
    LAND_BASED_FIGHTER = 48
    LAND_BASED_RECON = 49
    TRANSPORT_MATERIALS = 50 # Disassembled Saiun
    SUBMARINE_EQUIPMENT = 51
    LARGE_LAND_BASED_BOMBER = 53
    JET_FIGHTER = 56
    JET_FIGHTER_BOMBER = 57
    JET_TORPEDO_BOMBER = 58
    JET_RECON = 59

    # Only used in the game to decide if a ship can equip this category. Functions the same as their normal variant.
    LARGE_RADAR_II = 93
    CARRIER_RECON_II = 94
    SECONDARY_GUN_II = 95


class EQUIP_TYPE_3:
    """Icon ID
    """
    SMALL_CALIBER_GUN = 1
    MEDIUM_CALIBER_GUN = 2
    LARGE_CALIBER_GUN = 3
    SECONDARY_GUN = 4
    TORPEDO = 5
    CARRIER_FIGHTER = 6
    CARRIER_DIVE_BOMBER = 7
    CARRIER_TORPEDO_BOMBER = 8
    CARRIER_RECON = 9
    SEAPLANE = 10
    RADAR = 11
    ANTI_AIR_SHELL = 12
    AP_SHELL = 13
    DAMAGE_CONTROL = 14
    ANTI_AIR_MACHINE_GUN = 15
    HIGH_ANGLE_GUN = 16
    DEPTH_CHARGE = 17
    SONAR = 18


