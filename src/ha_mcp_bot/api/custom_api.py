import json
import logging
import httpx
from typing import Any, Dict, Optional
from ha_mcp_bot.config import config
from .base import BaseClient
from .client import HAClient

logger = logging.getLogger(__name__)



class HomeAssistantAPI:

    def __init__(self, client: Optional[BaseClient] = None):
        self._client = client or HAClient(config.HA_URL, config.HA_TOKEN)

    async def post(self, endpoint: str, json_data: Optional[dict] = None) -> httpx.Response:
        return await self._client.post(endpoint, json_data)

    async def get(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        return await self._client.get(endpoint, params=params)

    async def get_HA_template_data(self, payload: Dict[str, Any]) -> Any:
        try:
            response = await self._client.post("template", payload)
            result_data = response.json()
            
            if isinstance(result_data, str):
                try:
                    return json.loads(result_data)
                except json.JSONDecodeError:
                    return result_data
            return result_data

        except httpx.RequestError as e: # Updated exception type
            logger.exception(f"Connection Error: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return None

    async def close(self) -> None:
        try:
            await self._client.close()
        except Exception:
            logger.exception("Error closing HA client")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


_DEFAULT_API_INSTANCE: Optional['HomeAssistantAPI'] = None

def get_default_api() -> HomeAssistantAPI:
    """Global access to the API wrapper."""
    global _DEFAULT_API_INSTANCE
    if _DEFAULT_API_INSTANCE is None:
        _DEFAULT_API_INSTANCE = HomeAssistantAPI()
    return _DEFAULT_API_INSTANCE