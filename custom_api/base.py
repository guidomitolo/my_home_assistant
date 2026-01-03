import re
import os
from typing import List, Dict, Any
from schemas import Entity

# API Configuration
HA_URL = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
TOKEN =  os.getenv('TOKEN')



def search_entities_by_keywords(entities: List[Entity], description: str) -> List[Dict[str, Any]]:
    """Search for entities matching a natural language description.
    
    Args:
        entities: List of entity object list from Home Assistant
        description: Natural language description of the entity
        
    Returns:
        A list of matching entity objects sorted by relevance score
    """
    # Break description into tokens
    tokens = re.findall(r'\w+', description.lower())
    
    # Search for matching entities
    matches = []
    for entity in entities:
        entity._score = 0
        for token in tokens:
            for keyword in entity._keywords:
                if token in keyword:
                    entity._score += 1
        if entity._score:
            matches.append(entity)
    
    # Sort matches by score (descending)
    return sorted(matches, key=lambda ent: ent._score, reverse=True)


def format_entity_results(matches: List[Entity], limit: int = 10) -> str:
    """Format entity search results into a readable string.
    
    Args:
        matches: List of matching entities with scores
        limit: Maximum number of results to include
        
    Returns:
        Formatted string with entity results
    """
    if matches:
        result = "Found matching entities:\n"
        for entity in matches[:limit]:
            result += f"- Score: {entity._score} - {entity.id} ({entity.name})\n"
        return result
    else:
        return "No matching entities found." 