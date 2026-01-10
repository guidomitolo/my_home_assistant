from datetime import datetime
from pydantic import Field
from typing import Optional
from .base import BaseSchema, Attributes, Context, Area


class StateCore(BaseSchema):
    """A minimal snapshot of an entity's status."""
    entity_id: str = Field(description="Full entity ID string")
    state: str = Field(description="Current state value (e.g., 'on', '75.2')")
    entity_name: Optional[str] = Field(None, description="Display name of the entity")
    last_changed: datetime = Field(description="Timestamp of the last value change")
    area: Optional[Area] = None


class State(StateCore):
    """A comprehensive state object including attributes and context."""
    attributes: Attributes
    last_reported: datetime
    last_updated: datetime
    context: Optional[Context] = Field(default=None)