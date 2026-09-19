import json
from pathlib import Path
from typing import Dict, Any


REQUIRED_FIELDS = ["vehicles", "queue", "speed", "capacity", "signal"]


def load_traffic_state(path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Load and validate a junction-based traffic-state JSON file."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    validate_traffic_state(data)
    return data


def validate_traffic_state(data: Dict[str, Dict[str, Any]]) -> None:
    """Validate the common traffic-state contract."""
    if not isinstance(data, dict) or not data:
        raise ValueError("Traffic state must be a non-empty dictionary.")

    for junction, state in data.items():
        missing = [field for field in REQUIRED_FIELDS if field not in state]
        if missing:
            raise ValueError(f"{junction} is missing fields: {missing}")

        for field in ["vehicles", "queue", "speed", "capacity"]:
            if not isinstance(state[field], (int, float)):
                raise TypeError(f"{junction}.{field} must be numeric.")
            if state[field] < 0:
                raise ValueError(f"{junction}.{field} cannot be negative.")


def calculate_congestion_ratio(state: Dict[str, Any]) -> float:
    """Estimate congestion using queue relative to road capacity."""
    capacity = max(float(state["capacity"]), 1.0)
    return min(float(state["queue"]) / capacity, 1.0)


def normalize_traffic_state(data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Add a normalized congestion ratio without changing original fields."""
    validate_traffic_state(data)

    normalized = {}
    for junction, state in data.items():
        normalized[junction] = {
            **state,
            "congestion_ratio": round(calculate_congestion_ratio(state), 4)
        }

    return normalized
