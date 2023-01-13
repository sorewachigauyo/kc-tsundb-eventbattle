from typing import Union
import numpy as np
from battle.Hougeki import apply_postcap_target_special_modifier, calculate_anti_installation_precap, calculate_base_asw_power, calculate_critical_modifier
from battle.static import *
from objects.Battle import Battle
from objects.Ship import EnemyShip, FriendShip, PlayerShip
from objects.static import FORMATION, PHASE, SIDE, SPEED, STYPE
from data.utils import fetch_equip_master, get_gear_improvement_stats


def Midnight(rawapi: dict, phase: str, combined=False):
    return [
        MidnightAttack(
            attacker=attacker if cutin not in SPECIAL_ATTACK_IDS else (SPECIAL_ATTACK_ATTACKER_MAP[
                cutin][idx] + (6 if combined else 0)),
            defender=defender[idx],
            damage=damage,
            hitstatus=hitstatus[idx],
            phase=phase,
            night_carrier=night_carrier,
            cutin=cutin,
            cutin_equips=cutin_equips,
            side=SIDE.FRIEND if phase == PHASE.FRIENDLY_SHELLING and side == SIDE.PLAYER else side
        ) for attacker, defender, damage_array, hitstatus, night_carrier, cutin, cutin_equips, side in zip(
            rawapi["api_at_list"],
            rawapi["api_df_list"],
            rawapi["api_damage"],
            rawapi["api_cl_list"],
            rawapi["api_n_mother_list"],
            rawapi["api_sp_list"],
            rawapi["api_si_list"],
            rawapi["api_at_eflag"]
        ) for idx, damage in enumerate(damage_array) if damage > -1
    ]


def process_midnight(attack: MidnightAttack, battle: Battle):

    # Assign attacker, yasen attacker can be either friendly fleet or player fleet
    if attack.side == SIDE.FRIEND:
        attacker = battle.friendly_fleet.ships[attack.attacker]
    else:
        attacker = battle.fship_mapping[attack.attacker]

    defender = battle.eship_mapping[attack.defender]

    defender_submarine = defender.is_submarine()
    night_contact = battle.contact if attack.phase != PHASE.FRIENDLY_SHELLING else -1
    ark_royal_legacy = False

    if attack.night_carrier:
        num = calculate_night_carrier_power(attacker, defender, night_contact)
    elif defender_submarine:
        num = calculate_base_asw_power(attacker)
    elif attacker.id == 515 or attacker.id == 393:
        ark_royal_legacy = True
        num = calculate_ark_royal_night_power(attacker, defender, night_contact)
    else:
        num = calculate_base_attack_power(attacker, defender, night_contact)

    # Apply formation modifier if neeeded
    formation_modifier = 1

    # Apply engagement modifier for ASW
    if defender_submarine:
        formation_modifier = HOUGEKI_FORMATION_MODIFIER_ASW[attacker.fleet.formation]
        engagement_modifier = ENGAGEMENT_MODIFIERS[battle.engagement]
        num *= engagement_modifier

    if attacker.fleet.formation == FORMATION.VANGUARD:
        if attack.attacker >= int(len(attacker.fleet.ships) / 2):
            formation_modifier = 1 if not defender_submarine else 0.6
        else:
            formation_modifier = 0.5 if not defender_submarine else 1

    num *= formation_modifier

    # Apply cutin modifier
    cutin_modifier = calculate_special_attack_modifier(
        attack, attacker, battle)
    num *= cutin_modifier

    # Apply health damage modifier
    damage_modifier = DEFAULT_DAMAGE_MODIFIER[int(
        attacker.hp[0] / attacker.hp[1] * 4)]
    num *= damage_modifier

    # Invisible fits
    # CL/CLT/CT Single/Twin Gun Fit
    if attacker.stype in [STYPE.CL, STYPE.CLT, STYPE.CT]:
        single_gun_count = attacker.count_equip(CL_SINGLE_GUNS)
        twin_gun_count = attacker.count_equip(CL_TWIN_GUNS)
        num += np.sqrt(single_gun_count) + 2 * np.sqrt(twin_gun_count)

    # Zara/Pola 203mm Fit
    if attacker.id in [448, 358, 496, 449, 361]:
        num += np.sqrt(attacker.count_equip(162))

    # Apply cap
    cap = YASEN_CAP if not defender_submarine else DEFAULT_CAP

    if num > cap:
        num = cap + np.sqrt(num - cap)

    # Apply enemy specific modifiers
    num = apply_postcap_target_special_modifier(int(num), attacker, defender)

    # Apply critical modifiers if needed
    if attack.hitstatus == HITSTATUS.CRITICAL:
        num *= 1.5

        if attack.night_carrier or ark_royal_legacy or (defender_submarine and attacker.is_carrier() and attacker.stype not in [11, 18, 22]):
            critical_modifier = calculate_critical_modifier(attack, attacker)
            num *= critical_modifier

    # Invincible submarine check? No such check in kcvita so unsure where in formula to put this
    """ if defender_submarine and (battle.battletype == BATTLETYPE.COMBINED_NIGHT or battle.battletype == BATTLETYPE.NIGHT):
        num = 0 """

    return attacker, defender, int(num)


def calculate_base_attack_power(attacker: Union[PlayerShip, FriendShip], defender: EnemyShip, night_contact: int):

    defender_installation = defender.speed == SPEED.NONE
    if isinstance(attacker, PlayerShip):
        num = attacker.visible_stats["fp"] + \
            get_gear_improvement_stats(attacker)["yasen"]
    elif isinstance(attacker, FriendShip):
        num = attacker.fp + attacker.fetch_equipment_total_stats("houg", True)

    num += calculate_night_recon_modifier(night_contact)

    if defender_installation:
        num = calculate_anti_installation_precap(
            num, attacker, defender, False)
    else:
        if isinstance(attacker, PlayerShip):
            num += attacker.visible_stats["tp"]
        elif isinstance(attacker, FriendShip):
            num += attacker.tp + attacker.fetch_equipment_total_stats("raig", True)

    return num


def calculate_ark_royal_night_power(attacker: PlayerShip, defender: EnemyShip, night_contact: int):
    defender_installation = defender.speed == SPEED.NONE

    # Base firepower
    num = attacker.fp

    for equip_id in attacker.equip:
        if equip_id in SWORDFISH_IDS:
            master = fetch_equip_master(equip_id)
            num += master["api_houg"]

            if not defender_installation:
                num += master["api_raig"]

    num += calculate_night_recon_modifier(night_contact)

    if defender_installation:
        num = calculate_anti_installation_precap(
            num, attacker, defender, False)

    return num


def calculate_night_carrier_power(attacker: PlayerShip, defender: EnemyShip, night_contact: int):
    # For carrier night attack, only specific equipment and stats count towards calculation
    # This is likely to be an overestimation due to uncounted for plane slot size reduction

    defender_installation = defender.speed == SPEED.NONE

    # Base firepower
    num = attacker.fp

    for idx, equip_id in enumerate(attacker.equip):

        if equip_id == -1:
            continue

        special_bomber = equip_id in SPECIAL_NIGHT_BOMBER_IDS
        master = fetch_equip_master(equip_id)
        night_bomber = master["api_type"][3] in NIGHT_BOMBER_TYPE3_IDS
        stars = max(attacker.stars[idx], 0)

        if (special_bomber or night_bomber):
            slot_size = attacker.slot[idx]
            if slot_size > 0:
                num += master["api_houg"]

                if not defender_installation:
                    num += master["api_raig"]

                if special_bomber:
                    num += master["api_baku"]
                    mod = 0.3

                elif night_bomber:
                    num += 3 * slot_size
                    mod = 0.45

                num += np.sqrt(slot_size) * mod * (
                    master["api_baku"] + master["api_houg"] + master["api_raig"] + master["api_tais"])
                num += np.sqrt(stars)

    num += calculate_night_recon_modifier(night_contact)

    # Torpedo visible bonus counts, but not shelling
    if not defender_installation:
        num += attacker.fetch_equipment_total_stats(
            "raig", True, return_visible_bonus_only=True, included_types=[8, 58], included_ids=[])
    else:
        num = calculate_anti_installation_precap(
            num, attacker, defender, False)

    return num


def calculate_special_attack_modifier(attack: MidnightAttack, attacker: PlayerShip, battle: Battle):
    cutin_modifier = YASEN_CUTIN_MODIFIER[attack.cutin]

    # Subarmine TCI adjustment
    if attacker.is_submarine() and attack.cutin == YASEN_CUTIN.TORP_TORP_CUTIN:
        late_torpedo_count = attacker.count_equip([213, 214, 383, 441, 443, 457])

        if attacker.has_equip_type(51, 2) and late_torpedo_count:
            cutin_modifier = 1.75

        elif late_torpedo_count >= 2:
            cutin_modifier = 1.6

    # Adjust for CVCI
    elif attack.cutin == YASEN_CUTIN.CARRIER_CUTIN:

        # All 2 slot NCVCI is 1.2x modifier
        if len(attack.cutin_equips) == 2:
            cutin_modifier = 1.2
        else:

            nf = 0
            nb = 0

            for eq_id in attack.cutin_equips:
                master = fetch_equip_master(int(eq_id))
                if master["api_type"][3] == 45:
                    nf += 1
                elif master["api_type"][3] == 46:
                    nb += 1

            # Night Fighter x2 + Night Bomber is the only cutin with 1.25x modifier
            if nf == 2 and nb == 1:
                cutin_modifier = 1.25

    # DDCI 12.7cm Type D Adjustment
    elif attack.cutin >= YASEN_CUTIN.DD_MAIN_TORP_RADAR and attack.cutin <= YASEN_CUTIN.DD_TORP_LOOKOUT_DRUM2:
        dk2 = attacker.count_equip(267)
        dk3 = attacker.count_equip(366)

        cutin_modifier *= YASEN_DDCI_TYPE_D_MODIFIER[min(
            dk2 + dk3, 2)] * (1 + dk3 * 0.05)

    # Nelson Touch Red T
    elif attack.cutin == YASEN_CUTIN.NELSON_TOUCH and battle.engagement == ENGAGEMENT.RED_T:
        cutin_modifier = 2.5

    # Nagato Broadside
    elif attack.cutin == YASEN_CUTIN.NAGATO_SPECIAL:
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

    elif attack.cutin == YASEN_CUTIN.MUTSU_SPECIAL:
        thirdshot = attacker.id != 573
        partner_ship_id = attacker.fleet.ships[1].id
        if thirdshot:
            cutin_modifier = 1.2

        # Nagato K2 partner bonus
        if partner_ship_id == 541:
            cutin_modifier *= 1.4 if thirdshot else 1.2
            
        elif partner_ship_id == 275 or partner_ship_id == 80:
            cutin_modifier *= 1.35 if thirdshot else 1.15

        # Radar bonus
        if next((eq_id for eq_id in attacker.equip if eq_id > -1 if fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                and fetch_equip_master(eq_id)["api_saku"] > 4), False):
            cutin_modifier *= 1.15

    elif attack.cutin == YASEN_CUTIN.COLORADO_SPECIAL:
        if attacker.id != 601 and attacker.id != 1496 and attack.id != 913 and attack.id != 918:
            cutin_modifier = 1.3            

            # Big 7 partner bonus
            if attacker.id in [275, 541, 276, 573, 571, 576, 601, 1496, 913, 918]:
                cutin_modifier *= 1.15 if attacker.fleet.ships[1].id == attacker.id else 1.17

        # AP Shell bonus
        if attacker.has_equip_type(19, 2):
            cutin_modifier *= 1.35

        # Radar bonus
        if next((eq_id for eq_id in attacker.equip if eq_id > -1 and fetch_equip_master(eq_id)["api_type"][2] in [12, 13, 93]
                and fetch_equip_master(eq_id)["api_saku"] > 4), False):
            cutin_modifier *= 1.15

        # SG Radar LM bonus
        if attacker.has_equip(456):
            cutin_modifier *= 1.15

    elif attack.cutin == YASEN_CUTIN.KONGOU_K2_CUTIN:
        if battle.engagement == ENGAGEMENT.GREEN_T:
            cutin_modifier *= 1.25
        elif battle.engagement == ENGAGEMENT.RED_T:
            cutin_modifier *= 0.75

    elif attack.cutin == YASEN_CUTIN.YAMATO_3SHIP_CUTIN:

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

    elif attack.cutin == YASEN_CUTIN.YAMATO_2SHIP_CUTIN:
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

def calculate_night_recon_modifier(plane_id):
    if plane_id < 1:
        return 0

    master = fetch_equip_master(plane_id)
    acc = master["api_houm"]

    return YASEN_NIGHT_CONTACT_MODIFIER[acc]

