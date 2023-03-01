from typing import List, Union


from api_parsing.phase import parse_hougeki, parse_midnight, parse_kouku, parse_raigeki, parse_support
from battle.static import BATTLE_TYPE_ORDER_MAPPING, PHASE
from api_parsing.static import KoukuAttack, MidnightAttack, HougekiAttack, RaigekiAttack


def parse_landbase(rawapi: List[dict], phase: str) -> List[KoukuAttack]:
    ret = []
    for wave, data in enumerate(rawapi):
        ret += parse_kouku(data, phase, wave)
    return ret

def parse_battle(battle_type: str, rawapi: dict) -> List[Union[HougekiAttack, RaigekiAttack, KoukuAttack, MidnightAttack]]:
    all_phases = BATTLE_TYPE_ORDER_MAPPING[battle_type]
    attacks = []
    
    for phase in all_phases:
        phase_data = rawapi.get(phase)
        if phase_data:
            attacks += phase_handlers[phase](phase_data, phase)

    return attacks

phase_handlers = {
    PHASE.LAND_BASE_JET: parse_kouku,
    PHASE.JET: parse_kouku,
    PHASE.LAND_BASE: parse_landbase,
    PHASE.FRIENDLY_AIRBATTLE: parse_kouku,
    PHASE.AIRBATTLE: parse_kouku,
    PHASE.AIRBATTLE2: parse_kouku,
    PHASE.SUPPORT: parse_support,
    PHASE.OPENING_ASW: parse_hougeki,
    PHASE.OPENING_TORPEDO: parse_raigeki,
    PHASE.SHELLING: parse_hougeki,
    PHASE.SHELLING2: parse_hougeki,
    PHASE.SHELLING3: parse_hougeki,
    PHASE.CLOSING_TORPEDO: parse_raigeki,

    PHASE.FRIENDLY_SHELLING: parse_midnight,
    PHASE.NIGHT_SUPPORT: parse_support,
    PHASE.NIGHT_SHELLING: parse_midnight,
    PHASE.NIGHT_SHELLING2: parse_midnight,
}
