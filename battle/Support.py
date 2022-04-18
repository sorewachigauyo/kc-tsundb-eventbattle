from battle.static import HITSTATUS, HouraiAttackSupport, KoukuAttackSupport
from objects.static import SIDE

# Shelling + Torpedo Support
def SupportHourai(rawapi: dict, phase: str):
    return [
        HouraiAttackSupport(
            defender=ship_idx,
            damage=rawapi["api_damage"][ship_idx],
            hitstatus=hitstatus,
            phase=phase,
            side=SIDE.PLAYER
        ) for ship_idx, hitstatus in enumerate(rawapi["api_cl_list"])
        if hitstatus > 0
    ]

# Aerial + ASW Support
def SupportKouku(rawapi: dict, phase: str):
    return [
        KoukuAttackSupport(
            defender=ship_idx,
            damage=damage,
            hitstatus=HITSTATUS.CRITICAL if rawapi["api_ecl"][ship_idx] else HITSTATUS.HIT,
            phase=phase,
            db=rawapi["api_ebak_flag"][ship_idx] == 1,
            tb=rawapi["api_erai_flag"][ship_idx] == 1,
            side=SIDE.PLAYER
        ) for ship_idx, damage in enumerate(rawapi["api_edam"])
        if rawapi["api_erai_flag"][ship_idx] or rawapi["api_ebak_flag"][ship_idx]
    ]

