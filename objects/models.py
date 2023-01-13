from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ShipBase:
    id: int
    position: int
    hp: Tuple[int]
    equipment: List[int]
    firepower: int
    torpedo: int
    anti_air: int
    armor: int

    stype: int = None

    def __post_init__(self):
        pass
