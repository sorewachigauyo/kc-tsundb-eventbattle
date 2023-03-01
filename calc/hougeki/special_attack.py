from battle.static import ENGAGEMENT, HOUGEKI_CUTIN
from data.static import EQUIP_TYPE_2
from calc.base_logic import BattleLogicBase
from calc.hougeki.static import HOUGEKI_CUTIN_MODIFIER, HOUGEKI_SPATTACK_MODIFIER

def calculate_special_attack_modifier(base: BattleLogicBase, cutin: int):
    if cutin in HOUGEKI_CUTIN_MODIFIER:
        return HOUGEKI_CUTIN_MODIFIER[cutin]
    
    if cutin in SPATTACK_MAP:
        return SPATTACK_MAP[cutin](base)

    else:
        return 1

def nelson_touch(base: BattleLogicBase):
    if base.engagement == ENGAGEMENT.RED_T:
        return HOUGEKI_SPATTACK_MODIFIER.NELSON_TOUCH_RED_T
    return HOUGEKI_SPATTACK_MODIFIER.NELSON_TOUCH

def nagato_broadside(base: BattleLogicBase):
    is_main_attacker = base.attacker_id == base.attacker_fleet[0]
    partner_ship_id = base.attacker_fleet[1]

    if is_main_attacker:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.NAGATO_BROADSIDE_BASE
    else:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.NAGATO_BROADSIDE_PARTNER_BASE

    # Mutsu K2 partner bonus
    if partner_ship_id == 573:
        cutin_modifier *= 1.2 if is_main_attacker else 1.4

    # Mutsu Kai partner bonus
    elif partner_ship_id == 276 or partner_ship_id == 81:
        cutin_modifier *= 1.15 if is_main_attacker else 1.35

    # Nelson Kai partner bonus
    elif partner_ship_id == 576:
        cutin_modifier *= 1.1 if is_main_attacker else 1.25

    if base.has_equip_type2(EQUIP_TYPE_2.AP_SHELL):
        cutin_modifier *= 1.35

    if base.has_surface_radar():
        cutin_modifier *= 1.15

    return cutin_modifier

def mutsu_broadside(base: BattleLogicBase):
    is_main_attacker = base.attacker_id == base.attacker_fleet[0]
    partner_ship_id = base.attacker_fleet[1]

    if is_main_attacker:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.NAGATO_BROADSIDE_BASE
    else:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.NAGATO_BROADSIDE_PARTNER_BASE

    # Mutsu K2 partner bonus
    if partner_ship_id == 541:
        cutin_modifier *= 1.2 if is_main_attacker else 1.4

    # Mutsu Kai partner bonus
    elif partner_ship_id == 275 or partner_ship_id == 80:
        cutin_modifier *= 1.15 if is_main_attacker else 1.35

    if base.has_equip_type2(EQUIP_TYPE_2.AP_SHELL):
        cutin_modifier *= 1.35

    if base.has_surface_radar():
        cutin_modifier *= 1.15

    return cutin_modifier

def colorado_special(base: BattleLogicBase):
    is_main_attacker = base.attacker_id == base.attacker_fleet[0]
    is_second_attacker = base.attacker_id == base.attacker_fleet[1]

    if is_main_attacker:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.COLORADO_SPECIAL_BASE
    else:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.COLORADO_SPECIAL_PARTNER_BASE

        # Second and third ships get bonus mod if they are a partner ship
        if base.attacker.id in {275, 541, 276, 573, 571, 576, 601, 1496, 913, 918}:
            cutin_modifier *= 1.15 if is_second_attacker else 1.17
    
    if base.has_equip_type2(EQUIP_TYPE_2.AP_SHELL):
        cutin_modifier *= 1.35

    if base.has_surface_radar():
        cutin_modifier *= 1.15

    # SG Radar LM bonus
    if base.has_equipment(456):
        cutin_modifier *= 1.15

    return cutin_modifier


def yamato_3ship(base: BattleLogicBase):
    second_ship_id = base.attacker_fleet[1]
    third_ship_id = base.attacker_fleet[2]
    is_third_attacker = base.attacker_id == third_ship_id
    is_second_attacker = base.attacker_id == second_ship_id

    if is_third_attacker:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.YAMATO_3SHIP_THIRD_PARTNER_BASE
    else:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.YAMATO_3SHIP_BASE

    # Third attacker does not gain partner and rangefinder bonuses

    if not is_third_attacker:

        if is_second_attacker:
            # Second Shot Yamato-class bonus
            if second_ship_id in {911, 916, 546} or third_ship_id in {911, 916, 546}:
                cutin_modifier *= 1.2

            # Second Shot Nagato-class Bonus
            elif second_ship_id in {541, 573} or third_ship_id in {541, 573}:
                cutin_modifier *= 1.1
                
            # Second Shot Ise-class Bonus
            elif second_ship_id in {553, 554} or third_ship_id in {553, 554}:
                cutin_modifier *= 1.05

        # Flagship bonus for Yamato, Nagato and Ise-classes
        elif second_ship_id in {911, 916, 546, 541, 573, 553, 554} or third_ship_id in {911, 916, 546, 541, 573, 553, 554}:
            cutin_modifier *= 1.1

        # Rangefinder bonus
        if base.has_equipment_in_array({142, 460}):
            cutin_modifier *= 1.1

    if base.has_equip_type2(EQUIP_TYPE_2.AP_SHELL):
        cutin_modifier *= 1.35

    if base.has_surface_radar():
        cutin_modifier *= 1.15

    return cutin_modifier

def yamato_2ship(base: BattleLogicBase):
    partner_ship_id = base.attacker_fleet[1]
    is_main_attacker = base.attacker_id == base.attacker_fleet[0]

    if is_main_attacker:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.YAMATO_2SHIP_BASE
    else:
        cutin_modifier = HOUGEKI_SPATTACK_MODIFIER.YAMATO_2SHIP_PARTNER_BASE

    # Yamato-class K2 bonus
    if partner_ship_id in [546, 911]:
        cutin_modifier *= 1.1 if is_main_attacker else 1.2

    elif partner_ship_id == 916:
        cutin_modifier *= 1.1 if is_main_attacker else 1.25

    if base.has_equip_type2(EQUIP_TYPE_2.AP_SHELL):
        cutin_modifier *= 1.35

    if base.has_surface_radar():
        cutin_modifier *= 1.15

    # Rangefinder bonus
    if base.has_equipment_in_array({142, 460}):
        cutin_modifier *= 1.1

    return cutin_modifier

SPATTACK_MAP = {
    HOUGEKI_CUTIN.NELSON_TOUCH: nelson_touch,
    HOUGEKI_CUTIN.NAGATO_SPECIAL: nagato_broadside,
    HOUGEKI_CUTIN.MUTSU_SPECIAL: mutsu_broadside,
    HOUGEKI_CUTIN.COLORADO_SPECIAL: colorado_special,
    HOUGEKI_CUTIN.YAMATO_3SHIP_CUTIN: yamato_3ship,
    HOUGEKI_CUTIN.YAMATO_2SHIP_CUTIN: yamato_2ship
}
