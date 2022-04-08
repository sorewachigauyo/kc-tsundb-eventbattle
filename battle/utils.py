from objects.Ship import EnemyShip, PlayerShip
from utils import fetch_ship_master

def calculate_damage_range(attacker: PlayerShip, defender: EnemyShip, num: float):
    armor = defender.ar + defender._fetch_equipment_total_stats("souk")
    ammo_percent = attacker.ammo / fetch_ship_master(attacker.id)["api_bull_max"]
    ram = 1 if ammo_percent >= 0.5 else ammo_percent * 2

    min_val = int((num - armor * 0.7) * ram)
    max_val = int((num - armor * 0.7 - (armor - 1) * 0.6) * ram)
    return min_val, max_val

def is_scratch(dafender: EnemyShip, damage: float):
    return damage >= int(dafender.hp[0] * 0.06 + (dafender.hp[0] - 1) * 0.08)


    
