"""Describes the basic logic used to calculate attack power
"""
from abc import ABC, abstractclassmethod
from typing import Tuple

import numpy as np

from database.models import PlayerShip, Attack

class BattleLogicBase(ABC):
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

    @abstractclassmethod
    def calculate_basic_power(ship: PlayerShip):
        pass

    def apply_cap(self, power: float) -> int:
        if power > self.cap:
            return int(self.cap + np.sqrt(power))
        else:
            return int(power)

    @abstractclassmethod
    def calculate_attack(attack: Attack, params: dict) -> Tuple[int, int, float]:
        pass