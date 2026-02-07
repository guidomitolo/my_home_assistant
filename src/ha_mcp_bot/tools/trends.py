import logging
import ha_mcp_bot.helpers as helpers
import ha_mcp_bot.schemas as schemas
from datetime import datetime, timedelta
from typing import Optional, List, Union
from ha_mcp_bot.api import RetrievalService

logger = logging.getLogger(__name__)

_retrival = RetrievalService()


async def analyze_entity_trends(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
) -> dict:
    """
    Analyzes historical patterns and statistical summaries for any Home Assistant entity.
    Use this tool to evaluate electrical health, usage durations, or event frequencies.

    Args:
        entity_id: The full entity ID (e.g., 'sensor.main_power', 'light.kitchen', 'binary_sensor.door').
        start_time: ISO 8601 UTC timestamp (e.g., '2026-01-27T00:00:00Z'). 
                    Defaults to the start of the available history.
        end_time: ISO 8601 UTC timestamp (e.g., '2026-01-27T23:59:59Z').
                  Defaults to current time.

    Capabilities:
        - Electrical & Numeric (Power, Voltage, Temp): Returns statistics like Average (Mean), 
          Peaks (Max), and Sags (Min). Ideal for load analysis and monitoring electrical stability.
        - State & Event Tracking (Lights, Doors, Switches): Calculates 'Time Spent' in each 
          state (e.g., "On" for 4.5 hours) and 'Change Count' (e.g., "Opened 12 times").
        - Current Status: Provides the most recent state and the time of the last change.

    Returns:
        A dictionary summarizing the behavior of the entity over the requested period.
    """
    history = await _retrival.get_history(entity_id, start_time, end_time, limit=100)
    if not history:
        return f"Could not find enough data to analyze {entity_id}."
    stats = helpers.get_history_analytics(history)
    return stats


async def calculate_electrical_delta(entity_id: str, start_time: str, end_time: str) -> Optional[str]:
    """
    Calculates the change (delta) for electrical sensors (Energy, Power, or Voltage) between two points in time.
    Use this to measure consumption increases (kWh) or fluctuations in tension (V) and load (kW).

    Args:
        entity_id: The Home Assistant entity ID (e.g., 'sensor.fridge_energy', 'sensor.main_voltage').
        start_time: ISO 8601 UTC timestamp for the start of the period (e.g., '2026-01-27T12:00:00Z').
        end_time: ISO 8601 UTC timestamp for the end of the period (e.g., '2026-01-27T13:00:00Z').

    Returns:
        A string with the calculated difference and its unit (e.g., "5.2 kWh" or "-3.5 V").
    """
    time_format = '%Y-%m-%dT%H:%M:%S%z'

    # Fetching Start State
    start_dt = datetime.strptime(start_time, time_format) 
    next_to_start = start_dt + timedelta(seconds=1)
    start_history = await _retrival.get_history(
        entity_id,
        start_dt.strftime(time_format),
        next_to_start.strftime(time_format),
        limit=1
    )

    # Fetching End State
    end_dt = datetime.strptime(end_time, time_format) 
    next_to_end = end_dt + timedelta(seconds=1)
    end_history = await _retrival.get_history(
        entity_id,
        end_dt.strftime(time_format),
        next_to_end.strftime(time_format),
        limit=1
    )

    if not start_history or not end_history:
        return None

    # Calculate delta: (Latest Value) - (Initial Value)
    delta_value = end_history[0].state - start_history[0].state
    unit = end_history[0].unit_of_measurement

    return f"{delta_value} {unit}"


async def get_entity_state_history(
    entity_id: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
) -> Union[List[schemas.HistoryNumericState], List[schemas.HistoryCategoricalState], str]:
    """
    Retrieves the raw chronological history of state changes for a specific entity. 
    
    Use this to find:
    - 'When was the front door last opened?'
    - 'Show me the temperature logs for the last 4 hours.'
    - 'How has the power usage changed since this morning?'
    
    Args:
        entity_id: The full ID of the entity (e.g., 'sensor.living_room_temp').
        start_time: ISO 8601 UTC timestamp (e.g., '2026-01-10T10:00:00Z'). 
                    If omitted, the tool retrieves data for the last 24 hours.
        end_time: ISO 8601 UTC timestamp. If omitted, defaults to the current time.
    """
    try:
        result = await _retrival.get_history(entity_id, start_time, end_time)
        if not result:
            return f"No history records found for {entity_id} in that range."
        return result
    except Exception as e:
        return f"Error fetching history: {e}"