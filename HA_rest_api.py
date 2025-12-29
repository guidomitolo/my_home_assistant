import requests
import json
import os
import time
from typing import Any, Dict, List, Optional, Union
from HA_templates import HomeAssistantTemplates, build_payload
import HA_schemas as schemas
from datetime import datetime


# Configuration
HA_URL = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
TOKEN = os.getenv('TOKEN')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def is_valid_datetime(date_string: str, format_string: str) -> bool:
    """Validates if a string matches a specific datetime format.

    Args:
        date_string: The string representation of a date.
        format_string: The expected strftime format (e.g., '%Y-%m-%d').

    Returns:
        True if the string matches the format, False otherwise.
    """
    try:
        datetime.strptime(date_string, format_string)
        return True
    except (ValueError, TypeError):
        return False

def get_HA_template_data(payload: Dict[str, Any]) -> Any:
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







### GET AREAS or LABELS

def get_labels() -> List[str]:
    """Retrieves a list of all defined labels in Home Assistant.

    Returns:
        A list of strings representing label names.
        Example: ['luces', 'tv', 'consumo']
    """
    template_payload = build_payload(HomeAssistantTemplates.LIST_LABELS)
    return get_HA_template_data(template_payload) or []

def get_areas() -> List[str]:
    """Retrieves a list of all area names defined in Home Assistant.

    Returns:
        A list of strings (e.g., ['cocina', 'salon', 'exterior']).
    """
    template_payload = build_payload(HomeAssistantTemplates.LIST_AREAS)
    return get_HA_template_data(template_payload) or []


### GET DEVICES per AREA or LABEL

def get_area_devices(area_name: str) -> List[schemas.Device]:
    """Retrieves all devices and their entity states within a specific area.

    Args:
        area_name: The name of the area (e.g., 'tablero').

    Returns:
        A list of devices, including their child entities and current states.
    """
    devices = []
    template_payload = build_payload(HomeAssistantTemplates.AREA_DEVICES, area_name)
    response = get_HA_template_data(template_payload) or []
    for data in response:
        try:
            devices.append(schemas.Device(**data))
        except Exception as e:
            print(f"Error parsing device {data.get('device_id')}: {e}")
    return devices

def get_label_devices(label_name: str) -> List[schemas.Device]:
    """Retrieves all devices associated with a specific label.

    Args:
        label_name: The label to filter by (e.g., 'consumo').

    Returns:
        A list of dictionaries containing device information and their entities.
    """
    devices = []
    template_payload = build_payload(HomeAssistantTemplates.LABEL_DEVICES, label_name)
    response = get_HA_template_data(template_payload)
    for data in response:
        try:
            devices.append(schemas.Device(**data))
        except Exception as e:
            print(f"Error parsing device {data.get('device_id')}: {e}")
    return devices

# GET ENTITY or ENTITIES

def get_entity_info(entity_id: str) -> schemas.Entity:
    """Retrieves detailed metadata for a specific entity.

    Args:
        entity_id: The full entity ID (e.g., 'switch.shelly_kitchen').

    Returns:
        A dictionary containing area, device_id, attributes, and state.
    """
    template_payload = build_payload(HomeAssistantTemplates.SINGLE_ENTITY_INFO, entity_id)
    data = get_HA_template_data(template_payload) or {}
    entity = schemas.Entity(**data)
    return entity


def get_device_entities(device_id: str) -> List[schemas.Entity]:
    """Retrieves all entities belonging to a specific device.

    Args:
        device_id: The unique device identifier.

    Returns:
        A list of dictionaries mapping entity IDs to their current states.
        Example: [{'entity_id': 'remote.tv', 'entity_state': 'on'}]
    """
    entities = []
    template_payload = build_payload(HomeAssistantTemplates.DEVICE_ENTITIES, device_id)
    response = get_HA_template_data(template_payload)
    for data in response:
        try:
            entities.append(schemas.Entity(**data))
        except Exception as e:
            print(f"Error parsing entity {data.get('entity_id')}: {e}")
    return entities


### GET STATES or STATES

def get_states_by_condition(condition: Optional[str] = None) -> List[schemas.StateCore]:
    """Retrieves entity states, optionally filtered by a condition.

    Args:
        condition: Filter state by value (e.g., 'on' or 'off'). 
            If None, retrieves all states.

    Returns:
        A list of dictionaries containing entity state information.
        Example: [{'entity_id': 'light.living_room', 'state': 'on', ...}]
    """
    states = []
    if condition:
        template_payload = build_payload(HomeAssistantTemplates.STATES_BY_CONDITION, condition)
        response = get_HA_template_data(template_payload)
        for data in response:
            try:
                states.append(schemas.StateCore(**data))
            except Exception as e:
                print(f"Error parsing state {data.get('state_id')}: {e}")
    return states

def get_entity_state(entity_id: str) -> Optional[schemas.State]:
    """Retrieves the full state object for a specific Home Assistant entity.

    Args:
        entity_id: The full entity ID (e.g., 'light.kitchen_main' or 'sensor.temperature').

    Returns:
        A dictionary containing the state, attributes, and metadata, 
        or None if the request fails or the entity is not found.
    """
    try:
        response = requests.get(
            url=f"{HA_URL}states/{entity_id}", 
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        state = schemas.State(**data)
        return state

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_states(cheaper:bool=False) -> Optional[List[schemas.State]]:
    """Retrieves the current state of all Home Assistant entities.

    Returns:
        A list of state objects (dictionaries) if successful; None if the 
        request fails or a connection error occurs.
    """
    schema = {
        True: schemas.StateCore,
        False: schemas.State
    }
    states = []
    try:
        response = requests.get(
            url=f"{HA_URL}states", 
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        for state in data:
            states.append(schema[cheaper](**state))
        return states

    except requests.exceptions.RequestException as e:
        print(f"Home Assistant API connection error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in get_states: {e}")
        return None

#### GET ENTITY' STATE HISTORY 

def get_history(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
    limit: int = 20  # Added a default limit to protect tokens
) -> Optional[List[schemas.HistoryState]]:
    """Retrieves state history for a specific entity.

    Args:
        entity_id: The Home Assistant entity ID.
        start_time: ISO 8601 formatted string (YYYY-MM-DDThh:mm:ssZ).
        end_time: ISO 8601 formatted string.
        limit: The maximum number of historical states to return.

    Returns:
        A list of state changes limited to the most recent 'limit' items.
    """
    time_format = "%Y-%m-%dT%H:%M:%S%z"
    base_url = f"{HA_URL}history/period"
    
    if start_time and is_valid_datetime(start_time, time_format):
        base_url = f"{base_url}/{start_time}"

    params = {
        "filter_entity_id": entity_id,
        "minimal_response": "",
        "no_attributes": "",
        "significant_changes_only": ""
    }

    if end_time and is_valid_datetime(end_time, time_format):
        params["end_time"] = end_time

    history = []
    try:
        print("SEEEEEE:", entity_id, start_time, end_time)
        response = requests.get(
            url=base_url,
            headers=HEADERS,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, list) and len(data) > 0:
            history_list = data[0]
            history += [schemas.HistoryState(**record) for record in history_list[-limit:] ]
        
        return history

    except requests.exceptions.RequestException as e:
        print(f"Error fetching history for {entity_id}: {e}")
        return None

### TURN ON / OFF ENTITYE // CHANGE ENTITY' STATE

def trigger_service(entity_id: str, command: str) -> Optional[schemas.State]:
    """Triggers a turn_on or turn_off service for a specific entity.

    This function automatically detects the domain (e.g., 'switch', 'light') 
    from the entity_id to call the correct service.

    Args:
        entity_id: The full entity ID to control (e.g., 'switch.pool_pump').
        command: The action to perform. Accepted values are 'on' or 'off'.

    Returns:
        The updated entity state object after the command is executed. 
        Returns None if the command is invalid or the request fails.
    """
    # Mapping simple commands to Home Assistant service actions
    commands = {
        'on': 'turn_on',
        'off': 'turn_off'
    }
    
    action = commands.get(command.lower())
    if not action:
        print(f"Invalid command: {command}. Use 'on' or 'off'.")
        return None

    try:
        domain = entity_id.split('.')[0]
    except (ValueError, AttributeError):
        print(f"Invalid entity_id format: {entity_id}")
        return None

    try:
        response = requests.post(
            url=f"{HA_URL}services/{domain}/{action}", 
            headers=HEADERS,
            timeout=10,
            json={"entity_id": entity_id}
        )
        response.raise_for_status()

        if domain in ['switch', 'light']:
            time.sleep(1) # Wait for updated state
            return get_entity_state(entity_id)

        data = response.json()
        
        return data

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None