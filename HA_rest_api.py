import requests
import json
import os
import time
import HA_schemas as schemas
from HA_schemas import SwitchCommand
from HA_api_session import HAClient
from typing import Any, Dict, List, Optional, Union
from HA_templates import HomeAssistantTemplates, build_payload
from datetime import datetime

# API Configuration
HA_URL = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
TOKEN = os.getenv('TOKEN')


def is_valid_datetime(date_string: str, format_string: str) -> bool:
    """
    Internal utility to validate if a string matches a specific datetime format.
    
    Args:
        date_string: The string date to validate.
        format_string: The expected strftime format (e.g., '%Y-%m-%dT%H:%M:%S%z').

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_string, format_string)
        return True
    except (ValueError, TypeError):
        return False

def get_HA_template_data(payload: Dict[str, Any]) -> Any:
    """
    Executes a Jinja2 template on the Home Assistant server and returns the processed result.
    Useful for complex data extraction that standard REST endpoints don't support directly.

    Args:
        payload: A dictionary containing a 'template' key with the Jinja2 code.

    Returns:
        The processed data, automatically parsed from JSON if possible. 
        Returns None if the communication with Home Assistant fails.
    """
    try:
        client = HAClient(HA_URL, TOKEN)
        response = client.post("template", payload)
        response.raise_for_status()
        result_data = response.json()
        
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
    """
    Retrieves all user-defined labels in Home Assistant. Labels are used to 
    categorize multiple devices across different areas (e.g., 'Security', 'Energy').

    Returns:
        List[str]: A list of label identifiers.
    """
    template_payload = build_payload(HomeAssistantTemplates.LIST_LABELS)
    return get_HA_template_data(template_payload) or []

def get_areas() -> List[str]:
    """
    Retrieves all defined area names (rooms or zones) in Home Assistant.
    Example areas: 'kitchen', 'living_room', 'garage'.

    Returns:
        List[str]: A list of area names.
    """
    template_payload = build_payload(HomeAssistantTemplates.LIST_AREAS)
    return get_HA_template_data(template_payload) or []


### GET DEVICES per AREA or LABEL

def get_area_devices(area_name: str) -> List[schemas.Device]:
    """
    Lists all hardware devices located within a specific area and includes their 
    associated entity states.

    Args:
        area_name: The name of the area to query (e.g., 'living_room').

    Returns:
        List[schemas.Device]: A list of Device objects, each containing its 
        entities and their current states.
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
    """
    Retrieves all devices tagged with a specific label, regardless of which 
    area they are in.

    Args:
        label_name: The label to filter by (e.g., 'lights').

    Returns:
        List[schemas.Device]: A list of Device objects associated with the label.
    """
    devices = []
    template_payload = build_payload(HomeAssistantTemplates.LABEL_DEVICES, label_name)
    response = get_HA_template_data(template_payload) or []
    for data in response:
        try:
            devices.append(schemas.Device(**data))
        except Exception as e:
            print(f"Error parsing device {data.get('device_id')}: {e}")
    return devices

# GET ENTITY or ENTITIES

def get_entity_info(entity_id: str) -> schemas.Entity:
    """
    Retrieves comprehensive metadata for a specific entity, including its 
    parent device, area assignment, and current attributes.

    Args:
        entity_id: The full Home Assistant entity ID (e.g., 'light.desk_lamp').

    Returns:
        schemas.Entity: An object containing state, attributes, device_id, and area.
    """
    template_payload = build_payload(HomeAssistantTemplates.SINGLE_ENTITY_INFO, entity_id)
    data = get_HA_template_data(template_payload) or {}
    entity = schemas.Entity(**data)
    return entity


def get_device_entities(device_id: str) -> List[schemas.Entity]:
    """
    Retrieves all functional entities (sensors, switches, etc.) belonging to 
    a single physical device.

    Args:
        device_id: The unique identifier of the device.

    Returns:
        List[schemas.Entity]: A list of entities associated with the device.
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
    """
    Queries Home Assistant for all entities currently matching a specific state 
    value (e.g., finding all lights that are 'on').

    Args:
        condition: The state value to filter by (e.g., 'on', 'off', 'unavailable'). 
            If None, returns states for all entities.

    Returns:
        List[schemas.StateCore]: A list of matching entity states.
    """
    states = []
    if condition:
        template_payload = build_payload(HomeAssistantTemplates.STATES_BY_CONDITION, condition)
        response = get_HA_template_data(template_payload) or []
        for data in response:
            try:
                states.append(schemas.StateCore(**data))
            except Exception as e:
                print(f"Error parsing state {data.get('state_id')}: {e}")
    return states

def get_entity_state(entity_id: str) -> Optional[schemas.State]:
    """
    Fetches the current state, last updated time, and all attributes for a 
    specific entity.

    Args:
        entity_id: The full entity ID (e.g., 'sensor.living_room_temp').

    Returns:
        Optional[schemas.State]: The state object if found, or None if the 
        entity does not exist or the API is unreachable.
    """
    try:
        client = HAClient(HA_URL, TOKEN)
        response = client.get(f"states/{entity_id}")
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

def get_states(cheaper: bool = False) -> Optional[Union[List[schemas.State], List[schemas.StateCore]]]:
    """
    Snapshots the current state of every entity in the Home Assistant instance.

    Args:
        cheaper: If True, returns a lightweight version of the state (StateCore) 
            to reduce data processing and token usage.

    Returns:
        Optional[List[schemas.State]]: A list of all entity states, or None 
        on error.
    """
    schema = {
        True: schemas.StateCore,
        False: schemas.State
    }
    states = []
    try:
        client = HAClient(HA_URL, TOKEN)
        response = client.get("states")
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
    limit: int = 20
) -> Optional[List[schemas.HistoryState]]:
    """
    Retrieves the historical states of an entity over a period of time. 
    Useful for analyzing trends or finding when a device was last used.

    Args:
        entity_id: The entity to query.
        start_time: Start of the period in ISO 8601 format (YYYY-MM-DDThh:mm:ssZ).
        end_time: End of the period in ISO 8601 format.
        limit: Max number of history records to return (default 20).

    Returns:
        Optional[List[schemas.HistoryState]]: A list of historical state records.
    """
    time_format = "%Y-%m-%dT%H:%M:%S%z"
    history_endpoint = "history/period"
    
    if start_time and is_valid_datetime(start_time, time_format):
        history_endpoint = f"{history_endpoint}/{start_time}"

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
        client = HAClient(HA_URL, TOKEN)
        response = client.get(history_endpoint, params=params)
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

def trigger_service(entity_id: str, command: SwitchCommand) -> Optional[schemas.State]:
    """
    Executes an action (turn_on, turn_off, toggle) on a specific entity. 
    This function automatically determines the correct domain (light, switch, etc.) 
    based on the entity_id provided.

    Args:
        entity_id: The full entity ID to control (e.g., 'light.bedroom').
        command: The action to perform. Must be a value from schemas.SwitchCommand.

    Returns:
        Optional[schemas.State]: The state of the entity after the action, 
        allowing for verification of the change.
    """

    if not isinstance(command, SwitchCommand):
        print(f"Invalid command type. Expected SwitchCommand, got {type(command)}")
        return None

    try:
        domain = entity_id.split('.')[0]
    except (ValueError, AttributeError):
        print(f"Invalid entity_id format: {entity_id}")
        return None

    service_action = f"turn_{command.value}" if command != SwitchCommand.TOGGLE else "toggle"
    service_endpoint = f"services/{domain}/{service_action}"

    try:
        client = HAClient(HA_URL, TOKEN)
        response = client.post(service_endpoint, json_data={"entity_id": entity_id})
        response.raise_for_status()

        if domain in ['switch', 'light', 'fan']:
            time.sleep(1)
            return get_entity_state(entity_id)

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None