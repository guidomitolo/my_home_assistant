import requests
import json
import schemas as schemas
from custom_api.session import HAClient
from typing import Any, Dict, List, Optional, Union
from custom_api.templates import HomeAssistantTemplates, build_payload
from datetime import datetime
from .base import HA_URL, TOKEN


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

def get_labels() -> List[schemas.Label]:
    """
    Retrieves all user-defined labels in Home Assistant. Labels are used to 
    categorize multiple devices or entities across different areas 
    (e.g., 'Security', 'Energy').

    Returns:
        List[schemas.Label]: A list of label objects containing id, name and description of each.
    """
    labels = []
    template_payload = build_payload(HomeAssistantTemplates.LIST_LABELS)
    response = get_HA_template_data(template_payload) or []
    for data in response:
        try:
            labels.append(schemas.Label(**data))
        except Exception as e:
            print(f"Error parsing label {data.get('label_id')}: {e}")
    return labels

def get_areas() -> List[schemas.Area]:
    """
    Retrieves all defined area names (rooms or zones) in Home Assistant.
    Example areas: 'kitchen', 'living_room', 'garage'.

    Returns:
        List[schemas.Area]: A list of area objects containing id and name.
    """
    areas = []
    template_payload = build_payload(HomeAssistantTemplates.LIST_AREAS)
    response = get_HA_template_data(template_payload) or []
    for data in response:
        try:
            areas.append(schemas.Area(**data))
        except Exception as e:
            print(f"Error parsing area {data.get('area_id')}: {e}")
    return areas

### GET DEVICES per AREA or LABEL

def get_area_devices(area_name: str) -> List[schemas.Device]:
    """
    Lists all hardware devices located within a specific area and includes their 
    associated entity states.

    Args:
        area_name: The name of the area to query (e.g., 'living_room').

    Returns:
        List[schemas.Device]: A list of Device objects, each containing its
        labels and entities with their current states.
    """
    devices = []
    template_payload = build_payload(HomeAssistantTemplates.AREA_DEVICES, area_name)
    response = get_HA_template_data(template_payload)
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
        List[schemas.Device]: A list of Device objects associated with the label, 
        each containing its area and entities with their current states.
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

# GET ENTITIES per AREA or LABEL

def get_area_entities(area_name: str) -> List[schemas.Entity]:
    """
    Lists all entities belonging to a device located within a specific area 

    Args:
        area_name: The name of the area to query (e.g., 'living_room').

    Returns:
        List[schemas.Entity]: A list of Entity objects, each containing its
        labels.
    """
    entities = []
    template_payload = build_payload(HomeAssistantTemplates.AREA_ENTITIES, area_name)
    response = get_HA_template_data(template_payload)
    for data in response:
        try:
            entities.append(schemas.Entity(**data))
        except Exception as e:
            print(f"Error parsing entity {data.get('entity_id')}: {e}")
    return entities

def get_label_entities(label_name: str) -> List[schemas.Entity]:
    """
    Retrieves all entities that belong to a device tagged with a specific label, 
    regardless of which area they are in.

    Args:
        label_name: The label to filter by (e.g., 'lights').

    Returns:
        List[schemas.Entity]: A list of Entity objects associated with the label
    """
    entities = []
    template_payload = build_payload(HomeAssistantTemplates.LABEL_ENTITIES, label_name)
    response = get_HA_template_data(template_payload) or []
    for data in response:
        try:
            entities.append(schemas.Entity(**data))
        except Exception as e:
            print(f"Error parsing entity {data.get('entity_id')}: {e}")
    return entities


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


def get_all_entities() -> List[schemas.Entity]:
    """
    Retrieves all entities.

    Args:
        device_id: The unique identifier of the device.

    Returns:
        List[schemas.Entity]: A list of entities associated with the device.
    """
    entities = []
    template_payload = build_payload(HomeAssistantTemplates.ALL_ENTITITES)
    response = get_HA_template_data(template_payload) or []
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
) -> List[Union[schemas.HistoryNumericState, schemas.HistoryCategoricalState]]:
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
        Example: [
            HistoryState(state='215.8', last_changed=datetime.datetime(2026, 1, 3, 21, 31, 11, 936891, tzinfo=TzInfo(0)), state_class='measurement', unit_of_measurement='W', device_class='power'), 
            HistoryState(state='213.1', last_changed=datetime.datetime(2026, 1, 3, 21, 31, 20, 928893, tzinfo=TzInfo(0)), state_class='measurement', unit_of_measurement='W', device_class='power')
        ]
    """
    time_format = "%Y-%m-%dT%H:%M:%S%z"
    history_endpoint = "history/period"
    
    if start_time and is_valid_datetime(start_time, time_format):
        history_endpoint = f"{history_endpoint}/{start_time}"

    params = {
        "filter_entity_id": entity_id,
        "minimal_response": "",
        "significant_changes_only": ""
    }

    if end_time and is_valid_datetime(end_time, time_format):
        params["end_time"] = end_time

    try:
        client = HAClient(HA_URL, TOKEN)
        response = client.get(history_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        if not data or not isinstance(data, list):
            return []

        raw_records = data[0]
        attrs = raw_records[0].get('attributes', {})

        is_numeric = (
            attrs.get('state_class') == 'measurement' or 
            attrs.get('unit_of_measurement') is not None
        )
        SchemaCls = schemas.HistoryNumericState if is_numeric else schemas.HistoryCategoricalState
        
        return [
            SchemaCls(**(record | attrs)) 
            for record in raw_records[-limit:]
        ]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching history for {entity_id}: {e}")
        return None