"""
ha_mcp_bot: A Home Assistant MCP Server with Energy Intelligence.
"""
from .api import (get_areas, get_area_devices, get_labels, get_label_devices, get_all_entities,
get_states_by_condition, get_history, trigger_service)
from .schemas import HistoryState, HistoryNumericState, State, Entity
from .helpers import StateAnalytics, search_entities_by_keywords

__version__ = "0.1.0"

__all__ = [
    "get_areas",
    "get_area_devices",
    "get_labels",
    "get_label_devices",
    "get_all_entities",
    "get_states_by_condition",
    "get_history",
    "trigger_service",
    "HistoryState",
    "HistoryNumericState",
    "State",
    "Entity",
    "StateAnalytics",
    "search_entities_by_keywords",
    "__version__",
]


