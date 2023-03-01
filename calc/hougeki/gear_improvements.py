from calc.hougeki.static import FIGHTER_BOMBER_ID
from data.master import EquipMaster
from data.static import EQUIP_TYPE_2, EQUIP_TYPE_3


import numpy as np

firepower_type2_modifier = {
    EQUIP_TYPE_2.SMALL_CALIBER_GUN: 1,
    EQUIP_TYPE_2.MEDIUM_CALIBER_GUN: 1,
    EQUIP_TYPE_2.LARGE_CALIBER_GUN: 1.5,
    EQUIP_TYPE_2.SONAR: 0.75,
    EQUIP_TYPE_2.ANTI_AIR_SHELL: 1,
    EQUIP_TYPE_2.AP_SHELL: 1,
    EQUIP_TYPE_2.ANTI_AIR_MACHINE_GUN: 1,
    EQUIP_TYPE_2.LANDING_CRAFT: 1,
    EQUIP_TYPE_2.SEARCHLIGHT: 1,
    EQUIP_TYPE_2.SUBMARINE_TORPEDO: 1,
    EQUIP_TYPE_2.FLEET_COMMAND_FACILITY: 1,
    EQUIP_TYPE_2.HIGH_ANGLE_GUN: 1,
    EQUIP_TYPE_2.ANTI_GROUND: 1,
    EQUIP_TYPE_2.LARGE_GUN_II: 1.5,
    EQUIP_TYPE_2.SHIP_PERSONNEL: 1,
    EQUIP_TYPE_2.LARGE_SONAR: 0.75,
    EQUIP_TYPE_2.LARGE_SEARCHLIGHT: 1,
    EQUIP_TYPE_2.AMPHIBIOUS_TANK: 1
}

asw_type2_modifier = {
    EQUIP_TYPE_2.SONAR: 1,
    EQUIP_TYPE_2.DEPTH_CHARGE: 1,
    EQUIP_TYPE_2.LARGE_SONAR: 1,
}



def firepower_gear_improvement(equip: EquipMaster, improvement: int):
    if improvement <= 0:
        return 0
     
    mod = firepower_type2_modifier.get(equip.type_2, 0)
    if mod == 0:
        if equip.type_2 == EQUIP_TYPE_2.SECONDARY_GUN:
            if equip.id in [11, 134, 135]:
                mod = 1
            elif equip.id == 467:
                mod = 0.3
                return mod * improvement
            else:
                mod = 0.2 if equip.type_3 == EQUIP_TYPE_3.HIGH_ANGLE_GUN else 0.3
                return mod * improvement

        elif equip.type_2 in {EQUIP_TYPE_2.CARRIER_TORPEDO_BOMBER, EQUIP_TYPE_2.JET_TORPEDO_BOMBER, EQUIP_TYPE_2.CARRIER_DIVE_BOMBER, EQUIP_TYPE_2.JET_FIGHTER_BOMBER
                            } and equip.id not in FIGHTER_BOMBER_ID:
            return 0.2 * improvement
        
        elif equip.type_2 == 15 and not equip.id in [226, 227, 378, 488]:
            mod = 0.75

    return mod * np.sqrt(improvement)

def asw_gear_improvement(equip: EquipMaster, improvement: int):
    if improvement <= 0:
        return 0
    
    mod = asw_type2_modifier.get(equip.type_2, 0)
    if mod == 0:
        if equip.type_2 in {EQUIP_TYPE_2.CARRIER_TORPEDO_BOMBER, EQUIP_TYPE_2.JET_TORPEDO_BOMBER, EQUIP_TYPE_2.CARRIER_DIVE_BOMBER, EQUIP_TYPE_2.JET_FIGHTER_BOMBER
                            } and equip.id not in FIGHTER_BOMBER_ID:
            mod = 0.2
            return mod * improvement
        
        elif equip.type_2 == EQUIP_TYPE_2.AUTOGYRO:
            mod = 0.3 if equip.anti_sub > 10 else 0.2
            return mod * improvement
        
        elif equip.type_2 == EQUIP_TYPE_2.ANTI_SUBMARINE_PATROL:
            mod = 0.3 if equip.anti_sub > 7 else 0.2
            return mod * improvement

    return mod * np.sqrt(improvement)
