import json
import logging
import requests
from typing import Any, Dict, Optional
from .client import HAClient
from .config import HA_URL, HA_TOKEN


logger = logging.getLogger(__name__)


class HomeAssistantAPI:
    """Thin wrapper owning an HAClient/session and exposing low-level HA operations."""

    def __init__(self, client: Optional[HAClient] = None):
        self._client = client or HAClient(HA_URL, HA_TOKEN)

    def post(self, endpoint: str, json_data: Optional[dict] = None, timeout: int = 10) -> requests.Response:
        return self._client.post(endpoint, json_data, timeout=timeout)

    def get(self, endpoint: str, params: Optional[dict] = None, timeout: int = 10) -> requests.Response:
        return self._client.get(endpoint, params=params, timeout=timeout)

    def get_HA_template_data(self, payload: Dict[str, Any]) -> Any:
        """
        Executes a Jinja2 template on the Home Assistant server and returns the processed result.
        Useful for complex data extraction that standard REST endpoints don't support directly.

        Args:
            payload: A dictionary containing a 'template' key with the Jinja2 code.

        Returns:
            The processed data, automatically parsed from JSON if possible. 
            Returns None if the communication with Home Assistant fails.
        """
        try:
            response = self._client.post("template", payload)
            response.raise_for_status()
            result_data = response.json()
            
            if isinstance(result_data, str):
                try:
                    return json.loads(result_data)
                except json.JSONDecodeError:
                    return result_data
            return result_data

        except requests.exceptions.RequestException as e:
            logger.exception(f"Connection Error: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return None

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            logger.exception("Error closing HA client")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

### Global API settings

_default_api: Optional[HomeAssistantAPI] = None

def get_default_api() -> HomeAssistantAPI:
    global _default_api
    if _default_api is None:
        _default_api = HomeAssistantAPI()
    return _default_api

def set_default_api(api: HomeAssistantAPI):
    global _default_api
    _default_api = api