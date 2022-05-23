import json
from battle.Hougeki import process_hougeki
from battle.Midnight import process_midnight
from battle.Raigeki import process_raigeki
from battle.static import HougekiAttack, MidnightAttack, RaigekiAttack
from battle.utils import handle_battle, is_scratch, calculate_damage_range, handle_attack, reversed_attack_power
from objects.Battle import Battle

with open("./raw/E5-3.json") as r:
    data = json.load(r)

apiname = data["apiname"]
# early version on EO, no need for string reload into dict
rawapi = json.loads(data["rawapi"])
playerformation = data["playerformation"]
resupplyused = data["resupplyused"]
fleet = data["fleet"]
battle = Battle(apiname, rawapi, playerformation, resupplyused, fleet)
attacks = handle_battle(battle, rawapi)


for attack in attacks:
    dmg = int(attack.damage)
    if isinstance(attack, RaigekiAttack) and attack.hitstatus > 0:
        attacker, defender, num = process_raigeki(attack, battle)
        lbound, ubound = calculate_damage_range(attacker, defender, num)

    elif isinstance(attack, HougekiAttack) and attack.hitstatus > 0 and attack.cutin < 300:

        attacker, defender, num = process_hougeki(attack, battle)
        lbound, ubound = calculate_damage_range(attacker, defender, num)

    elif isinstance(attack, MidnightAttack) and attack.hitstatus > 0 and attack.cutin < 300:

        attacker, defender, num = process_midnight(attack, battle)
        lbound, ubound = calculate_damage_range(attacker, defender, num)

        if not is_scratch(defender, dmg) and dmg > ubound:
            reversed_num_low, reversed_num_high = reversed_attack_power(
                attacker, defender, dmg)
            print(f"Ship {attacker.id}")
            print(f"Expected Damage Range: {lbound} - {ubound}")
            print(f"Actual Damage: {dmg}")
            lmod = reversed_num_low / num
            umod = reversed_num_high / num
            print(f"Estimated Bonus Range: {lmod} - {umod}")
            print()

    handle_attack(attack, battle)
