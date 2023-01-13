from tsundb_parser.phase import parse_hougeki, parse_midnight
from data.static_battle import BATTLE_TYPE_ORDER_MAPPING

phase_handler = {}

def parse_battle(battle_type: str, rawapi: dict):
    all_phases = BATTLE_TYPE_ORDER_MAPPING[battle_type]
    attacks = []
    
    for phase in all_phases:
        handler = phase_handler[phase]
        phase_data = rawapi.get(phase)
        attacks += handler(phase_data, phase)

    return attacks