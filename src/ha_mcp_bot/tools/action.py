import logging
import ha_mcp_bot.schemas as schemas
from typing import Union
from ha_mcp_bot.api import ActionService

logger = logging.getLogger(__name__)

_action = ActionService()


async def trigger_service(entity_id: str, command: str) -> Union[schemas.State, str]:
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
        result = await _action.trigger_service(entity_id, action)
        return result or f"Command '{command}' sent to {entity_id}."
    except Exception as e:
        return f"Error triggering service: {e}"
    

