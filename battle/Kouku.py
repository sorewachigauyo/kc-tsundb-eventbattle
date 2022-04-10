from battle.static import KoukuAttack
from objects.static import PHASE, SIDE


def Kouku(rawapi: dict, phase: str):
    return [
        KoukuAttack(
            side=SIDE.PLAYER if phase != PHASE.FRIENDLY_AIRBATTLE else SIDE.FRIEND
        )
    ] + [
        KoukuAttack(
            side=SIDE.ENEMY
        )
    ]

def LBKouku(rawapi: dict, phase: str, wave: int):
    pass
