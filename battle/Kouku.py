from battle.static import KOUKU_SIDE_TERMS, KoukuAttack, HITSTATUS, KoukuAttackLB
from objects.static import SIDE

def Kouku(rawapi: dict, phase: str, side: int, combined=False):
    pad = 6 if combined else 0
    dmg_key, critical_key, bak_flag_key, rai_flag_key = KOUKU_SIDE_TERMS[side]
    return [
        KoukuAttack(
            defender=ship_idx + pad,
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if rawapi[critical_key][ship_idx] else HITSTATUS.HIT,
            phase=phase,
            db=rawapi[bak_flag_key][ship_idx] == 1,
            tb=rawapi[rai_flag_key][ship_idx] == 1,
            side=side
        ) for ship_idx, damage in enumerate(rawapi[dmg_key])
        if rawapi[rai_flag_key][ship_idx] or rawapi[bak_flag_key][ship_idx]
    ]

def LBKouku(rawapi: dict, phase: str, wave: int, combined=False):
    pad = 6 if combined else 0
    return [
        KoukuAttackLB(
            defender=ship_idx + pad,
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if rawapi["api_ecl_flag"][ship_idx] else HITSTATUS.HIT,
            phase=phase,
            db=rawapi["api_ebak_flag"][ship_idx] == 1,
            tb=rawapi["api_erai_flag"][ship_idx] == 1,
            wave=wave,
            side=SIDE.PLAYER
        ) for ship_idx, damage in enumerate(rawapi["api_edam"])
        if rawapi["api_erai_flag"][ship_idx] or rawapi["api_ebak_flag"][ship_idx]
    ]
