from typing import List
from collections import Counter
from schemas import HistoryNumericState, HistoryCategoricalState, HistoryState


class StateAnalytics:
    
    @staticmethod
    def numeric_summary(instances: List[HistoryNumericState]) -> dict:
        if not instances: return {}
        vals = [i.state for i in instances]
        return {
            "avg": sum(vals) / len(vals),
            "max": max(vals),
            "min": min(vals),
            "unit": instances[0].unit_of_measurement
        }

    @staticmethod
    def categorical_summary(instances: List[HistoryCategoricalState]) -> dict:
        if not instances: return {}
        counts = Counter(i.state for i in instances)
        return {
            "most_common": counts.most_common(1)[0][0],
            "total_changes": len(instances),
            "distribution": dict(counts)
        }
    
    @staticmethod
    def state_durations(instances: List[HistoryCategoricalState]) -> dict[str, float]:
        """Returns total seconds spent in each state."""
        durations = {}
        
        for i in range(len(instances) - 1):
            state_label = instances[i].state
            duration = (instances[i+1].last_changed - instances[i].last_changed).total_seconds()
            
            durations[state_label] = durations.get(state_label, 0) + duration
            
        return durations
    

def get_history_analytics(
    state_history: List[HistoryState],
    ) -> dict:
    """
    Performs statistical analysis on a sequence of Home Assistant state records.

    This function automatically detects if the history is numeric (measurements) 
    or categorical (labels/states) and returns the appropriate statistical summary.

    Args:
        state_history: A list of state objects retrieved from Home Assistant. 
            Should be either all HistoryNumericState or all HistoryCategoricalState.

    Returns:
        dict: A dictionary containing the analysis results.
        
        If the input is Numeric (e.g., Temperature, Power):
            - 'avg' (float): The mean value across all records.
            - 'max' (float): The highest value recorded.
            - 'min' (float): The lowest value recorded.
            - 'unit' (str): The unit of measurement (e.g., '°C', 'W').

        If the input is Categorical (e.g., On/Off, Open/Closed):
            - 'most_common' (str): The state the entity was in most frequently.
            - 'total_changes' (int): The number of times the state changed.
            - 'distribution' (dict): A mapping of state labels to occurrence counts.
            - 'durations' (dict): A mapping of state labels to total seconds spent 
              in that state (time-weighted).
    """
    if not state_history:
        return {}
    
    if isinstance(state_history[0], HistoryNumericState):
        stats = StateAnalytics.numeric_summary(state_history)
    
    if isinstance(state_history[0], HistoryCategoricalState):
        stats = StateAnalytics.categorical_summary(state_history)
        durations = StateAnalytics.state_durations(state_history)
        stats.update({'durations': durations})

    return stats
    