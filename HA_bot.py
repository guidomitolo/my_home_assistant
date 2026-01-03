from mcp.server.fastmcp import FastMCP
from typing import List, Union, Optional
import custom_api as api
import schemas as schemas
from schemas.base import SwitchCommand

mcp = FastMCP("HomeAssistantBot")

@mcp.tool()
def get_areas() -> List[str]:
    """
    Lists all physical areas (rooms/zones) defined in Home Assistant.
    
    Use this as the primary discovery tool to understand the house layout 
    before querying specific devices.
    Example: ['Living Room', 'Kitchen', 'Master Bedroom']
    """
    try:
        return api.get_areas() or []
    except Exception as e:
        return [f"Error: {e}"]

@mcp.tool()
def get_area_devices(area_name: str) -> Union[List[schemas.Device], str]:
    """
    Lists all devices and their entity states within a specific room/area.

    Use this when the user asks: 'What's going on in the Living Room?' or 
    'Are the lights on in the kitchen?'.
    
    Args:
        area_name: The name of the area (e.g., 'kitchen', 'living_room'). 
                  Use get_areas first to see valid names.
    """
    try:
        return api.get_area_devices(area_name) or f"No devices found in {area_name}."
    except Exception as e:
        return f"Error querying area {area_name}: {e}"

@mcp.tool()
def get_all_entity_states() -> Union[List[schemas.State], str]:
    """
    Snapshots the current state and attributes of every entity in the house.
    
    Use this for global status checks like "Is anything on?" or when 
    the location of a device is unknown. Note: This may return a large 
    amount of data.
    """
    try:
        states = api.get_states(cheaper=True) 
        if not states:
            return "No entities found or unable to communicate with Home Assistant."
        return states
    except Exception as e:
        return f"Error fetching states: {e}"
    
@mcp.tool()
def get_states_by_condition(condition: str) -> Union[List[schemas.StateCore], str]:
    """
    Finds all entities matching a specific state (e.g., 'on', 'off', 'unavailable').
    
    Use this for specific cross-house questions: 
    - "Which lights are on?" -> condition='on'
    - "Are any windows open?" -> condition='open'
    Args:
        condition: The state value to filter by (e.g., 'on', 'off', 'home', 'not_home').    
    """
    try:
        results = api.get_states_by_condition(condition)
        if not results:
            return f"No entities are currently in the '{condition}' state."
        return results
    except Exception as e:
        return f"Error filtering states by condition: {e}"
    
@mcp.tool()
def get_entity_state_history(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None
) -> Union[List[schemas.HistoryState], str]:
    """
    Retrieves history for an entity. Use this for questions about 
    trends, duration, or 'last time' something happened.
    
    Args:
        entity_id: The entity ID (e.g., 'sensor.temperature').
        start_time: ISO 8601 string (e.g., '2023-10-27T10:00:00Z'). 
                    If omitted, defaults to the last 24 hours.
        end_time: ISO 8601 string.
    """
    try:
        result = api.get_history(entity_id, start_time, end_time)
        if not result:
            return f"No history records found for {entity_id} in that range."
        return result
    except Exception as e:
        return f"Error fetching history: {e}"
    
@mcp.tool()
def get_entity_information(entity_id: str) -> Union[schemas.Entity, str]:
    """
    Gets detailed metadata, data and attributes for a unique and given/provided specific entity.
    
    Use this when you have an entity_id (like 'light.bulb_1') and need to know any related
    information, like manufacturer, area, associated device or associated labels. Can also retrieve
    state data (but for this it is better to use get_entity_state tool)

    Args:
        entity_id: The full ID of the entity (e.g., 'light.living_room' or 'sensor.temperature').
    """
    try:
        return api.get_entity_info(entity_id) or f"Entity {entity_id} not found."
    except Exception as e:
        return f"Error fetching entity info: {e}"

@mcp.tool()
def get_labels() -> List[str]:
    """
    Lists categories (labels) like 'Security', 'Lights', or 'Critical'.
    Labels group devices or entities across different rooms or areas.
    """
    try:
        return api.get_labels() or []
    except Exception as e:
        return [f"Error fetching labels: {e}"]

@mcp.tool()
def get_label_devices(label_name: str) -> Union[List[schemas.Device], str]:
    """
    Retrieves all devices tagged with a specific label, regardless of their area.
    Example: 'Show me all devices in the Security category.'
    """
    try:
        return api.get_label_devices(label_name) or f"No devices found with label: {label_name}"
    except Exception as e:
        return f"Error querying label {label_name}: {e}"

@mcp.tool()
def get_device_entities(device_id: str) -> Union[List[schemas.Entity], str]:
    """
    Lists all individual sensors or controls (entities) belonging to a specific hardware device.
    
    Use this when a user asks about a specific piece of hardware, e.g., 'What sensors 
    does the Shelly Plug in the wall have?'.

    Args:
        device_id: The full ID of the device (e.g., 'e5e97c06bff524b0017449d402417ec3').
    
    """
    try:
        return api.get_device_entities(device_id) or f"No entities found for device {device_id}."
    except Exception as e:
        return f"Error fetching device entities: {e}"
    
@mcp.tool()
def get_entity_state(entity_id: str) -> Union[schemas.State, str]:
    """
    Gets the live state and detailed attributes of a single entity.

    Use this to check a specific state of a given entity, like a sensor's value or a light's brightness.
    
    Args:
        entity_id: The full ID of the entity (e.g., 'light.living_room' or 'sensor.temperature').
    """
    try:
        result = api.get_entity_state(entity_id)
        return result or f"Could not find state for {entity_id}."
    except Exception as e:
        return f"Error fetching state: {e}"

@mcp.tool()
def trigger_service(entity_id: str, command: str) -> Union[schemas.State, str]:
    """
    Turns a device on or off. 
    Supported for switches, lights, fans, and other binary controls.
    
    Args:
        entity_id: The ID of the device (e.g., 'light.living_room').
        command: Action to perform: 'on' or 'off'.
    """
    # Map string input to the Enum required by your trigger_service API
    cmd_map = {
        "on": SwitchCommand.ON,
        "off": SwitchCommand.OFF
    }
    
    action = cmd_map.get(command.lower())
    if not action:
        return "Error: Command must be 'on' or 'off'."
        
    try:
        result = api.trigger_service(entity_id, action)
        if result:
            return result
        return f"Command '{command}' sent to {entity_id}."
    except Exception as e:
        return f"Error triggering service: {e}"
    

def search_entities(description: str) -> str:
    """Search for Home Assistant entities matching a natural language description.
    
    Args:
        description: Natural language description of the entity (e.g., "office light", "kitchen fan")
    
    Returns:
        A list of matching entity IDs with their friendly names, or an error message
    """
    
    # Get all entities
    entities = api.get_all_entities()
    if not entities:
        return "Failed to retrieve entities from Home Assistant."
    
    # Search and format results
    matches = api.search_entities_by_keywords(entities, description)
    return api.format_entity_results(matches)


if __name__ == "__main__":
    mcp.run()