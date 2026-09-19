"""
Automatic traffic-shock detection.

Compares two consecutive traffic snapshots and detects
abnormal changes in vehicles, queue length, and speed.
"""

from typing import Dict


# Thresholds for detecting significant changes.
VEHICLE_INCREASE_THRESHOLD = 10
QUEUE_INCREASE_THRESHOLD = 5
SPEED_DECREASE_THRESHOLD = 3


def calculate_changes(
    previous_state: Dict,
    current_state: Dict,
) -> Dict[str, Dict]:
    """
    Calculate traffic changes between two consecutive states.
    """

    changes = {}

    junctions = set(previous_state) | set(current_state)

    for junction in junctions:

        previous = previous_state.get(junction, {})
        current = current_state.get(junction, {})

        previous_vehicles = previous.get("vehicles", 0)
        current_vehicles = current.get("vehicles", 0)

        previous_queue = previous.get("queue", 0)
        current_queue = current.get("queue", 0)

        previous_speed = previous.get("speed", 0)
        current_speed = current.get("speed", 0)

        changes[junction] = {
            "vehicles": current_vehicles - previous_vehicles,
            "queue": current_queue - previous_queue,
            "speed": current_speed - previous_speed,
        }

    return changes


def calculate_shock_score(change: Dict) -> float:
    """
    Calculate a transparent shock score from traffic changes.

    The score is based on:
    - vehicle increase
    - queue increase
    - speed decrease
    """

    vehicle_change = change["vehicles"]
    queue_change = change["queue"]
    speed_change = change["speed"]

    vehicle_score = max(
        0.0,
        vehicle_change / VEHICLE_INCREASE_THRESHOLD,
    )

    queue_score = max(
        0.0,
        queue_change / QUEUE_INCREASE_THRESHOLD,
    )

    speed_score = max(
        0.0,
        -speed_change / SPEED_DECREASE_THRESHOLD,
    )

    # Weighted combination.
    score = (
        0.4 * vehicle_score
        + 0.4 * queue_score
        + 0.2 * speed_score
    )

    return round(score, 3)


def classify_severity(score: float) -> str:
    """
    Convert shock score into a severity level.
    """

    if score >= 1.5:
        return "HIGH"

    if score >= 0.75:
        return "MEDIUM"

    return "LOW"


def detect_traffic_shock(
    previous_state: Dict,
    current_state: Dict,
) -> Dict:
    """
    Detect the strongest traffic shock between two snapshots.
    """

    changes = calculate_changes(
        previous_state,
        current_state,
    )

    junction_results = {}

    for junction, change in changes.items():

        score = calculate_shock_score(change)

        severity = classify_severity(score)

        junction_results[junction] = {
            "score": score,
            "severity": severity,
            "changes": change,
        }

    # Select the junction with the largest shock score.
    source_junction = max(
        junction_results,
        key=lambda junction: junction_results[junction]["score"],
        default=None,
    )

    if source_junction is None:
        return {
            "detected": False,
            "source": None,
            "severity": "LOW",
            "changes": {},
            "junctions": {},
        }

    source_result = junction_results[source_junction]

    detected = source_result["score"] >= 0.75

    return {
        "detected": detected,
        "source": source_junction if detected else None,
        "severity": (
            source_result["severity"]
            if detected
            else "LOW"
        ),
        "changes": (
            source_result["changes"]
            if detected
            else {}
        ),
        "score": source_result["score"],
        "junctions": junction_results,
    }