import logging
import ha_mcp_bot.helpers as helpers
import ha_mcp_bot.schemas as schemas
from typing import List, Union, Optional
from ha_mcp_bot.api import RetrievalService

logger = logging.getLogger(__name__)

_retrieval = RetrievalService()


    
async def search_entities(description: str, area: Optional[str] = None, label: Optional[str] = None) -> Union[List[schemas.SearchEntity], str]:
    """
    Search for Home Assistant entities using natural language descriptions.
    
    Use this tool when the user's request is vague or you don't know the exact entity_id.
    - 'Find the fan in the office' -> description='fan', area='office'
    - 'Search for security sensors' -> description='sensor', label='Security'

    Args:
        description: Natural language search term (e.g., "desk lamp").
        area: (Optional) The room or location to narrow results.
        label: (Optional) The category or type of entity to filter by.
    
    Returns:
        A list of schemas.SearchEntity objects ordered by a matching relevant score. Each
        object contains a integer score and the correspondent entity information (ID, name, state, attrs)
    """
    area_entities = label_entities = []
    if area:
        area_entities = await _retrieval.get_area_entities(area)
    if label:
        label_entities = await _retrieval.get_label_entities(label)

    entities = label_entities + area_entities

    if not entities:
        entities = await _retrieval.get_all_entities()

    if not entities:
        return "Failed to retrieve entities from Home Assistant."
    
    try:
        return helpers.search_entities_by_keywords(entities, description)
    except Exception as e:
        return f"Error during search: {str(e)}"