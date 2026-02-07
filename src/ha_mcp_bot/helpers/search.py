import re
from typing import List, Optional
from ha_mcp_bot.schemas import Entity, SearchEntity
from .tokenization import tokenizer


def search_entities_by_keywords(entities: List[Entity], description: str) -> Optional[List[SearchEntity]]:
    """Search for entities matching a natural language description.
    
    Args:
        entities: List of entity object list from Home Assistant
        description: Natural language description of the entity
        
    Returns:
        A list of matching entity objects sorted by relevance score
    """
    keywords = set(re.findall(r'\w+', description.lower()))
    matches = []
 
    for entity in entities:
        tokens = tokenizer(entity)
        score = 0
        for keyword in keywords:
            for token in tokens:
                if keyword.lower() == token:
                    score += 2
                elif token in keyword:
                    score += 1
        if score > 0:
            found_entity = SearchEntity(entity=entity, score=score)
            matches.append(found_entity)
            
    return sorted(matches, key=lambda e: e.score, reverse=True)