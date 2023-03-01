from data.master import is_abyssal_ship, fetch_ship_master
from dataclasses import dataclass
from typing import List

@dataclass
class Ship:
    id: int
    level: int
    equipment: List[int]
    firepower: int
    torpedo: int
    anti_air: int
    armor: int
    starting_hp: int
    max_hp: int
    improvement: List[int] = None
    ammo: int = None

    def __post_init__(self):
        if self.improvement is None:
            self.improvement = [-1 for _ in self.equipment]

        if self.ammo is None and not is_abyssal_ship(self.id):
            self.ammo = fetch_ship_master(self.id).max_ammo
