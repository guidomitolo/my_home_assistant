import logging
import ha_mcp_bot.schemas as schemas
from typing import List, Union
from ha_mcp_bot.api import RetrievalService

logger = logging.getLogger(__name__)

_retrieval = RetrievalService()



async def get_all_entities_state() -> Union[List[schemas.State], List[schemas.StateCore], str]:
    """
    Snapshots the current real-time state and attributes of every entity in the house.
    
    Use this for global status checks like 'Is anything on?' or 'Is the house secure?'
    or when you cannot find a device in a specific area. 
    
    WARNING: In large installations, this returns a high volume of data. Use 
    get_states_by_condition if you only need entities in a specific state (e.g., 'on').
    """
    try:
        states = await _retrieval.get_states(cheaper=True) 
        if not states:
            return "No entities found or unable to communicate with Home Assistant."
        return states
    except Exception as e:
        return f"Error fetching states: {e}"


async def get_entity_information(entity_id: str) -> Union[schemas.Entity, str]:
    """
    Retrieves detailed metadata for a specific entity, including hardware info.
    
    Use this when you need background info on an entity, such as:
    - 'Who manufactured this light?'
    - 'What device is this sensor part of?'
    - 'What labels are assigned to this switch?'

    Args:
        entity_id: The full ID of the entity (e.g., 'light.kitchen_main').
    """
    try:
        return await _retrieval.get_entity_info(entity_id) or f"Entity {entity_id} not found."
    except Exception as e:
        return f"Error fetching entity info: {e}"


async def get_device_entities(device_id: str) -> Union[List[schemas.Entity], str]:
    """
    Lists all individual sensors and controls (entities) belonging to one physical device.
    
    Use this when a user asks about a specific piece of hardware:
    - 'What sensors does the Shelly Plug have?'
    - 'Show me all the controls for the multi-sensor in the hallway.'

    Args:
        device_id: The unique hardware device ID.
    """
    try:
        return await _retrieval.get_device_entities(device_id) or f"No entities found for device {device_id}."
    except Exception as e:
        return f"Error fetching device entities: {e}"
    

async def get_entity_state(entity_id: str) -> Union[schemas.State, str]:
    """
    Gets the current live state and detailed attributes for a single specific entity.

    Use this for high-precision checks on one entity:
    - 'What is the current brightness of the kitchen light?'
    - 'What is the exact battery level of the thermostat?'
    
    Args:
        entity_id: The full ID of the entity (e.g., 'sensor.bedroom_humidity').
    """
    try:
        result = await _retrieval.get_entity_state(entity_id)
        return result or f"Could not find state for {entity_id}."
    except Exception as e:
        return f"Error fetching state: {e}"

