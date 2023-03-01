from typing import List, Dict
from functools import reduce


import numpy as np


from data.master import fetch_ship_master, fetch_equip_master
from calc.base_logic import BattleLogicBase
from battle.static import FORMATION, HOUGEKI_CUTIN, HITSTATUS
from data.static import FLEET_TYPE, SHIP_TYPE, EQUIP_TYPE_2, EQUIP_TYPE_3, EQUIP_TYPE_1
from calc.hougeki.gear_improvements import asw_gear_improvement, firepower_gear_improvement
from calc.hougeki.static import AP_SHELL_WEAK_SHIP_TYPES, ASW_DC_DCP_SONAR_SYNERGY, ASW_DC_DCP_SYNERGY, ASW_EQUIP_TYPE2, ASW_LEGACY_SONAR_SYNERGY, CL_SINGLE_GUN_ID, CL_TWIN_GUN_ID, DEPTH_CHARGE_ID, DEPTH_CHARGE_PROJECTOR_ID, FORMATION_MODIFIER, FORMATION_MODIFIER_ASW, FORMATION_MODIFIER_ECHELON_VS_CF, FORMATION_MODIFIER_VANGUARD_LHALF, FORMATION_MODIFIER_VANGUARD_LHALF_ASW, FORMATION_MODIFIER_VANGUARD_UHALF, FORMATION_MODIFIER_VANGUARD_UHALF_ASW, ZARA_CLASS_CTYPE
from calc.hougeki.special_attack import calculate_special_attack_modifier


class HougekiPrediction(BattleLogicBase):
    cap = 220

    def __init__(self, attacker_id: int, attacker_level: int, attacker_hp: int, attacker_max_hp: int, attacker_equip: List[int],
                 attacker_improvement: List[int], attacker_fleet: List[int], attacker_ammo: int,
                 attacker_firepower: int, attacker_torpedo: int, attacker_formation: int, attacker_combined: int, attacker_position: int,
                 defender_id: int, defender_hp: int, defender_max_hp: int, defender_equip: int, defender_armor: int, defender_combined,
                 damage: float, hitstatus: int, engagement: int, attacker_cutin: int, attacker_cutin_equips: List[int]):
        
        super().__init__(attacker_id, attacker_level, attacker_hp, attacker_max_hp, attacker_equip,
                 attacker_improvement, attacker_fleet, attacker_ammo,
                 attacker_firepower, attacker_torpedo, attacker_formation, attacker_combined, attacker_position, defender_id,
                 defender_hp, defender_max_hp, defender_equip, defender_armor, defender_combined,
                 damage, hitstatus, engagement)
        
        self.attacker_cutin = attacker_cutin
        self.attacker_cutin_equips = attacker_cutin_equips

    def is_valid_attack(self):
        return super().is_valid_attack() and not (self.attacker.is_carrier() and self.attacker_cutin == HOUGEKI_CUTIN.CARRIER_CUTIN
                                                 ) and not (self.attacker.is_carrier() and self.hitstatus == HITSTATUS.CRITICAL)
    

    def calculate_basic_power(self):

        if self.defender.is_submarine():
            return self.calculate_asw_power()
        
        if self.attacker.is_carrier():
            return self.calculate_carrier_basic_power()
        
        bap = self.attacker_firepower
        cf_factor = self.calculate_combined_fleet_factor()
        gear_improvement = sum([firepower_gear_improvement(equip, improvement) for equip, improvement in zip(self.attacker_equipment_mst, self.attacker_improvement)])
        return bap + cf_factor + gear_improvement + 5

        
    def calculate_asw_power(self):

        naked_asw = self.attacker.estimate_asw(self.attacker_level)
        asw_constant = 8 if self.attacker.ship_type in {SHIP_TYPE.BBV, SHIP_TYPE.CVL, SHIP_TYPE.CAV, SHIP_TYPE.AV, SHIP_TYPE.LHA} else 13
        equip_asw = sum([equip.anti_sub for equip in self.attacker_equipment_mst if equip.type_2 in ASW_EQUIP_TYPE2])
        gear_improvement = sum([asw_gear_improvement(equip, improvement) for equip, improvement in zip(self.attacker_equipment_mst, self.attacker_improvement)])
        
        bap = asw_constant + 2 * np.sqrt(naked_asw) + 1.5 * equip_asw + gear_improvement

        has_depth_charge = self.has_equipment_in_array(DEPTH_CHARGE_ID)
        has_depth_charge_projector = self.has_equipment_in_array(DEPTH_CHARGE_PROJECTOR_ID)

        if has_depth_charge and has_depth_charge_projector:
            synergy_modifier = ASW_DC_DCP_SYNERGY

            if self.has_equip_type2(EQUIP_TYPE_2.SONAR):
                synergy_modifier = ASW_DC_DCP_SONAR_SYNERGY

            bap *= synergy_modifier

        if self.has_equip_type3(EQUIP_TYPE_3.SONAR) and self.has_equip_type3(EQUIP_TYPE_3.DEPTH_CHARGE):
            bap *= ASW_LEGACY_SONAR_SYNERGY

        return bap

    
    def calculate_carrier_basic_power(self):

        bap = self.attacker_firepower
        bap += self.calculate_combined_fleet_factor()
        bap += int(sum([equip.torpedo for equip in self.attacker_equipment_mst]))
        bap += sum([firepower_gear_improvement(equip, improvement) for equip, improvement in zip(self.attacker_equipment_mst, self.attacker_improvement)])
        bap += int(1.3 * sum([equip.dive_bombing for equip in self.attacker_equipment_mst]))

        return 55 + int(1.5 * bap)
    
    def calculate_precap_power(self, basic_power: int) -> float:

        engagement_modifier = self.engagement_modifier()
        hp_modifier = self.hp_modifier()

        target_submarine = self.defender.is_submarine()
        if target_submarine:
            formation_modifier = FORMATION_MODIFIER_ASW.get(self.attacker_formation, 0)
        else:
            formation_modifier = FORMATION_MODIFIER.get(self.attacker_formation, 0)

        if self.attacker_formation == FORMATION.ECHELON and self.defender_combined:
            formation_modifier = FORMATION_MODIFIER_ECHELON_VS_CF

        elif self.attacker_formation == FORMATION.VANGUARD:
            if self.attacker_position >= int(len(self.attacker_fleet) / 2):
                formation_modifier = FORMATION_MODIFIER_VANGUARD_LHALF if not target_submarine else FORMATION_MODIFIER_VANGUARD_LHALF_ASW
            else:
                formation_modifier = FORMATION_MODIFIER_VANGUARD_UHALF if not target_submarine else FORMATION_MODIFIER_VANGUARD_UHALF_ASW

        precap_additive = 0

        if self.attacker.ship_type in {SHIP_TYPE.CL, SHIP_TYPE.CLT, SHIP_TYPE.CT}:
            precap_additive += np.sqrt(self.count_equip_in_array(CL_SINGLE_GUN_ID)) + 2 * np.sqrt(self.count_equip_in_array(CL_TWIN_GUN_ID))
        
        if self.attacker.class_type == ZARA_CLASS_CTYPE:
            precap_additive += np.sqrt(self.count_equip(162))

        return basic_power * engagement_modifier * hp_modifier * formation_modifier + precap_additive
    
    def calculate_postcap_power(self, capped_power: int):
        pcp = capped_power * calculate_special_attack_modifier(self, self.attacker_cutin)
        if self.defender.ship_type in AP_SHELL_WEAK_SHIP_TYPES and self.has_equip_type2(EQUIP_TYPE_2.AP_SHELL) and self.has_equip_type1(EQUIP_TYPE_1.MAIN_GUN):
            mod = 1.08

            if self.has_equip_type1(EQUIP_TYPE_1.SECONDARY_GUN):
                mod = 1.15

            elif self.has_equip_type1(EQUIP_TYPE_1.RADAR):
                mod = 1.1

            pcp = int(pcp * mod)
        return super().calculate_postcap_power(pcp)

    
    def calculate_combined_fleet_factor(self):
        attacker_is_in_main_fleet = self.attacker_position < 6

        if self.defender_combined == FLEET_TYPE.SINGLE:
            # CTF vs single
            if self.attacker_combined == FLEET_TYPE.CTF:
                return 2 if attacker_is_in_main_fleet else 10
            # STF vs single
            elif self.attacker_combined == FLEET_TYPE.STF:
                return 10 if attacker_is_in_main_fleet else -5
            # TCF vs single
            elif self.attacker_combined == FLEET_TYPE.TCF:
                return -5 if attacker_is_in_main_fleet else 10
            # Single vs Single
            else:
                return 0
            
        else:
             # CTF vs CF
            if self.attacker_combined == FLEET_TYPE.CTF:
                return 2 if attacker_is_in_main_fleet else -5
            # STF vs CF
            elif self.attacker_combined == FLEET_TYPE.STF:
                return 2 if attacker_is_in_main_fleet else -5
            # TCF vs CF
            elif self.attacker_combined == FLEET_TYPE.TCF:
                return -5
            # Single vs CF
            else:
                return 5
