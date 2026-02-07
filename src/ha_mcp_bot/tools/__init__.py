import logging
from .action import run_entity_command
from .groups import (
    get_areas, 
    get_area_devices, 
    get_labels,
    get_label_devices,
    get_states_by_condition,
    get_device_entities
)
from .lookup import (
    get_all_entities_state, 
    get_entity_information,
    get_entity_state,
)
from .search import search_entities
from .trends import analyze_entity_trends, calculate_electrical_delta, get_entity_state_history


logger = logging.getLogger(__name__)


HANDLERS = {
    'get_HA_areas': get_areas,
    'get_HA_devices_per_area': get_area_devices,
    'get_HA_all_entities_state': get_all_entities_state,
    'get_HA_states_by_condition': get_states_by_condition,
    'get_HA_entity_state_history': get_entity_state_history,
    'analyze_HA_entity_trends': analyze_entity_trends,
    'get_HA_entity_info': get_entity_information,
    'get_HA_labels': get_labels,
    'get_HA_devices_per_label': get_label_devices,
    'get_HA_entities_per_device': get_device_entities,
    'get_HA_entity_state': get_entity_state,
    'trigger_HA_service': run_entity_command,
    'search_HA_entities': search_entities,
    'calculate_HA_electrical_delta': calculate_electrical_delta,
}


def register_tools(mcp):
    for name, func in HANDLERS.items():
        mcp.tool(name=name)(func)
        logger.info(f"Registered tool: {name}")