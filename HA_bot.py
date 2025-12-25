from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union, Any, Optional
import HA_rest_api as api

mcp = FastMCP("HomeAssistantBot")

@mcp.tool()
def get_areas() -> List[str]:
    """
    Lists all physical areas/rooms defined in Home Assistant.
    
    Use this as a starting point to browse the house layout.
    Example: ['Living Room', 'Kitchen', 'Master Bedroom']
    """
    try:
        return api.get_areas() or []
    except Exception as e:
        return [f"Error: {e}"]

@mcp.tool()
def get_area_devices(area_name: str) -> Union[List[Dict[str, Any]], str]:
    """
    Lists all devices and their current states within a specific area.
    
    Use this when the user asks: 'What's going on in the Living Room?' or 
    'Are the lights on in the kitchen?'.
    """
    try:
        return api.get_area_devices(area_name) or f"No devices found in {area_name}."
    except Exception as e:
        return f"Error querying area {area_name}: {e}"

@mcp.tool()
def get_all_entity_states() -> Union[List[Dict[str, Any]], str]:
    """
    Retrieves the current state and attributes of all entities in Home Assistant.
    
    Use this tool when the user asks for a general overview of the house, 
    needs to find available entities, or wants to know the status of multiple 
    different types of devices at once.
    
    Returns:
        A list of state objects containing entity_id, state, and attributes.
    """
    try:
        states = api.get_states()
        if not states:
            return "No entities found or unable to communicate with Home Assistant."
        return states
    except Exception as e:
        return f"Error fetching states: {e}"
    
@mcp.tool()
def get_states_by_condition(condition: str) -> Union[List[Dict[str, Any]], str]:
    """
    Filters all entities by a specific state (e.g., 'on', 'off', 'unavailable').
    
    Use this for targeted global queries such as "Which lights are on?", 
    "Are any windows open?", or "Show me all disconnected devices."
    
    Args:
        condition: The state value to filter by (e.g., 'on', 'off', 'home', 'not_home').
    """
    try:
        # Note: Ensure api.get_states_by_condition is implemented to handle the logic
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
) -> Union[List[Dict[str, Any]], str]:
    """
    Retrieves the historical state changes for a specific entity over time.
    
    Use this tool to answer questions about trends, such as "How has the 
    temperature changed today?", "When was the front door last opened?", 
    or "How long was the AC running yesterday?"
    
    Args:
        entity_id: The full Home Assistant entity ID (e.g., 'sensor.living_room_temp').
        start_time: Optional. Start point in ISO 8601 format (YYYY-MM-DDThh:mm:ssZ). 
                    Defaults to 24 hours ago if not provided.
        end_time: Optional. End point in ISO 8601 format (YYYY-MM-DDThh:mm:ssZ).
    """
    try:
        result = api.get_history(entity_id, start_time or '', end_time or '')
        if not result:
            return f"No history records found for {entity_id} in the specified time range."
        return result
    except Exception as e:
        return f"Error fetching history for {entity_id}: {e}"

@mcp.tool()
def get_entity_info(entity_id: str) -> Union[Dict[str, Any], str]:
    """
    Gets detailed metadata and attributes for one specific entity.
    
    Use this when you have an entity_id (like 'light.bulb_1') and need to know 
    its brightness, manufacturer, or precise last changed timestamp.
    """
    try:
        return api.get_entity_info(entity_id) or f"Entity {entity_id} not found."
    except Exception as e:
        return f"Error fetching entity info: {e}"

@mcp.tool()
def get_labels() -> List[str]:
    """
    Lists all labels/tags used to categorize devices across the house.
    
    Labels are cross-area categories like 'Security', 'Lights', or 'Power Consumption'.
    """
    try:
        return api.get_labels() or []
    except Exception as e:
        return [f"Error fetching labels: {e}"]

@mcp.tool()
def get_label_devices(label_name: str) -> Union[List[Dict[str, Any]], str]:
    """
    Retrieves all devices associated with a specific label, regardless of their area.
    
    Use this for functional queries like 'Show me all energy consumption sensors' 
    if the 'consumption' label exists.
    """
    try:
        # Note: Corrected to label_name based on our previous API improvement
        return api.get_label_devices(label_name) or f"No devices found with label: {label_name}"
    except Exception as e:
        return f"Error querying label {label_name}: {e}"

@mcp.tool()
def get_device_entities(device_id: str) -> Union[List[Dict[str, str]], str]:
    """
    Lists all individual sensors or controls (entities) belonging to a specific hardware device.
    
    Use this when a user asks about a specific piece of hardware, e.g., 'What sensors 
    does the Shelly Plug in the wall have?'.
    """
    try:
        return api.get_device_entities(device_id) or f"No entities found for device {device_id}."
    except Exception as e:
        return f"Error fetching device entities: {e}"

@mcp.tool()
def get_entity_state(entity_id: str) -> Union[Dict[str, Any], str]:
    """
    Retrieves the current state and all attributes of a specific entity.
    
    Use this to get a "snapshot" of a single item, such as the current temperature 
    of a climate entity, the brightness of a light, or whether a motion sensor 
    is currently detecting anything.
    
    Args:
        entity_id: The full ID of the entity (e.g., 'light.living_room' or 'sensor.temperature').
    """
    try:
        result = api.get_entity_state(entity_id)
        return result or f"Could not find state for {entity_id}."
    except Exception as e:
        return f"Error fetching state: {e}"
    
@mcp.tool()
def get_entity_state_history(entity_id: str, start_time: str = '', end_time: str = '') -> Optional[List[Dict[str, Any]]]:
    """
    Retrieves the entity attributes and their history of a specific entity.
    
    Use this to get a the changes of the state of a entity over a time period, such as the temperature
    or if it was turned on or off.
    
    Args:
        entity_id: The full ID of the entity (e.g., 'light.living_room' or 'sensor.temperature').
        start_time: The start time for the history query in pattern YYYY-MM-DDThh:mm:ssZ.
        end_time: The end time for the history query in patter YYYY-MM-DDThh:mm:ssZ.
    """
    try:
        result = api.get_history(entity_id, start_time, end_time)
        return result or f"Could not find the history for {entity_id}."
    except Exception as e:
        return f"Error fetching state: {e}"

@mcp.tool()
def trigger_service(entity_id: str, command: str) -> Union[Dict[str, Any], str]:
    """
    Controls a device by sending 'on' or 'off' commands.
    
    Use this tool when the user gives a direct command like 'Turn on the kitchen light' 
    or 'Switch off the heater'. 
    
    Args:
        entity_id: The full ID of the entity to control (e.g., 'switch.outlet_1').
        command: The action to perform. Must be either 'on' or 'off'.
    
    Returns:
        The new state of the entity after the command has been processed.
    """
    if command.lower() not in ['on', 'off']:
        return "Error: Command must be 'on' or 'off'."
        
    try:
        result = api.trigger_service(entity_id, command.lower())
        if result:
            return result
        return f"Command '{command}' sent to {entity_id}, but no confirmation was received."
    except Exception as e:
        return f"Error triggering service: {e}"


if __name__ == "__main__":
    mcp.run()