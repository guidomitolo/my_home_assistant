import asyncio 
import ha_mcp_bot.schemas as schemas
import logging
from typing import Optional
from .custom_api import HomeAssistantAPI, get_default_api

logger = logging.getLogger(__name__)


class ActionService:
    """Domain-level action methods that use a HomeAssistantAPI instance."""

    def __init__(self, api: Optional[HomeAssistantAPI] = None):
        self.api = api or get_default_api()

    async def trigger_service(self, entity_id: str, command: schemas.SwitchCommand) -> Optional[schemas.State]:
        if not isinstance(command, schemas.SwitchCommand):
            logger.error(f"Invalid command type: {type(command)}")
            return None

        try:
            domain = entity_id.split('.')[0]
        except (ValueError, AttributeError, IndexError):
            logger.error(f"Invalid entity_id format: {entity_id}")
            return None

        service_action = "toggle" if command == schemas.SwitchCommand.TOGGLE else f"turn_{command.value}"
        service_endpoint = f"services/{domain}/{service_action}"

        try:
            await self.api.post(service_endpoint, json_data={"entity_id": entity_id})
            await asyncio.sleep(1) 
            response = await self.api.get(f"states/{entity_id}")
            data = response.json()
            logger.info(f"Successfully executed {service_action} on {entity_id}")
            return schemas.State(**data)

        except Exception as e:
            logger.exception(f"Unexpected error in trigger_service: {e}")
            return None