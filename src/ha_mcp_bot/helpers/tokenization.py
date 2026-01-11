import re
from ha_mcp_bot.schemas import Entity
from typing import List


def tokenizer(entity: Entity) -> List[str]:
    """
    transform entitys id, name, description, labels and areas in
    identifilable tokens for keyword matching

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

    tokens = filter(lambda term: len(term) > 2, tokens)

    return tokens