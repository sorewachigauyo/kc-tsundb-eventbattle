"""Describes the basic logic used to calculate attack power
"""
from abc import ABC, abstractclassmethod
from typing import List, Dict
from functools import reduce
from collections import Counter

import numpy as np


from data.master import fetch_ship_master, fetch_equip_master, EquipMaster
from data.static import SHIP_TYPE
from battle.static import HITSTATUS
from calc.static import ASW_ARMOR_PENETRATION_EQUIPMENT, ENGAGEMENT_MODIFIER, HP_MODIFIER_CHUUHA, HP_MODIFIER_SHOUHA_PLUS, HP_MODIFIER_TAIHA, PT_IMP_ID, SURFACE_RADAR_TYPE2


class BattleLogicBase:
    """For calculating damage, there are generally 8 steps
    [PRECAP]
    1: Calculate the basic attack power
    2: Apply the anti-installation (or enemy like PT imp) modifiers
    3: Applying precap modifiers like engagement, formation and special attacks

    [CAP]
    4: Applying damage cap
    
    [POSTCAP]
    These two steps depend on the enemy ship type?
    6a: Apply AP modifier
    6b: Apply critical modifier

    7: Apply the anti-installation (or enemy like PT imp) modifiers
    8: Apply postcap modifiers like 
    """

    cap = 180

    def __init__(self, attacker_id: int, attacker_level: int, attacker_hp: int, attacker_max_hp: int, attacker_equip: List[int],
                 attacker_improvement: List[int], attacker_fleet: List[int], attacker_ammo: int,
                 attacker_firepower: int, attacker_torpedo: int, attacker_formation: int, attacker_combined: int, attacker_position: int,
                 defender_id: int, defender_hp: int, defender_max_hp: int, defender_equip: int, defender_armor: int, defender_combined,
                 damage: float, hitstatus: int, engagement: int):

        self.attacker_id = attacker_id
        self.attacker_level = attacker_level
        self.attacker = fetch_ship_master(attacker_id)
        self.attacker_hp = attacker_hp
        self.attacker_max_hp = attacker_max_hp
        self.attacker_equipment = np.array([mst_id for mst_id in attacker_equip if mst_id > 0])
        self.attacker_equipment_count = Counter(self.attacker_equipment)
        self.attacker_equipment_unique = set(self.attacker_equipment_count.keys())
        self.attacker_equipment_mst: List[EquipMaster] = np.array([fetch_equip_master(mst_id) for mst_id in self.attacker_equipment])
        self.attacker_improvement = np.array([imprv for imprv, mst_id in zip(attacker_improvement, attacker_equip) if mst_id > 0])
        self.attacker_fleet = attacker_fleet
        self.attacker_firepower = attacker_firepower
        self.attacker_torpedo = attacker_torpedo
        self.attacker_ammo = attacker_ammo
        self.attacker_formation = attacker_formation
        self.attacker_combined = attacker_combined
        self.attacker_position = attacker_position

        self.defender_id = defender_id
        self.defender = fetch_ship_master(defender_id)
        self.defender_hp = defender_hp
        self.defender_max_hp = defender_max_hp
        self.defender_equipment = np.array([equip for equip in defender_equip if equip > 0])
        self.defender_equipment_mst = np.array([fetch_equip_master(mst_id) for mst_id in self.defender_equipment])
        self.defender_armor = defender_armor
        self.defender_combined = defender_combined

        self.damage = int(damage)
        self.hitstatus = hitstatus
        self.engagement = engagement

        self._final_attack_power = None
        self._remaining_ammo_modifier = None
        self._enemy_armor = None
        
    def is_scratch_attack(self):
        return self.damage <= int(self.defender_hp * 0.06 + (self.defender_hp - 1) * 0.08)

    def is_valid_attack(self):
        return not (self.defender.is_installation()
                    #or self.defender.is_submarine()
                    or self.is_scratch_attack()
                    or self.defender_id in PT_IMP_ID
                    or self.hitstatus == HITSTATUS.MISS
                    or self.has_equipment(43)) # damegami

    def calculate_basic_power(self) -> int:
        pass

    def calculate_precap_power(self, basic_power: int) -> float:
        pass

    def apply_cap(self, power: float) -> int:
        if power > self.cap:
            return int(self.cap + np.sqrt(power))
        else:
            return int(power)

    def calculate_postcap_power(self, capped_power: int):
        if self.hitstatus == HITSTATUS.CRITICAL:
            return int(capped_power * 1.5)
        return int(capped_power)

    def final_attack_power(self):
        if self._final_attack_power is None:
            self._final_attack_power = self.calculate_postcap_power(self.apply_cap(self.calculate_precap_power(self.calculate_basic_power())))
        return self._final_attack_power

    def calculate_defender_armor(self):
        if self._enemy_armor is None:
            armor = self.defender_armor + reduce(lambda acc, equip: acc + equip.armor, self.defender_equipment_mst, 0)

            if self.defender.is_submarine():
                de_bonus = 0
                if self.attacker.ship_type == SHIP_TYPE.DE:
                    de_bonus = 1

                for equip_id, equip in zip(self.attacker_equipment, self.attacker_equipment_mst):
                    if equip_id in ASW_ARMOR_PENETRATION_EQUIPMENT:
                        armor -= np.sqrt(equip.anti_sub - 2) + de_bonus

                armor = max(armor, 1)
            
            self._enemy_armor = armor
        return self._enemy_armor
    
    def calculate_ammo_modifier(self):
        if self._remaining_ammo_modifier is None:
            ammo_ratio = self.attacker_ammo / self.attacker.max_ammo
            self._remaining_ammo_modifier = 1 if ammo_ratio >= 0.5 else ammo_ratio * 2

        return self._remaining_ammo_modifier
    
    def calculate_defender_armor_minmax(self):
        armor = self.calculate_defender_armor()
        return armor * 0.7, armor * 0.7 + 0.6 * (armor - 1)
    
    def calculate_expected_damage_bounds(self):
        armor_rolls = self.calculate_defender_armor_minmax()
        attack_power = self.final_attack_power()
        ram = self.calculate_ammo_modifier()

        return [int((attack_power - armor) * ram) for armor in reversed(armor_rolls)]
    
    def is_abnormal_instance(self):
        b1, b2 = self.calculate_expected_damage_bounds()
        return self.damage > b2
    
    def reverse_bonus_calculation(self):
        dmg = self.damage
        ram = self.calculate_ammo_modifier()
        armor_lbound, armor_ubound = self.calculate_defender_armor_minmax()
        fap = self.final_attack_power()

        if self.hitstatus == HITSTATUS.CRITICAL:
            return (
                (dmg / ram + armor_lbound) / fap,
                ((dmg + 1) / ram + armor_ubound + 1) / fap,
            )
        else:
            return (
                (dmg / ram + armor_lbound) / fap,
                ((dmg + 1) / ram + armor_ubound) / fap,
            )

    def has_equipment(self, equip_id: int):
        return equip_id in self.attacker_equipment_unique
    
    def has_equipment_in_array(self, equipment_array: set):
        return not equipment_array.isdisjoint(self.attacker_equipment_unique)
    
    def has_equip_type2(self, equip_type: int):
        return next((equip for equip in self.attacker_equipment_mst
                     if equip.type_2 == equip_type), False)
    
    def has_equip_type3(self, equip_type: int):
        return next((equip for equip in self.attacker_equipment_mst
                     if equip.type_3 == equip_type), False)
    
    def has_equip_type1(self, equip_type: int):
        return next((equip for equip in self.attacker_equipment_mst
                     if equip.type_1 == equip_type), False)
    
    def count_equip(self, equip_id: int):
        return self.attacker_equipment_count.get(equip_id, 0)
    
    def count_equip_in_array(self, equip_array: set):
        return reduce(lambda acc, mst_id: acc + self.count_equip(mst_id), np.intersect1d(self.attacker_equipment_unique, equip_array, True), 0)

    def engagement_modifier(self):
        return ENGAGEMENT_MODIFIER[self.engagement]
    
    def hp_modifier(self):
        hp_ratio = self.attacker_hp / self.attacker_max_hp

        if hp_ratio <= 0.25:
            return HP_MODIFIER_TAIHA
        elif hp_ratio <= 0.5:
            return HP_MODIFIER_CHUUHA
        else:
            return HP_MODIFIER_SHOUHA_PLUS
        
    def has_surface_radar(self):
        return next((equip for equip in self.attacker_equipment_mst
                     if equip.type_2 in SURFACE_RADAR_TYPE2 and equip.los > 4), False)
