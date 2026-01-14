import requests
import time
import ha_mcp_bot.schemas as schemas
import logging
from typing import Optional
from .api import HomeAssistantAPI


logger = logging.getLogger(__name__)


class ActionService:
    """Domain-level action methods that use a HomeAssistantAPI instance."""

    def __init__(self, api: HomeAssistantAPI):
        self.api = api

    def trigger_service(self, entity_id: str, command: schemas.SwitchCommand) -> Optional[schemas.State]:
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

        if not isinstance(command, schemas.SwitchCommand):
            logger.exception(f"Invalid command type. Expected SwitchCommand, got {type(command)}")
            return None

        try:
            domain = entity_id.split('.')[0]
        except (ValueError, AttributeError):
            logger.exception(f"Invalid entity_id format: {entity_id}")
            return None

        service_action = f"turn_{command.value}" if command != schemas.SwitchCommand.TOGGLE else "toggle"
        service_endpoint = f"services/{domain}/{service_action}"

        try:
            response = self.api.post(service_endpoint, json_data={"entity_id": entity_id})
            response.raise_for_status()

            if domain in ['switch', 'light', 'fan', 'remote']:
                time.sleep(1)
                try:
                    response = self.api.get(f"states/{entity_id}")
                    response.raise_for_status()
                    data = response.json()
                    return schemas.State(**data)
                except Exception as e:
                    logger.exception(f"Error after updated state retrieval: {e}")

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.exception(f"Connection Error: {e}")
            return None