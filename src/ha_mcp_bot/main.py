import logging
import ha_mcp_bot.helpers as helpers
import ha_mcp_bot.schemas as schemas
import ha_mcp_bot.api.config as config
from mcp.server.fastmcp import FastMCP
from typing import List, Union, Optional
from ha_mcp_bot.api import HomeAssistantAPI,  RetrievalService, ActionService

logger = logging.getLogger(__name__)


_default_api = HomeAssistantAPI()
_default_retrieval = RetrievalService(_default_api)
_default_action = ActionService(_default_api)

mcp = FastMCP("HomeAssistantBot")


@mcp.tool()
def get_areas() -> Union[List[schemas.Area], str]:
    """
    Lists all physical areas (rooms or zones) defined in the Home Assistant instance.
    
    Use this as the primary discovery tool to understand the house layout before 
    querying specific devices. It helps map natural language names (like 'Living Room') 
    to valid area_ids.

    Returns:
        A list of Area objects containing 'id' and 'name'.
        Example: [Area(id='exterior', name='Exterior'), Area(id='hall', name='Hall')]
    """
    try:
        return _default_retrieval.get_areas()
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_area_devices(area_name: str) -> Union[List[schemas.Device], str]:
    """
    Lists all hardware devices and their current entity states within a specific room/area.

    Use this to answer questions about the status of a specific room, such as:
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
        return _default_retrieval.get_area_devices(area_name) or f"No devices found in {area_name}."
    except Exception as e:
        return f"Error querying area {area_name}: {e}"

@mcp.tool()
def get_all_entity_states() -> Union[List[schemas.State], str]:
    """
    Snapshots the current real-time state and attributes of every entity in the house.
    
    Use this for global status checks like 'Is anything on?' or 'Is the house secure?'
    or when you cannot find a device in a specific area. 
    
    WARNING: In large installations, this returns a high volume of data. Use 
    get_states_by_condition if you only need entities in a specific state (e.g., 'on').
    """
    try:
        states = _default_retrieval.get_states(cheaper=True) 
        if not states:
            return "No entities found or unable to communicate with Home Assistant."
        return states
    except Exception as e:
        return f"Error fetching states: {e}"
    
@mcp.tool()
def get_states_by_condition(condition: str) -> Union[List[schemas.StateCore], str]:
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
        results = _default_retrieval.get_states_by_condition(condition)
        if not results:
            return f"No entities are currently in the '{condition}' state."
        return results
    except Exception as e:
        return f"Error filtering states by condition: {e}"
    
@mcp.tool()
def get_entity_state_history(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
) -> Union[List[schemas.HistoryState], str]:
    """
    Retrieves the raw chronological history of state changes for a specific entity. 
    
    Use this to find:
    - 'When was the front door last opened?'
    - 'Show me the temperature logs for the last 4 hours.'
    - 'How has the power usage changed since this morning?'
    
    Args:
        entity_id: The full ID of the entity (e.g., 'sensor.living_room_temp').
        start_time: ISO 8601 UTC timestamp (e.g., '2026-01-10T10:00:00Z'). 
                    If omitted, the tool retrieves data for the last 24 hours.
        end_time: ISO 8601 UTC timestamp. If omitted, defaults to the current time.
    """
    try:
        result = _default_retrieval.get_history(entity_id, start_time, end_time)
        if not result:
            return f"No history records found for {entity_id} in that range."
        return result
    except Exception as e:
        return f"Error fetching history: {e}"


@mcp.tool()
def analyze_entity_trends(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
) -> dict:
    """
    Calculates statistical trends and state changes for a Home Assistant entity over time.
    Use this tool when a user asks for summaries, averages, or how long a device was in a certain state.

    Args:
        entity_id: The full Home Assistant entity ID (e.g., 'sensor.temperature' or 'binary_sensor.door').
        start_time: Start period in ISO 8601 format (e.g., '2026-01-10T00:00:00Z'). 
                    If omitted, defaults to the start of the current history buffer.
        end_time: End period in ISO 8601 format (e.g., '2026-01-10T23:59:59Z').
                  If omitted, defaults to the current time.

    Capabilities:
        - For Numeric Sensors (Measurement): Returns average, maximum, and minimum values.
        - For Categorical Sensors (Labels): Returns most common state, total change count, 
          frequency distribution, and duration (time spent) in each state.

    Returns:
        A string containing a formatted summary of the statistical analysis.
    """
    history = _default_retrieval.get_history(entity_id, start_time, end_time, limit=100)
    if not history:
        return f"Could not find enough data to analyze {entity_id}."
    stats = helpers.get_history_analytics(history)
    return stats


@mcp.tool()
def get_entity_information(entity_id: str) -> Union[schemas.Entity, str]:
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
        return _default_retrieval.get_entity_info(entity_id) or f"Entity {entity_id} not found."
    except Exception as e:
        return f"Error fetching entity info: {e}"

@mcp.tool()
def get_labels() -> Union[List[schemas.Label], str]:
    """
    Lists all user-defined labels (categories) used to group entities across rooms.
    
    Labels are useful for organizational queries like 'Security', 'Energy', or 'Entertainment'.
    Use this to understand available groupings before calling get_label_devices.
    """
    try:
        return _default_retrieval.get_labels() or []
    except Exception as e:
        return f"Error fetching labels: {e}"

@mcp.tool()
def get_label_devices(label_name: str) -> Union[List[schemas.Device], str]:
    """
    Retrieves all hardware devices associated with a specific label, regardless of location.
    
    Use this for category-wide questions like:
    - 'Show me all devices in the Security group.'
    - 'What entertainment devices do we have?'
    
    Args:
        label_name: The name or ID of the label (e.g., 'Security').
    """
    try:
        return _default_retrieval.get_label_devices(label_name) or f"No devices found with label: {label_name}"
    except Exception as e:
        return f"Error querying label {label_name}: {e}"

@mcp.tool()
def get_device_entities(device_id: str) -> Union[List[schemas.Entity], str]:
    """
    Lists all individual sensors and controls (entities) belonging to one physical device.
    
    Use this when a user asks about a specific piece of hardware:
    - 'What sensors does the Shelly Plug have?'
    - 'Show me all the controls for the multi-sensor in the hallway.'

    Args:
        device_id: The unique hardware device ID.
    """
    try:
        return _default_retrieval.get_device_entities(device_id) or f"No entities found for device {device_id}."
    except Exception as e:
        return f"Error fetching device entities: {e}"
    
@mcp.tool()
def get_entity_state(entity_id: str) -> Union[schemas.State, str]:
    """
    Gets the current live state and detailed attributes for a single specific entity.

    Use this for high-precision checks on one entity:
    - 'What is the current brightness of the kitchen light?'
    - 'What is the exact battery level of the thermostat?'
    
    Args:
        entity_id: The full ID of the entity (e.g., 'sensor.bedroom_humidity').
    """
    try:
        result = _default_retrieval.get_entity_state(entity_id)
        return result or f"Could not find state for {entity_id}."
    except Exception as e:
        return f"Error fetching state: {e}"

@mcp.tool()
def trigger_service(entity_id: str, command: str) -> Union[schemas.State, str]:
    """
    Performs an action (on/off) on a controllable device.
    
    Supported for lights, switches, fans, and other binary toggles.
    
    Args:
        entity_id: The ID of the device to control (e.g., 'light.living_room').
        command: Action to perform. Must be strictly 'on' or 'off'.
    """
    cmd_map = {"on": schemas.SwitchCommand.ON, "off": schemas.SwitchCommand.OFF}
    action = cmd_map.get(command.lower())
    if not action:
        return "Error: Command must be 'on' or 'off'."
        
    try:
        result = _default_action.trigger_service(entity_id, action)
        return result or f"Command '{command}' sent to {entity_id}."
    except Exception as e:
        return f"Error triggering service: {e}"
    
@mcp.tool()
def search_entities(description: str, area: Optional[str] = None, label: Optional[str] = None) -> str:
    """
    Search for Home Assistant entities using natural language descriptions.
    
    Use this tool when the user's request is vague or you don't know the exact entity_id.
    - 'Find the fan in the office' -> description='fan', area='office'
    - 'Search for security sensors' -> description='sensor', label='Security'

    Args:
        description: Natural language search term (e.g., "desk lamp").
        area: (Optional) The room or location to narrow results.
        label: (Optional) The category or type of entity to filter by.
    
    Returns:
        A list of matching entity IDs and friendly names.
    """
    area_entities = label_entities = []
    if area:
        area_entities = _default_retrieval.get_area_entities(area)
    if label:
        label_entities = _default_retrieval.get_label_entities(label)

    entities = label_entities + area_entities

    if not entities:
        entities = _default_retrieval.get_all_entities()

    if not entities:
        return "Failed to retrieve entities from Home Assistant."

    matches = helpers.search_entities_by_keywords(entities, description)
    return helpers.format_entity_results(matches)



if __name__ == "__main__":
    mcp.run()