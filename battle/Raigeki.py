from battle.static import RaigekiAttack
from objects.static import SIDE


def Raigeki(rawapi: dict, phase: str):
    return [
        RaigekiAttack(idx, frai, rawapi["api_fydam"][idx],
                      rawapi["api_fcl"][idx], phase, side=SIDE.PLAYER) for idx, frai in 
                      enumerate(rawapi["api_frai"]) if frai > -1
    ] + [
        RaigekiAttack(idx, erai, rawapi["api_eydam"][idx],
                      rawapi["api_ecl"][idx], phase, side=SIDE.ENEMY) for idx, erai in 
                      enumerate(rawapi["api_erai"]) if erai > -1
    ]
