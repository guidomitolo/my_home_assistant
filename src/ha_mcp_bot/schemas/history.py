from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, List
from typing import List



class HistoryState(BaseModel):
    last_changed: datetime    
    device_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    state_class: Optional[str] = None


class HistoryNumericState(HistoryState):
    state: float 

    @field_validator('state', mode='before')
    @classmethod
    def handle_numeric_strings(cls, v):
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError(f"State '{v}' is not a valid number")


class HistoryCategoricalState(HistoryState):
    state: str


### List of historic states


class HistorySeries(BaseModel):
    entity_id: str
    states: List[HistoryNumericState]


class HistoryCategoricalSeries(BaseModel):
    entity_id: str
    states: List[HistoryCategoricalState]