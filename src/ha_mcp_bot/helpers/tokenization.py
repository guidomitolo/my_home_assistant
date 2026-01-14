import re
from ha_mcp_bot.schemas import Entity
from typing import List


def tokenizer(entity: Entity) -> List[str]:
    """
    Tokenizes an entity's metadata for keyword matching.

    Flattens the entity's domain, ID, name, labels, and area into a list of 
    lowercase strings. Strings are split using delimiters (semicolon, comma, 
    pipe, space, underscore, or hyphen) and filtered to remove any tokens 
    with 2 or fewer characters.

    Args:
        entity: The Entity object containing the metadata to be processed.

    Returns:
        A list of alphanumeric strings extracted from the entity's attributes.
    """
    delimiters = r'[;,| _-]+'

    tokens = [entity.domain]
    tokens += re.split(delimiters, entity.id.lower())

    if entity.name:
        tokens += re.split(delimiters, entity.name.lower())

    for label in entity.labels:
        tokens += re.split(delimiters, label.id.lower()) 
        tokens += re.split(delimiters, label.name.lower())
        if label.description:
            tokens += re.split(delimiters, label.description.lower()) 

    if entity.area:
        tokens += re.split(delimiters, entity.area.id.lower()) 
        tokens += re.split(delimiters, entity.area.name.lower())

    tokens = filter(lambda term: len(term) > 1, tokens)

    return tokens