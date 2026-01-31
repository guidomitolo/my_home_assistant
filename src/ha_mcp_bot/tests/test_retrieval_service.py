import pytest
from unittest.mock import AsyncMock
from ha_mcp_bot.api import HomeAssistantAPI, RetrievalService
from ha_mcp_bot import schemas


@pytest.fixture
def mock_api():
    api = AsyncMock(spec=HomeAssistantAPI)
    return api


@pytest.mark.asyncio
async def test_get_labels_success(mock_api):
    """Test that valid JSON data is correctly parsed into Label schemas."""
    
    fake_ha_response = [
        {"label_id": "light", "label_name": "Light", "label_description": "Light related entity" },
        {"label_id": "consumption", "label_name": "Consumption", "label_description": "Energy and power meter"}
    ]
    mock_api.get_HA_template_data.return_value = fake_ha_response # mock to retun when api method called
    service = RetrievalService(api=mock_api)
    labels = await service.get_labels()

    assert len(labels) == 2
    assert isinstance(labels[0], schemas.Label)
    assert labels[0].id == "light" 
    assert labels[1].name == "Consumption"


@pytest.mark.asyncio
async def test_get_labels_partial_failure(mock_api):
    """Test that one bad record doesn't crash the whole retrieval."""
    
    fake_ha_response = [
        {"label_id": "outlet", "label_name": "Outlet", "label_description": "Power socket" },
        {"label_id_field": "missing_id", "label_name_field": "Invalid"}
    ]
    
    mock_api.get_HA_template_data.return_value = fake_ha_response
    service = RetrievalService(api=mock_api)
    labels = await service.get_labels()
    assert len(labels) == 1
    assert labels[0].id == "outlet"