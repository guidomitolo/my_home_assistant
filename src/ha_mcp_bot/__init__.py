"""
ha_mcp_bot: A Home Assistant MCP Server with Energy Intelligence.
"""
from .api import HomeAssistantAPI, RetrievalService, ActionService, get_default_api
from .schemas import HistoryState, HistoryNumericState, State, Entity
from .helpers import StateAnalytics, search_entities_by_keywords

__version__ = "0.1.0"

__all__ = [
    "HomeAssistantAPI",
    "RetrievalService",
    "ActionService",
    "get_default_api",
    "HistoryState",
    "HistoryNumericState",
    "State",
    "Entity",
    "StateAnalytics",
    "search_entities_by_keywords",
    "__version__",
]


