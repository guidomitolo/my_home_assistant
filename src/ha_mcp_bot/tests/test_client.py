import pytest
import json
import httpx
from unittest.mock import AsyncMock
from ha_mcp_bot.api import HomeAssistantAPI, HAClient


@pytest.fixture
def mock_client():
    return AsyncMock(spec=HAClient)


@pytest.mark.asyncio
async def test_api_template_parses_stringified_json(mock_client):
    """
    The API class handling returned JSON from template response
    """
    inner_data = [{"id": "light.living_room", "state": "on"}]
    stringified_body = json.dumps(inner_data)
    
    mock_response = httpx.Response(200, json=stringified_body)
    mock_client.post.return_value = mock_response
    api = HomeAssistantAPI(client=mock_client)

    result = await api.get_HA_template_data(payload={"...": "..."})

    assert isinstance(result, list)
    assert result[0]['id'] == "light.living_room"

@pytest.mark.asyncio
async def test_api_handles_httpx_error(mock_client):
    """Connection errors caught and logged."""
    mock_client.post.side_effect = httpx.RequestError("Connection failed")
    api = HomeAssistantAPI(client=mock_client)
    result = await api.get_HA_template_data(payload={})
    assert result is None