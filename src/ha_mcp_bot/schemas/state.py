from datetime import datetime
from pydantic import Field, model_validator
from typing import Optional
from .common import BaseSchema, Attributes, Context, Area


class StateCore(BaseSchema):
    """A minimal snapshot of an entity's status."""
    entity_id: str = Field(description="Full entity ID string")
    state: str = Field(description="Current state value (e.g., 'on', '75.2')")
    last_changed: datetime = Field(description="Timestamp of the last value change")
    area: Optional[Area] = None


class State(StateCore):
    """A comprehensive state object including attributes and context."""
    entity_name: Optional[str] = Field(None, description="Entity name given by friendly name attr")
    attributes: Optional[Attributes] = None
    last_reported: datetime
    last_updated: datetime
    context: Optional[Context] = Field(default=None)

    @model_validator(mode='before')
    @classmethod
    def entity_name_fill(cls, data: dict) -> dict:
        if data and isinstance(data, dict):
            if data.get('attributes'):
                data['entity_name'] = data['attributes'].get('friendly_name')
        return data