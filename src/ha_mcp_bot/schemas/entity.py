from datetime import datetime
from pydantic import Field, model_validator
from typing import List, Optional
from .common import BaseSchema, Area, Label, Attributes
import re



class EntityCore(BaseSchema):
    """Minimal entity reference used for lists or IDs."""
    id: str = Field(alias="entity_id", description="Unique entity ID")
    name: Optional[str] = Field(None, alias="entity_name", description="Entity name")
    domain: str = Field('unknown', description="Entity domain")
    state: str = Field('unknown', alias="entity_state", description="Entity state")

    @model_validator(mode='before')
    @classmethod
    def autofill(cls, data: dict) -> dict:
        if data and isinstance(data, dict):
            entity_id = data.get("entity_id") or data.get("id")
            if entity_id and isinstance(entity_id, str):
                data['domain'] = entity_id.split('.')[0]
            else:
                data['domain'] = "unknown"
        return data


class Entity(EntityCore):
    """Full entity details including its current state and device relationship."""
    last_changed: Optional[datetime] = None
    area: Optional[Area] = None
    labels: List[Label] = Field(default_factory=list)
    attributes: Optional[Attributes] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None


class SearchEntity(BaseSchema):
    entity: Entity
    score: int = 0


class Device(BaseSchema):
   """A hardware or service container grouping multiple entities."""
   id: str = Field(alias="device_id", description="Hardware device ID")
   name: str = Field(alias="device_name", description="Friendly device name")
   entities: List[EntityCore] = Field(default_factory=list, description="Entities belonging to this device")
   labels: List[Label] = Field(default_factory=list)
   area: Optional[Area] = None
    