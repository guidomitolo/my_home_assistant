from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional
from enum import Enum



class SwitchCommand(str, Enum):
    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class BaseSchema(BaseModel):
    """Shared configuration to handle Home Assistant's flat data and aliases."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def map_flat_fields(cls, data: dict):
        # Automatically bundles area_id/area_name into the nested 'area' object
        if not isinstance(data, dict):
            return data

        area_id = data.get("area_id")
        area_name = data.get("area_name")
        
        if (area_id or area_name) and not data.get("area"):
            data["area"] = {"id": area_id, "name": area_name}
            
        return data


class Context(BaseSchema):
    """Traceability information for who or what triggered a state change."""
    id: Optional[str] = Field(None, description="Unique ID of the context")
    parent_id: Optional[str] = Field(None, description="ID of the parent context if chained")
    user_id: Optional[str] = Field(None, description="ID of the user who triggered the change")


class Attributes(BaseSchema):
    """Detailed metadata and technical specifications for an entity."""
    friendly_name: Optional[str] = Field(None, description="Human-readable name")
    device_class: Optional[str] = Field(None, description="Category of device (e.g., energy, motion)")
    state_class: Optional[str] = Field(None, description="Classification of the state (e.g., measurement)")
    unit_of_measurement: Optional[str] = Field(None, description="Unit (e.g., kWh, °C, %)")
    auto_update: bool = Field(False, description="Whether the firmware/software updates automatically")
    display_precision: Optional[int] = None
    installed_version: Optional[str] = None
    in_progress: bool = False
    latest_version: Optional[str] = None
    release_summary: Optional[str] = None
    release_url: Optional[str] = None
    skipped_version: Optional[str] = None
    title: Optional[str] = None
    update_percentage: Optional[int] = None
    entity_picture: Optional[str] = None
    supported_features: int = 0


class Area(BaseSchema):
    """The physical or logical zone where a device or entity is located."""
    id: Optional[str] = Field(None, alias="area_id", description="Unique ID of the area")
    name: Optional[str] = Field(None, alias="area_name", description="Friendly name (e.g., 'Master Bedroom')")


class Label(BaseSchema):
    """A user-defined tag for organizing or filtering data."""
    id: str = Field(alias="label_id")
    name: str = Field(alias="label_name")
    description: Optional[str] = Field(None, alias="label_description")


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

class EntityCore(BaseSchema):
    """Minimal entity reference used for lists or IDs."""
    id: str = Field(alias="entity_id", description="Unique entity ID")
    name: Optional[str] = Field(None, alias="entity_name", description="Friendly entity name")


class Entity(EntityCore):
    """Full entity details including its current state and device relationship."""
    state: str = Field(alias="entity_state", description="The current numeric or string value")
    last_changed: Optional[datetime] = None
    area: Optional[Area] = None
    labels: List[Label] = Field(default_factory=list)
    attributes: Optional[Attributes] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None


class Device(BaseSchema):
   """A hardware or service container grouping multiple entities."""
   id: str = Field(alias="device_id", description="Hardware device ID")
   name: str = Field(alias="device_name", description="Friendly device name")
   entities: List[EntityCore] = Field(default_factory=list, description="Entities belonging to this device")
   labels: List[Label] = Field(default_factory=list)
   area: Optional[Area] = None


class HistoryState(BaseModel):
    state: str
    last_changed: datetime