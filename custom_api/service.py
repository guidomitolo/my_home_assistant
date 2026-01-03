import requests
import time
import schemas.state as schemas
from schemas import SwitchCommand
from custom_api.session import HAClient
from typing import Optional
from .base import HA_URL, TOKEN
from .retrieval import get_entity_state


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

        if domain in ['switch', 'light', 'fan', 'remote']:
            time.sleep(1)
            return get_entity_state(entity_id)

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None