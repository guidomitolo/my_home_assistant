import re
from typing import List, Dict, Any
from schemas import Entity


def search_entities_by_keywords(entities: List[Entity], description: str) -> List[Dict[str, Any]]:
    """Search for entities matching a natural language description.
    
    Args:
        entities: List of entity object list from Home Assistant
        description: Natural language description of the entity
        
    Returns:
        A list of matching entity objects sorted by relevance score
    """
    tokens = set(re.findall(r'\w+', description.lower()))
    matches = []
    
    for entity in entities:
        keywords = entity._keywords
        for keyworkd in keywords:
            for token in tokens:
                if keyworkd in token:
                    entity._score += 1
        if entity._score > 0:
            matches.append(entity)
            
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
        for i, entity in enumerate(matches[:limit]):
            result += f"{i + 1}. Score: {entity._score} - Entity ID: {entity.id} - Entity Name: {entity.name}\n"
        return result
    else:
        return "No matching entities found." 