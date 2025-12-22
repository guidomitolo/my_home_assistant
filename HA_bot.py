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
def get_states(condition: Optional[str] = None) -> Union[List[Dict[str, Any]], str]:
    """
    Retrieves the status of entities, optionally filtered by state (e.g., 'on' or 'off').
    
    Use this for global queries like 'Which lights are currently on?' or 
    'Show me everything that is off'.
    """
    try:
        return api.get_states(condition) or "No entities match that condition."
    except Exception as e:
        return f"Error fetching states: {e}"

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

if __name__ == "__main__":
    mcp.run()