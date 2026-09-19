"""
Integrated rolling traffic intelligence pipeline.

Combines:
1. Rolling traffic prediction
2. Confidence estimation
3. Automatic traffic-shock detection
4. Shock propagation

This module is independent of the SUMO network and can later
consume real TraCI traffic snapshots.
"""

from typing import Dict, List, Optional

from prediction.predictor import predict_network
from prediction.confidence import build_confidence_map
from prediction.shock_detector import detect_traffic_shock
from prediction.shock_propagation import propagate_shock


def run_integrated_cycle(
    traffic_state: Dict,
    demand_multiplier: float = 1.0,
    historical_data=None,
    previous_state: Optional[Dict] = None,
) -> Dict:
    """
    Run one complete traffic-intelligence cycle.

    If previous_state is provided, the current traffic state is
    compared against it to detect a traffic shock.
    """

    # ---------------------------------------------------------
    # 1. Predict future traffic
    # ---------------------------------------------------------

    predictions = predict_network(
        traffic_state,
        demand_multiplier=demand_multiplier,
        historical_data=historical_data,
    )

    # ---------------------------------------------------------
    # 2. Calculate prediction confidence
    # ---------------------------------------------------------

    confidence = build_confidence_map(
        traffic_state,
        predictions,
    )

    # ---------------------------------------------------------
    # 3. Detect traffic shock
    # ---------------------------------------------------------

    if previous_state is not None:

        shock_event = detect_traffic_shock(
            previous_state,
            traffic_state,
        )

    else:

        shock_event = {
            "detected": False,
            "source": None,
            "severity": "LOW",
            "changes": {},
            "score": 0.0,
            "junctions": {},
        }

    # ---------------------------------------------------------
    # 4. Propagate shock through network
    # ---------------------------------------------------------

    if shock_event["detected"]:

        event = {
            "type": "TRAFFIC_SHOCK",
            "junction": shock_event["source"],
            "severity": shock_event["severity"],
        }

        shock_map = propagate_shock(
            traffic_state,
            event,
        )

    else:

        # No detected shock.
        # The existing propagation function provides the
        # baseline congestion intensity.
        shock_map = propagate_shock(
            traffic_state,
            None,
        )

    return {
        "traffic_state": traffic_state,
        "predictions": predictions,
        "confidence": confidence,
        "shock_event": shock_event,
        "shock_map": shock_map,
    }


def run_integrated_rolling_pipeline(
    traffic_states: List[Dict],
    demand_multiplier: float = 1.0,
    historical_data=None,
) -> List[Dict]:
    """
    Run the integrated pipeline across consecutive traffic states.

    Each traffic snapshot represents a later point in the
    simulation.

    The previous snapshot is automatically used for shock
    detection.
    """

    results = []

    previous_state = None

    for step, traffic_state in enumerate(traffic_states):

        result = run_integrated_cycle(
            traffic_state=traffic_state,
            demand_multiplier=demand_multiplier,
            historical_data=historical_data,
            previous_state=previous_state,
        )

        result["step"] = step

        results.append(result)

        previous_state = traffic_state

    return results