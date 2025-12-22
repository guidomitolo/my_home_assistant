import requests
import json
import os
from typing import Any, Dict, List, Optional, Union
from HA_templates import HomeAssistantTemplates, build_payload

# Configuration
HA_URL = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
TOKEN = os.getenv('TOKEN')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def get_ha_data(payload: Dict[str, Any]) -> Any:
    """Sends a Jinja template to Home Assistant and returns parsed JSON data.

    Args:
        payload: The dictionary containing the 'template' string to be processed.

    Returns:
        The parsed JSON data (dict or list) if successful, the raw text if 
        JSON parsing fails, or None if an HTTP error occurs.
    """
    try:
        response = requests.post(
            url=f"{HA_URL}template", 
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result_data = response.json()
        
        # HA sometimes returns a JSON string inside a string; try to parse it
        if isinstance(result_data, str):
            try:
                return json.loads(result_data)
            except json.JSONDecodeError:
                return result_data
        return result_data

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_states(condition: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves entity states, optionally filtered by a condition.

    Args:
        condition: Filter state by value (e.g., 'on' or 'off'). 
            If None, retrieves all states.

    Returns:
        A list of dictionaries containing entity state information.
        Example: [{'entity_id': 'light.living_room', 'state': 'on', ...}]
    """
    if condition:
        payload = build_payload(HomeAssistantTemplates.STATES_BY_CONDITION, condition)
    else:
        payload = build_payload(HomeAssistantTemplates.ALL_STATES)
    return get_ha_data(payload) or []

def get_entity_info(entity_id: str) -> Dict[str, Any]:
    """Retrieves detailed metadata for a specific entity.

    Args:
        entity_id: The full entity ID (e.g., 'switch.shelly_kitchen').

    Returns:
        A dictionary containing area, device_id, attributes, and state.
    """
    payload = build_payload(HomeAssistantTemplates.SINGLE_ENTITY_INFO, entity_id)
    return get_ha_data(payload) or {}

def get_labels() -> List[str]:
    """Retrieves a list of all defined labels in Home Assistant.

    Returns:
        A list of strings representing label names.
        Example: ['luces', 'tv', 'consumo']
    """
    payload = build_payload(HomeAssistantTemplates.LIST_LABELS)
    return get_ha_data(payload) or []

def get_label_devices(label_name: str) -> List[Dict[str, Any]]:
    """Retrieves all devices associated with a specific label.

    Args:
        label_name: The label to filter by (e.g., 'consumo').

    Returns:
        A list of dictionaries containing device information and their entities.
    """
    payload = build_payload(HomeAssistantTemplates.LABEL_DEVICES, label_name)
    return get_ha_data(payload) or []

def get_areas() -> List[str]:
    """Retrieves a list of all area names defined in Home Assistant.

    Returns:
        A list of strings (e.g., ['cocina', 'salon', 'exterior']).
    """
    payload = build_payload(HomeAssistantTemplates.LIST_AREAS)
    return get_ha_data(payload) or []

def get_area_devices(area_name: str) -> List[Dict[str, Any]]:
    """Retrieves all devices and their entity states within a specific area.

    Args:
        area_name: The name of the area (e.g., 'tablero').

    Returns:
        A list of devices, including their child entities and current states.
    """
    payload = build_payload(HomeAssistantTemplates.AREA_DEVICES, area_name)
    return get_ha_data(payload) or []

def get_device_entities(device_id: str) -> List[Dict[str, str]]:
    """Retrieves all entities belonging to a specific device.

    Args:
        device_id: The unique device identifier.

    Returns:
        A list of dictionaries mapping entity IDs to their current states.
        Example: [{'entity_id': 'remote.tv', 'entity_state': 'on'}]
    """
    payload = build_payload(HomeAssistantTemplates.DEVICE_ENTITIES, device_id)
    return get_ha_data(payload) or []