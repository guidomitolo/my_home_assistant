import logging
import ha_mcp_bot.schemas as schemas
from typing import List, Union
from ha_mcp_bot.api import RetrievalService

logger = logging.getLogger(__name__)

_retrieval = RetrievalService()


async def get_areas() -> Union[List[schemas.Area], str]:
    """
    Lists all physical areas (rooms or zones) defined in the Home Assistant instance.
    
    Use this to understand the house layout. It helps map natural language names
    (like 'Living Room') to valid area_ids. Do not use it for retrieve area devices.

    Returns:
        A list of Area objects containing 'id' and 'name'.
        Example: [Area(id='exterior', name='Exterior'), Area(id='hall', name='Hall')]
    """
    try:
        return await _retrieval.get_areas()
    except Exception as e:
        return f"Error querying areas: {e}"


async def get_area_devices(area_name: str) -> Union[List[schemas.Device], str]:
    """
    Lists all hardware devices and their current entity states within a specific room/area.

    Use as a primary discovery tool for finding the devices and their corresponding entities
    within a specific area or room. Answer questions about the status of a particular area devices or
    entities, such as:
    - 'What's going on in the Living Room?'
    - 'Are any lights on in the kitchen?'
    - 'What devices are in the office?'
    
    Args:
        area_name: The exact name or ID of the area (e.g., 'kitchen', 'living_room'). 
                  Always call get_areas first to verify the correct name.
    
    Returns:
        A list of Device objects including their current states and attributes.
    """
    try:
        return await _retrieval.get_area_devices(area_name) or f"No devices found in {area_name}."
    except Exception as e:
        return f"Error querying area {area_name} devices: {e}"
    

async def get_labels() -> Union[List[schemas.Label], str]:
    """
    Lists all user-defined labels (categories) used to group entities across rooms.
    
    Labels are useful for organizational queries like 'Security', 'Energy', or 'Entertainment'.
    Use this to understand available groupings before calling get_label_devices.
    """
    try:
        return await _retrieval.get_labels() or []
    except Exception as e:
        return f"Error fetching labels: {e}"


async def get_label_devices(label_name: str) -> Union[List[schemas.Device], str]:
    """
    Retrieves all hardware devices associated with a specific label, regardless of location.
    
    Use this for category-wide questions like:
    - 'Show me all devices in the Security group.'
    - 'What entertainment devices do we have?'
    
    Args:
        label_name: The name or ID of the label (e.g., 'Security').
    """
    try:
        return await _retrieval.get_label_devices(label_name) or f"No devices found with label: {label_name}"
    except Exception as e:
        return f"Error querying label {label_name}: {e}"
    

async def get_states_by_condition(condition: str) -> Union[List[schemas.StateCore], str]:
    """
    Filters all entities in the house that match a specific state value.
    
    Use this for cross-house boolean or status questions: 
    - 'Which lights are currently on?' -> condition='on'
    - 'Are any windows open?' -> condition='open'
    - 'Which sensors are unavailable?' -> condition='unavailable'
    
    Args:
        condition: The state value to filter for. Common values: 'on', 'off', 
                  'home', 'not_home', 'open', 'closed', 'locked', 'unlocked'.
    """
    try:
        return await _retrieval.get_states_by_condition(condition) or f"No entities are currently in the '{condition}' state."
    except Exception as e:
        return f"Error filtering states by condition: {e}"
    