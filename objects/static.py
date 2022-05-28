class SIDE:
    PLAYER = 0
    ENEMY = 1
    FRIEND = 2


class FLEETTYPE:
    SINGLE = 0
    CTF = 1
    STF = 2
    TCF = 3
    ENEMYCOMBINED = 4


class FLEETORDER:
    MAIN = 0
    ESCORT = 1


class FORMATION:
    LINEAHEAD = 1
    DOUBLELINE = 2
    DIAMOND = 3
    ECHELON = 4
    LINEABREAST = 5
    VANGUARD = 6
    CF1 = 11
    CF2 = 12
    CF3 = 13
    CF4 = 14


class SPEED:
    NONE = 0
    SLOW = 5
    FAST = 10
    FASTPLUS = 15
    FASTEST = 20


class STYPE:
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


class BATTLETYPE:
    # Order is player side, enemy side
    NORMAL = "api_req_sortie/battle"
    NIGHT = "api_req_battle_midnight/battle"
    NIGHT_START = "api_req_battle_midnight/sp_midnight"
    AERIAL_EXCHANGE = "api_req_sortie/airbattle"
    AERIAL_RAID = "api_req_sortie/ld_airbattle"
    RADAR_AMBUSH = "api_req_sortie/ld_shooting"

    SINGLE_VS_COMBINED = "api_req_combined_battle/ec_battle"
    SINGLE_VS_COMBINED_NIGHT = "api_req_combined_battle/ec_midnight_battle"
    SINGLE_VS_COMBINED_NIGHT_TO_DAY = "api_req_combined_battle/ec_night_to_day"

    COMBINED_NIGHT = "api_req_combined_battle/midnight_battle"
    COMBINED_NIGHT_START = "api_req_combined_battle/sp_midnight"
    AERIAL_EXCHANGE_COMBINED = "api_req_combined_battle/airbattle"
    AERIAL_RAID_COMBINED = "api_req_combined_battle/ld_airbattle"
    RADAR_AMBUSH_COMBINED = "api_req_combined_battle/ld_shooting"

    CTF_TCF_VS_SINGLE = "api_req_combined_battle/battle"
    CTF_TCF_VS_COMBINED = "api_req_combined_battle/each_battle"

    STF_VS_SINGLE = "api_req_combined_battle/battle_water"
    STF_VS_COMBINED = "api_req_combined_battle/each_battle_water"


class PHASE:
    # Day
    LAND_BASE_JET = "api_air_base_injection"
    JET = "api_injection_kouku"
    LAND_BASE = "api_air_base_attack"
    FRIENDLY_AIRBATTLE = "api_friendly_kouku"
    AIRBATTLE = "api_kouku"
    AIRBATTLE2 = "api_kouku2"
    SUPPORT = "api_support_info"
    OPENING_ASW = "api_opening_taisen"
    OPENING_TORPEDO = "api_opening_atack"
    SHELLING = "api_hougeki1"
    SHELLING2 = "api_hougeki2"
    SHELLING3 = "api_hougeki3"
    CLOSING_TORPEDO = "api_raigeki"

    # Night
    FRIENDLY_SHELLING = "api_friendly_battle"
    NIGHT_SUPPORT = "api_n_support_info"
    NIGHT_SHELLING = "api_hougeki"
    NIGHT_SHELLING1 = "api_n_hougeki1"
    NIGHT_SHELLING2 = "api_n_hougeki2"


class BATTLEORDER:
    NORMAL = [PHASE.LAND_BASE_JET, PHASE.JET, PHASE.LAND_BASE, PHASE.FRIENDLY_AIRBATTLE, PHASE.AIRBATTLE,
              PHASE.AIRBATTLE2, PHASE.SUPPORT, PHASE.OPENING_ASW, PHASE.OPENING_TORPEDO, PHASE.SHELLING,
              PHASE.SHELLING2, PHASE.SHELLING3, PHASE.CLOSING_TORPEDO]

    NIGHT = [PHASE.FRIENDLY_SHELLING,
             PHASE.NIGHT_SUPPORT, PHASE.NIGHT_SHELLING]

    SINGLE_VS_COMBINED = [PHASE.LAND_BASE_JET, PHASE.JET, PHASE.LAND_BASE, PHASE.FRIENDLY_AIRBATTLE, PHASE.AIRBATTLE,
                          PHASE.AIRBATTLE2, PHASE.SUPPORT, PHASE.OPENING_ASW, PHASE.OPENING_TORPEDO, PHASE.SHELLING,
                          PHASE.CLOSING_TORPEDO, PHASE.SHELLING2, PHASE.SHELLING3]

    NIGHT_TO_DAY = [PHASE.FRIENDLY_SHELLING, PHASE.NIGHT_SUPPORT, PHASE.NIGHT_SHELLING1, PHASE.NIGHT_SHELLING2,
                    PHASE.LAND_BASE_JET, PHASE.JET, PHASE.LAND_BASE, PHASE.FRIENDLY_AIRBATTLE, PHASE.AIRBATTLE,
                    PHASE.SUPPORT, PHASE.OPENING_ASW, PHASE.OPENING_TORPEDO, PHASE.SHELLING, PHASE.SHELLING2, PHASE.CLOSING_TORPEDO]

    CTF_TCF_VS_COMBINED = [PHASE.LAND_BASE_JET, PHASE.JET, PHASE.LAND_BASE, PHASE.FRIENDLY_AIRBATTLE, PHASE.AIRBATTLE,
                           PHASE.AIRBATTLE2, PHASE.SUPPORT, PHASE.OPENING_ASW, PHASE.OPENING_TORPEDO, PHASE.SHELLING,
                           PHASE.SHELLING2, PHASE.CLOSING_TORPEDO, PHASE.SHELLING3]

    def get(x: str):
        return o[x]


o = {
    BATTLETYPE.NORMAL: BATTLEORDER.NORMAL,
    BATTLETYPE.NIGHT: BATTLEORDER.NIGHT,
    BATTLETYPE.NIGHT_START: BATTLEORDER.NIGHT,
    BATTLETYPE.AERIAL_EXCHANGE: BATTLEORDER.NORMAL,
    BATTLETYPE.AERIAL_RAID: BATTLEORDER.NORMAL,
    BATTLETYPE.RADAR_AMBUSH: BATTLEORDER.NORMAL,

    BATTLETYPE.SINGLE_VS_COMBINED: BATTLEORDER.SINGLE_VS_COMBINED,
    BATTLETYPE.SINGLE_VS_COMBINED_NIGHT: BATTLEORDER.NIGHT,
    BATTLETYPE.SINGLE_VS_COMBINED_NIGHT_TO_DAY: BATTLEORDER.NIGHT_TO_DAY,

    BATTLETYPE.COMBINED_NIGHT: BATTLEORDER.NIGHT,
    BATTLETYPE.COMBINED_NIGHT_START: BATTLEORDER.NIGHT,
    BATTLETYPE.AERIAL_EXCHANGE_COMBINED: BATTLEORDER.NORMAL,
    BATTLETYPE.AERIAL_RAID_COMBINED: BATTLEORDER.NORMAL,
    BATTLETYPE.RADAR_AMBUSH_COMBINED: BATTLEORDER.NORMAL,

    BATTLETYPE.CTF_TCF_VS_SINGLE: BATTLEORDER.SINGLE_VS_COMBINED,
    BATTLETYPE.CTF_TCF_VS_COMBINED: BATTLEORDER.CTF_TCF_VS_COMBINED,

    BATTLETYPE.STF_VS_SINGLE: BATTLEORDER.NORMAL,
    BATTLETYPE.STF_VS_COMBINED: BATTLEORDER.NORMAL
}
