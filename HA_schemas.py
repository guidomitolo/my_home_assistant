from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional



class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    @model_validator(mode="before")
    @classmethod
    def map_flat_fields(cls, data: dict):
        if "area_id" in data and "area_name" in data:
            data["area"] = {"id": data["area_id"], "name": data["area_name"]}
        return data


class Context(BaseSchema):
    id: Optional[str] = None
    parent_id: Optional[str] = None
    user_id: Optional[str] = None


class Attributes(BaseSchema):
    auto_update: bool = False
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
    friendly_name: Optional[str] = None
    supported_features: int = 0
    device_class: Optional[str] = None
    state_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None


class Area(BaseSchema):
    id: Optional[str] = Field(None, alias="area_id")
    name: Optional[str] = Field(None, alias="area_name")


class Label(BaseSchema):
    id: str = Field(alias="label_id")
    name: str = Field(alias="label_name")
    description: Optional[str] = Field(None, alias="label_description")


class StateCore(BaseSchema):
    state: str
    entity_id: str
    entity_name: Optional[str] = None
    last_changed: datetime
    area: Optional[Area] = None


class State(StateCore):
    attributes: Attributes
    last_reported: datetime
    last_updated: datetime
    context: Optional[Context] = {}


class EntityCore(BaseSchema):
    id: str = Field(None, alias="entity_id")
    name: Optional[str] = Field(None, alias="entity_id")


class Entity(EntityCore):
    state: str = Field(None, alias="entity_id")
    last_changed: Optional[datetime] = None
    area: Optional[Area] = None
    labels: List[Label] = []
    attributes: Optional[Attributes] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None


class Device(BaseSchema):
   id: str = Field(None, alias="device_id")
   name: str = Field(None, alias="device_id")
   entities: List[EntityCore] = []
   labels: List[Label] = []
   area: Optional[Area] = None

