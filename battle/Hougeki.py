from functools import reduce
import numpy as np
from objects.Battle import Battle
from objects.Ship import EnemyShip, PlayerShip
from objects.static import FLEETORDER, FLEETTYPE, FORMATION, PHASE, SIDE, SPEED, STYPE
from utils import fetch_equip_master, get_gear_improvement_stats
from battle.static import *


def Hougeki(rawapi: dict, phase: str):
    return [
        HougekiAttack(
            attacker=attacker if cutin not in SPECIAL_ATTACK_IDS else SPECIAL_ATTACK_ATTACKER_MAP[
                cutin][idx],
            defender=defender[idx],
            damage=damage,
            hitstatus=hitstatus[idx],
            phase=phase,
            cutin=cutin,
            cutin_equips=cutin_equips,
            side=side
        ) for attacker, defender, damage_array, hitstatus, cutin, cutin_equips, side in zip(
            rawapi["api_at_list"],
            rawapi["api_df_list"],
            rawapi["api_damage"],
            rawapi["api_cl_list"],
            rawapi["api_at_type"],
            rawapi["api_si_list"],
            rawapi["api_at_eflag"],
        ) for idx, damage in enumerate(damage_array)
    ]


def process_hougeki(attack: HougekiAttack, battle: Battle):

    attacker = battle.fship_mapping[attack.attacker]
    defender = battle.eship_mapping[attack.defender]

    defender_submarine = defender.is_submarine()
    defender_installation = defender.speed == SPEED.NONE

    # Calculate precapped power
    if defender_submarine:
        num = calculate_base_asw_power(attacker)
    else:
        num = calculate_base_attack_power(attacker, defender)

    # Anti-installation modifiers
    if defender_installation:
        num = calculate_anti_installation_precap(num, attacker, defender)

    # Apply formation and engagement modifiers
    formation_modifier = (HOUGEKI_FORMATION_MODIFIER if not defender_submarine else HOUGEKI_FORMATION_MODIFIER_ASW)[
        attacker.fleet.formation]

    if attacker.fleet.formation == FORMATION.ECHELON and defender.fleet.fleet_type == FLEETTYPE.ENEMYCOMBINED:
        formation_modifier = 0.6

    if attacker.fleet.formation == FORMATION.VANGUARD:
        if attack.attacker >= int(len(attacker.fleet.ships) / 2):
            formation_modifier = 1 if not defender_submarine else 0.6
        else:
            formation_modifier = 0.5 if not defender_submarine else 1

    engagement_modifier = ENGAGEMENT_MODIFIERS[battle.engagement]
    num *= formation_modifier * engagement_modifier

    # Apply health damage modifier
    hpercent = attacker.hp[0] / attacker.hp[1]
    if hpercent == 1:
        damage_modifier = DEFAULT_DAMAGE_MODIFIER[4]
    elif hpercent <= 0.25:
        damage_modifier = DEFAULT_DAMAGE_MODIFIER[0]
    elif hpercent <= 0.5:
        damage_modifier = DEFAULT_DAMAGE_MODIFIER[1]
    else:
        damage_modifier = DEFAULT_DAMAGE_MODIFIER[2]
    num *= damage_modifier

    # Apply invisible firepower fits
    # CL/CLT/CT Single/Twin Gun Fit
    if attacker.stype in [STYPE.CL, STYPE.CLT, STYPE.CT]:
        single_gun_count = attacker.count_equip(CL_SINGLE_GUNS)
        twin_gun_count = attacker.count_equip(CL_TWIN_GUNS)
        num += np.sqrt(single_gun_count) + 2 * np.sqrt(twin_gun_count)

    # Zara/Pola 203mm Fit
    if attacker.id in [448, 358, 496, 449, 361]:
        num += np.sqrt(attacker.count_equip(162))

    # Apply day cap
    cap = HOUGEKI_CAP if not defender_submarine else DEFAULT_CAP

    if num > cap:
        num = cap + np.sqrt(num)

    # Apply enemy specific modifiers
    num = apply_postcap_target_special_modifier(int(num), attacker, defender)

    # Calculate and apply cutin modifier
    cutin_modifier = calculate_special_attack_modifier(
        attack, attacker, battle)
    num *= cutin_modifier

    # Apply AP shell modifier if present
    if attacker.has_equip_type(19, 2) and attacker.has_equip_type(1, 1) and defender.stype in [5, 6, 8, 9, 10, 11, 18]:
        ap_shell_mod = 1.08

        # Secondary AP mod takes priority
        if attacker.has_equip_type(2, 1):
            ap_shell_mod = 1.15

        # Radar AP mod
        elif attacker.has_equip_type(8, 1):
            ap_shell_mod = 1.1

        num = int(num * ap_shell_mod)

    # Apply critical modifiers
    if attack.hitstatus == HITSTATUS.CRITICAL:
        num *= 1.5
        critical_modifier = 1

        # Carrier shelling on non sub OR aerial attack on a sub that is not OASW, CV(B) and AO do not gain prof crit mod on subs
        if (attacker.uses_carrier_shelling() and not defender_submarine) or (defender_submarine and
                                                                             attack.phase != PHASE.OPENING_ASW and attacker.uses_carrier_asw_shelling() and attacker.stype not in [11, 18, 22]):

            critical_modifier = calculate_critical_modifier(attack, attacker)
            num *= critical_modifier

    return attacker, defender, int(num)


def calculate_special_attack_modifier(attack: HougekiAttack, attacker: PlayerShip, battle: Battle):
    spattack = attack.cutin
    # Apply cutin modifier
    cutin_modifier = HOUGEKI_CUTIN_MODIFIER[spattack]

    # No need to process further for regular cutins
    if spattack < 7 or spattack > 199:
        return cutin_modifier

    # Adjust for CVCI
    if attack.cutin == HOUGEKI_CUTIN.CARRIER_CUTIN and len(attack.cutin_equips) == 3:
        cutin_modifier = 1.2 if sum([fetch_equip_master(
            int(eq_id))["api_type"][2] for eq_id in attack.cutin_equips]) == 22 else 1.25

    # Nelson Touch Red T
    elif attack.cutin == HOUGEKI_CUTIN.NELSON_TOUCH and battle.engagement == ENGAGEMENT.RED_T:
        cutin_modifier = 2.5

    # Nagato Broadside
    elif attack.cutin == HOUGEKI_CUTIN.NAGATO_SPECIAL:
        thirdshot = attacker.id != 541
        if thirdshot:
            cutin_modifier = 1.2

        partner_ship_id = attacker.fleet.ships[1].id
        # Mutsu K2 partner bonus
        if partner_ship_id == 573:
            cutin_modifier *= 1.4 if thirdshot else 1.2

        # Mutsu Kai partner bonus
        elif partner_ship_id == 276 or partner_ship_id == 81:
            cutin_modifier *= 1.35 if thirdshot else 1.15

        # Nelson Kai partner bonus
        elif partner_ship_id == 576:
            cutin_modifier *= 1.25 if thirdshot else 1.1

        # AP Shell bonus
        if attacker.has_equip_type(19, 2):
            cutin_modifier *= 1.35

        # Radar
        if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                and fetch_equip_master(eq_id)["api_saku"] > 4), False):
            cutin_modifier *= 1.15

    elif attack.cutin == HOUGEKI_CUTIN.MUTSU_SPECIAL:
        thirdshot = attacker.id != 573
        partner_ship_id = attacker.fleet.ships[1].id
        if thirdshot:
            cutin_modifier = 1.2

        # Nagato K2 partner bonus
        if partner_ship_id == 541:
            cutin_modifier *= 1.4 if thirdshot else 1.2
            
        elif partner_ship_id == 275 or partner_ship_id == 80:
            cutin_modifier *= 1.35 if thirdshot else 1.15

        # AP Shell bonus
        if attacker.has_equip_type(19, 2):
            cutin_modifier *= 1.35

        # Radar bonus
        if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                and fetch_equip_master(eq_id)["api_saku"] > 4), False):
            cutin_modifier *= 1.15

    elif attack.cutin == HOUGEKI_CUTIN.COLORADO_SPECIAL:
        if attacker.id != 601 and attacker.id != 1496:
            cutin_modifier = 1.2

            # Big 7 partner bonus
            if attacker.id in [80, 275, 541, 81, 276, 573, 571, 576]:
                cutin_modifier *= 1.1 if attacker.fleet.ships[1].id == attacker.id else 1.15

        # AP Shell bonus
        if attacker.has_equip_type(19, 2):
            cutin_modifier *= 1.35

        # Radar bonus
        if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                and fetch_equip_master(eq_id)["api_saku"] > 4), False):
            cutin_modifier *= 1.15

        elif attack.cutin == HOUGEKI_CUTIN.YAMATO_3SHIP_CUTIN:

            thirdshot = attacker.id == attacker.fleet.ships[2].id
            partner_ship_id = attacker.fleet.ships[1].id

            if thirdshot:
                cutin_modifier = 1.65

            # Class modifiers and rangefinder do not apply to the third attacker
            if not thirdshot:
                # Yamato-class K2
                if partner_ship_id in [911, 916, 546]:
                    if attacker.id == attacker.fleet.ships[0].id:
                        cutin_modifier *= 1.1
                    else:
                        cutin_modifier *= 1.2

                # Nagato-class K2
                elif partner_ship_id in [541, 573]:
                    cutin_modifier *= 1.1

                # Ise-class K2
                elif partner_ship_id in [553, 554]:
                    cutin_modifier *= 1.05

                # Rangefinder bonus
                if attacker.has_equip([142, 460]):
                    cutin_modifier *= 1.1

            # AP Shell bonus
            if attacker.has_equip_type(19, 2):
                cutin_modifier *= 1.35

            # Radar bonus
            if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                    and fetch_equip_master(eq_id)["api_saku"] > 4), False):
                cutin_modifier *= 1.15

        elif attack.cutin == HOUGEKI_CUTIN.YAMATO_2SHIP_CUTIN:
            partner_ship_id = attacker.fleet.ships[1].id
            thirdshot = attacker.id == partner_ship_id

            if thirdshot:
                cutin_modifier = 1.55

             # Yamato-class K2 bonus
            if partner_ship_id in [546, 911, 916]:
                cutin_modifier *= 1.2 if thirdshot else 1.1

            # AP Shell bonus
            if attacker.has_equip_type(19, 2):
                cutin_modifier *= 1.35

            # Radar bonus
            if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                    and fetch_equip_master(eq_id)["api_saku"] > 4), False):
                cutin_modifier *= 1.15

            # Rangefinder bonus
            if attacker.has_equip([142, 460]):
                cutin_modifier *= 1.1


    return cutin_modifier


def calculate_base_attack_power(ship: PlayerShip, target: EnemyShip):
    num = ship.visible_stats["fp"]
    cf_factor = determine_combined_fleet_factor(ship, target)

    carrier_shelling = ship.uses_carrier_shelling()
    if carrier_shelling:
        # If attacking installation, fetch equipment stats
        if target.speed == SPEED.NONE:
            torpedo_baku = ship.fetch_equipment_total_stats(
                "baku", False, [8, 58])
            dive_baku = ship.fetch_equipment_total_stats(
                "baku", False, [7, 57], ANTI_LAND_BOMBER_IDS)
            num += int(1.3 * (torpedo_baku + dive_baku))
        else:
            num += ship.fetch_equipment_total_stats("raig", True)
            num += cf_factor
            num += int(1.3 * ship.fetch_equipment_total_stats("baku"))
            if ship.side == SIDE.PLAYER:
                num += get_gear_improvement_stats(ship).get("fp")
            num = int(1.5 * num)
            num += 50
    else:
        num += cf_factor
        num += get_gear_improvement_stats(ship).get("fp")
    num += 5
    return num


def calculate_base_asw_power(ship: PlayerShip):
    aerial_attack = ship.uses_carrier_asw_shelling()
    # Base attack constant
    num = 8 if aerial_attack else 13

    # Equipment ASW, includes visible bonus
    eq_asw = 0
    for eq_id in ship.equip:
        if eq_id == -1:
            continue

        master = fetch_equip_master(eq_id)
        if master["api_type"][2] in ASW_EQUIPMENT_TYPE2_IDS:
            eq_asw += master["api_tais"]

    eq_asw_bonus = ship.fetch_equipment_total_stats(
        "tais", True, return_visible_bonus_only=True)
    eq_asw += eq_asw_bonus
    num += 1.5 * eq_asw
    #num += eq_asw_bonus

    # Base ship ASW
    base_asw = ship.visible_stats["as"] - \
        ship.fetch_equipment_total_stats("tais", True)
    num += 2 * np.sqrt(base_asw)

    # Improvement bonus
    num += get_gear_improvement_stats(ship)["asw"]

    # ASW equip synergy
    synergy_modifier = 1
    has_dc = ship.has_equip([226, 227, 378, 439])
    has_dcp = ship.has_equip([44, 45, 287, 288, 377])

    # DC + DCP
    if has_dc and has_dcp:
        synergy_modifier = 1.1

        # Small Sonar + DC + DCP
        if ship.has_equip_type(14, 2):
            synergy_modifier = 1.25

    # Legacy synergy
    if ship.has_equip_type(18, 3) and ship.has_equip_type(17, 3):
        synergy_modifier *= 1.15

    num *= synergy_modifier

    return num


def determine_combined_fleet_factor(attacker: PlayerShip, target: EnemyShip):
    is_main = attacker.fleet.order == FLEETORDER.MAIN

    if target.fleet.fleet_type != FLEETTYPE.ENEMYCOMBINED:
        # CTF vs single
        if attacker.fleet.fleet_type == FLEETTYPE.CTF:
            return 2 if is_main else 10
        # STF vs single
        elif attacker.fleet.fleet_type == FLEETTYPE.STF:
            return 10 if is_main else -5
        # TCF vs single
        elif attacker.fleet.fleet_type == FLEETTYPE.CTF:
            return -5 if is_main else 10
        # Single vs Single
        else:
            return 0
    else:
        # CTF vs CF
        if attacker.fleet.fleet_type == FLEETTYPE.CTF:
            return 2 if is_main else -5
        # STF vs CF
        elif attacker.fleet.fleet_type == FLEETTYPE.STF:
            return 2 if is_main else -5
        # TCF vs CF
        elif attacker.fleet.fleet_type == FLEETTYPE.TCF:
            return -5
        # Single vs CF
        else:
            return 5


def calculate_anti_installation_precap(num: float, attacker: PlayerShip, defender: EnemyShip, is_hougeki=True):
    # https://github.com/Nishisonic/UnexpectedDamage/blob/master/UnexpectedDamage.js#L1865-L2057

    # Order of calculations
    # stype bonus mult, add
    # basic bonus mult
    # 11th tank regiment mult, add
    # m4a1 mult, add
    # honi mult, add
    # armed dlc/ab mult, add
    # basic bonus add

    stype_bonus = basic_bonus = shikon_bonus = m4a1_bonus = m4a1_bonus = honi_bonus = armed_dlc_ab_bonus = (
        1, 0)

    # Assign general modifiers first

    # WG42
    wg42_count = attacker.count_equip(126)
    basic_bonus[1] += ANTI_INSTALLATION_WG42_MODIFIER[wg42_count]

    # T2 Mortar
    t2_mortar_count = attacker.count_equip(346)
    basic_bonus[1] += ANTI_INSTALLATION_T2_MORTAR_MODIFIER[t2_mortar_count]

    # T2 Mortar CD
    t2_mortar_ex_count = attacker.count_equip(347)
    basic_bonus[1] += ANTI_INSTALLATION_T2_MORTAR_EX_MODIFIER[t2_mortar_ex_count]

    # T4 Rocket
    t4_rocket_count = attacker.count_equip(348)
    basic_bonus[1] += ANTI_INSTALLATION_T4_ROCKET_MODIFIER[t4_rocket_count]

    # T4 Rocket CD
    t4_rocket_ex_count = attacker.count_equip(349)
    basic_bonus[1] += ANTI_INSTALLATION_T4_ROCKET_EX_MODIFIER[t4_rocket_ex_count]

    # Daihatsu improvement modifier
    dlc_count = attacker.count_equip_by_type(24, 2)
    if dlc_count:
        dlc_lv = reduce((lambda x, y: x + max(attacker.stars[y[0]], 0) if fetch_equip_master(y[1])["api_type"][2] == 24 else 0),
                        enumerate(attacker.equip), 0) / dlc_count
        basic_bonus[0] = (dlc_lv / 50 + 1)

        # 11th Tank Regiment
        has_shikon = attacker.has_equip(230)
        if has_shikon:
            shikon_bonus = ANTI_INSTALLATION_SHIKON_MODIFIER

        # M4A1DD
        has_m4a1 = attacker.has_equip(355)
        if has_m4a1:
            m4a1_bonus = ANTI_INSTALLATION_M4A1_MODIFIER

        # Toku Daihatsu Landing Craft + Type 1 Gun Tank
        has_honi = attacker.has_equip(449)
        if has_honi:
            shikon_bonus = ANTI_INSTALLATION_SHIKON_MODIFIER
            honi_bonus = ANTI_INSTALLATION_HONI_MODIFIER

        armed_dlc_count = attacker.count_equip(409)
        ab_count = attacker.count_equip(230)
        armed_dlc_ab_count = armed_dlc_count + ab_count
        # Daihatsu, Toku Daihatsu, T89, Panzer II, HoNi
        groupA_count = attacker.count_equip([68, 193, 166, 436, 449])
        # 11th Tank Regiment, Kami
        groupB_count = attacker.count_equip([230, 167])

        # Armed DLC + AB
        if (armed_dlc_count < 2 and ab_count < 2):

            if armed_dlc_ab_count == 1 and (groupA_count + groupB_count):
                armed_dlc_ab_bonus = ANTI_INSTALLATION_ARMED_DLC_AB_GRPA_GRPB_MODIFIER

            elif armed_dlc_ab_count >= 2:
                if (groupA_count + groupB_count) >= 2:
                    armed_dlc_ab_bonus = ANTI_INSTALLATION_ARMED_DLC_AB2_GRPA_GRPB_MODIFIER

                elif groupA_count:
                    armed_dlc_ab_bonus = ANTI_INSTALLATION_ARMED_DLC_AB2_GRPA_MODIFIER

                elif groupB_count:
                    armed_dlc_ab_bonus = ANTI_INSTALLATION_ARMED_DLC_AB2_GRPB_MODIFIER

    # Kami improvement modifier
    kami_count = attacker.count_equip(167)
    if kami_count:
        kami_lv = reduce((lambda x, y: x + max(attacker.stars[y[0]], 0) if y[1] == 167 else 0),
                         enumerate(attacker.equip), 0) / kami_count
        basic_bonus[0] *= (1 + kami_lv / 30)

    # SS(V) modifier
    if attacker.stype == STYPE.SS or attacker.stype == STYPE.SSV:
        stype_bonus[1] += ANTI_INSTALLAION_SUBMARINE_MODIFIER

    # Artillery Imp
    if defender.id in ARTILLERY_IMP_IDS:

        # DD stype bonus
        if attacker.stype == STYPE.DD or attacker.stype == STYPE.CL:
            stype_bonus[0] = ARTILLERY_IMP_DD_CL_MODIFIER

        # AP shell modifier
        if attacker.has_equip_type(19, 2):
            basic_bonus[0] *= ARTILLERY_IMP_AP_MODIFIER

        # WG42
        basic_bonus[0] *= ARTILLERY_IMP_WG42_MODIFIER[min(wg42_count, 2)]

        # T4 Rocket
        basic_bonus[0] *= ARTILLERY_IMP_T4_ROCKET_MODIFIER[min(
            t4_rocket_count + t4_rocket_ex_count, 2)]

        # T2 Mortar
        basic_bonus[0] *= ARTILLERY_IMP_MORTAR_MODIFIER[min(
            t2_mortar_count + t2_mortar_ex_count, 2)]

        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            basic_bonus[0] *= ARTILLERY_IMP_SEAPLANE_MODIFIER

        # Kami
        basic_bonus[0] *= ARTILLERY_IMP_KAMI_MODIFIER[min(kami_count, 2)]

        # Bombers
        bcount = attacker.count_equip_by_type(7, 2)
        basic_bonus[0] *= ARTILLERY_IMP_BOMBER_MODIFIER[min(bcount, 2)]

        # Daihatsu bonuses
        if dlc_count:
            basic_bonus[0] *= ARTILLERY_IMP_DAIHATSU_MODIFIER

            # Toku Daihatsu
            if attacker.has_equip(193):
                basic_bonus[0] *= ARTILLERY_IMP_TOKU_MODIFIER

            # T89/HoNi
            t89_count = min(attacker.count_equip(166, 449), 2)
            basic_bonus[0] *= ARTILLERY_IMP_T89_HONI_MODIFIER[t89_count]

            # M4A1
            if has_m4a1:
                basic_bonus[0] *= ARTILLERY_IMP_M4A1_MODIFIER

            if armed_dlc_ab_count and is_hougeki:
                basic_bonus[0] *= ARTILLERY_IMP_DAY_ARMED_DLC_AB_MODIFIER[min(
                    armed_dlc_ab_count, 2)]

    # Isolated Island Princess
    elif defender.id in ISOLATED_ISLAND_PRINCESS_IDS:

        # T3 shell modifier
        if attacker.has_equip_type(18, 2):
            basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_T3_SHELL_MODIFIER

        # WG42
        basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_WG42_MODIFIER[min(
            wg42_count, 2)]

        # T4 Rocket
        basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_T4_ROCKET_MODIFIER[min(
            t4_rocket_count + t4_rocket_ex_count, 2)]

        # T2 Mortar
        basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_MORTAR_MODIFIER[min(
            t2_mortar_count + t2_mortar_ex_count, 2)]

        # Bombers
        bcount = attacker.count_equip_by_type(7, 2)
        basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_BOMBER_MODIFIER[min(
            bcount, 2)]

        # Kami
        basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_KAMI_MODIFIER[min(
            kami_count, 2)]

        # Daihatsu bonuses
        if dlc_count:
            basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_DAIHATSU_MODIFIER

            # Toku Daihatsu
            if attacker.has_equip(193):
                basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_TOKU_MODIFIER

            # T89/HoNi
            t89_count = min(attacker.count_equip(166, 449), 2)
            basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_T89_HONI_MODIFIER[t89_count]

            # M4A1
            if has_m4a1:
                basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_M4A1_MODIFIER

            # Armed DLC/AB
            if armed_dlc_ab_count and is_hougeki:
                basic_bonus[0] *= ISOLATED_ISLAND_PRINCESS_ARMED_DLC_AB_MODIFIER[min(
                    armed_dlc_ab_count, 2)]

    # Harbour Summer Princess
    elif defender.id in HARBOUR_SUMMER_PRINCESS_IDS:

        # T3 shell modifier
        if attacker.has_equip_type(18, 2):
            basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_T3_SHELL_MODIFIER

        # AP shell modifier
        if attacker.has_equip_type(19, 2):
            basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_AP_SHELL_MODIFIER

        # WG42
        basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_WG42_MODIFIER[min(
            wg42_count, 2)]

        # T4 Rocket
        basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_T4_ROCKET_MODIFIER[min(
            t4_rocket_count + t4_rocket_ex_count, 2)]

        # T2 Mortar
        basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_MORTAR_MODIFIER[min(
            t2_mortar_count + t2_mortar_ex_count, 2)]

        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_SEAPLANE_MODIFIER

        # Kami
        basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_KAMI_MODIFIER[min(
            kami_count, 2)]

        # Bombers
        bcount = attacker.count_equip_by_type(7, 2)
        basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_BOMBER_MODIFIER[min(
            bcount, 2)]

        # Daihatsu bonuses
        if dlc_count:
            basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_DAIHATSU_MODIFIER

            # Toku Daihatsu
            if attacker.has_equip(193):
                basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_TOKU_MODIFIER

            # T89/HoNi
            t89_count = min(attacker.count_equip(166, 449), 2)
            basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_T89_HONI_MODIFIER[t89_count]

            # M4A1
            if has_m4a1:
                basic_bonus[0] *= HARBOUR_SUMMER_PRINCESS_M4A1_MODIFIER

    # Soft skinned
    else:

        # T3 shell modifier
        if attacker.has_equip_type(18, 2):
            basic_bonus[0] *= SOFT_SKINNED_T3_SHELL_MODIFIER

        # WG42
        basic_bonus[0] *= SOFT_SKINNED_WG42_MODIFIER[min(wg42_count, 2)]

        # T4 Rocket
        basic_bonus[0] *= SOFT_SKINNED_T4_ROCKET_MODIFIER[min(
            t4_rocket_count + t4_rocket_ex_count, 2)]

        # T2 Mortar
        basic_bonus[0] *= SOFT_SKINNED_MORTAR_MODIFIER[min(
            t2_mortar_count + t2_mortar_ex_count, 2)]

        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            basic_bonus[0] *= SOFT_SKINNED_SEAPLANE_MODIFIER

        # Kami
        basic_bonus[0] *= SOFT_SKINNED_KAMI_MODIFIER[min(kami_count, 2)]

        # Daihatsu bonuses
        if dlc_count:
            basic_bonus[0] *= SOFT_SKINNED_DAIHATSU_MODIFIER

            # Toku Daihatsu
            if attacker.has_equip(193):
                basic_bonus[0] *= SOFT_SKINNED_TOKU_MODIFIER

            # T89/HoNi
            t89_count = min(attacker.count_equip(166, 449), 2)
            basic_bonus[0] *= SOFT_SKINNED_T89_HONI_MODIFIER[t89_count]

            # M4A1
            if has_m4a1:
                basic_bonus[0] *= SOFT_SKINNED_M4A1_MODIFIER

            # Armed DLC/AB
            if armed_dlc_ab_count and is_hougeki:
                basic_bonus[0] *= SOFT_SKINNED_DAY_ARMED_DLC_AB_MODIFIER[min(
                    armed_dlc_ab_count, 2)]

            # Pancer
            if attacker.has_equip(436):
                basic_bonus[0] *= SOFT_SKINNED_PANZER_MODIFIER

    # Apply modifiers
    num = num * stype_bonus[0] + stype_bonus[1]
    num *= basic_bonus[0]
    num = num * shikon_bonus[0] + shikon_bonus[1]
    num = num * m4a1_bonus[0] + m4a1_bonus[1]
    num = num * honi_bonus[0] + honi_bonus[1]
    num = num * armed_dlc_ab_bonus[0] + armed_dlc_ab_bonus[1]
    num += basic_bonus[1]

    return num


def calculate_critical_modifier(attack: HougekiAttack, attacker: PlayerShip):
    critical_modifier = 1

    if attack.cutin == HOUGEKI_CUTIN.CARRIER_CUTIN:
        # If captain participates in cutin
        if str(attacker.equip[0]) in attack.cutin_equips:
            critical_modifier += 0.15

        cnt = 0
        alv = 0
        # Calculate average proficiency bonus
        for idx, eq_id in enumerate(attacker.equip):
            if eq_id == -1:
                continue

            if fetch_equip_master(eq_id)["api_type"][2] in BOMBER_TYPE2_IDS:
                cnt += 1
                alv += max(attacker.proficiency[idx], 0)

        critical_modifier += PROFICIENCY_MODIFIER[int(alv / cnt)] / 100

    else:
        # Calculate normal carrier bonus, note that even zeroed planes count towards total proficiency
        for idx, eq_id in enumerate(attacker.equip):

            if eq_id == -1:
                continue

            divisor = 200 if idx != 0 else 100
            if fetch_equip_master(eq_id)["api_type"][2] in BOMBER_TYPE2_IDS:
                proficiency = max(attacker.proficiency[idx], 0)
                critical_modifier += int(np.sqrt(
                    PROFICIENCY_EXPERIENCE[proficiency]) + PROFICIENCY_MODIFIER[proficiency]) / divisor

    return critical_modifier


def apply_postcap_target_special_modifier(num: float, attacker: PlayerShip, defender: EnemyShip):
    """Calculate target specific weakness modifiers

    See https://github.com/Nishisonic/UnexpectedDamage/blob/master/UnexpectedDamage.js#L1595-L1765
    """
    # PT imp Pack
    if defender.id in PT_IMP_IDS:
        num *= 0.35
        num += 15

        # Small caliber gun
        num *= PT_IMP_SMALL_GUN_MODIFIER[min(
            attacker.count_equip_by_type(1, 2), 2)]

        # Secondary gun
        if attacker.has_equip_type(4, 2):
            num *= PT_IMP_SECONDARY_GUN_MODIFIER

        # Bombers (max of carrier or jets)
        bcount = min(max(attacker.count_equip_by_type(7, 2),
                     attacker.count_equip_by_type(57, 2)), 2)
        num *= PT_IMP_BOMBER_MODIFIER[bcount]

        # Seaplane bomber and fighter
        if attacker.has_equip_type([11, 45], 2):
            num *= PT_IMP_SEAPLANE_MODIFIER

        # AA gun
        num *= PT_IMP_AA_GUN_MODIFIER[min(
            attacker.count_equip_by_type(21, 2), 2)]

        # Skilled Lookout
        if attacker.has_equip_type(39, 2):
            num *= PT_IMP_LOOKOUT_MODIFIER

        # Armed Daihatsu/Armed Boat
        num *= PT_IMP_BOAT_MODIFIER[min(attacker.count_equip([408, 409]), 2)]

    # Battleship Summer Princess
    elif defender.id in SUMMER_BATTLESHIP_PRINCESS_IDS:

        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            num *= SUMMER_BATTLESHIP_SEAPLANE_MODIFIER

        # AP shell modifier
        if attacker.has_equip_type(19, 2):
            num *= SUMMER_BATTLESHIP_AP_MODIFIER

        # Nishisonic included a foreign ship bonus, but I'm not sure about this

    # Summer Heavy Cruiser Princess
    elif defender.id in SUMMER_HEAVY_CRUISER_PRINCESS_IDS:

        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            num *= SUMMER_HEAVY_CRUISER_PRINCESS_SEAPLANE_MODIFIER

        # AP shell modifier
        if attacker.has_equip_type(19, 2):
            num *= SUMMER_HEAVY_CRUISER_AP_MODIFIER

    # Supply Depot Princess
    elif defender.id in SDH_IDS:

        # Apply Daihatsu modifiers
        dlc_count = attacker.count_equip_by_type(24, 2)
        if dlc_count:
            num *= SDH_DAIHATSU_MODIFIER

            # Calculate average improvement of daihatsu
            dlc_lv = reduce((lambda x, y: x + max(attacker.stars[y[0]], 0) if fetch_equip_master(
                y[1])["api_type"][2] == 24 else 0), enumerate(attacker.equip), 0) / dlc_count
            # Apply improvement modifier for daihatsus,  repeat if T89/Honi and Panzer II is present
            num *= np.power(1 + dlc_lv / 50, 1 + (
                166 in attacker.equip or 449 in attacker.equip) + (436 in attacker.equip))

            # Toku Daihatsu
            if attacker.has_equip(193):
                num *= SDH_TOKU_DAIHATSU_MODIFIER

            # T89 + Honi
            num *= SDH_HONI_T89_MODIFIER[min(
                attacker.count_equip([166, 449]), 2)]

            # M4A1
            if attacker.has_equip(355):
                num *= SDH_M4A1_MODIFIER

            # Panzer II
            if attacker.has_equip(436):
                num *= SDH_PANZER_MODIFIER

            # Armed Daihatsu + Armed Boat
            num *= SDH_AB_ARMED_DAIHATSU_MODIFIER[min(
                attacker.count_equip([408, 409]), 2)]

        # Apply improvement modifier for Type 2 Tank
        kami_count = attacker.count_equip(167)
        if kami_count:
            kami_lv = reduce(
                (lambda x, y: x + max(attacker.stars[y[0]], 0) if y[1] == 167 else 0), enumerate(attacker.equip), 0) / kami_count
            num *= (1 + kami_lv / 30)

            num *= SDH_KAMI_MODIFIER[min(kami_count, 2)]

        # WG42
        num *= SDH_WG42_MODIFIER[min(attacker.count_equip(126), 2)]

        # Type 4 Rocket
        num *= SDH_TYPE4_ROCKET_MODIFIER[min(
            attacker.count_equip([348, 349]), 2)]

        # Mortar
        num *= SDH_MORTAR_MODIFIER[min(attacker.count_equip([346, 347]), 2)]

    # French Battleship Princess
    elif defender.id in FRENCH_BATTLESHIP_PRINCESS_ID:
        # Seaplane modifiers
        if attacker.has_equip_type([11, 45], 2):
            num *= FRENCH_BATTLESHIP_PRINCESS_SEAPLANE_MODIFIER

        # AP shell modifier
        if attacker.has_equip_type(19, 2):
            num *= FRENCH_BATTLESHIP_PRINCESS_AP_MODIFIER

        # Late298B
        if 194 in attacker.equip:
            num *= FRENCH_BATTLESHIP_PRINCESS_LATE_MODIFIER

        # Bomber modifier
        bcount = attacker.count_equip_by_type(7, 2)
        if bcount:
            num *= FRENCH_BATTLESHIP_PRINCESS_BOMBER_MODIFIER[min(bcount, 2)]

        # Richelieu
        if attacker.id == 392 or attacker.id == 492:
            num *= FRENCH_BATTLESHIP_PRINCESS_RICHELIEU_MODIFIER

    return int(num)
