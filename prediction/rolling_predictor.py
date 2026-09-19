"""
Rolling-horizon traffic prediction.

Runs repeated prediction cycles using updated traffic states.
Designed to work with SAMPLE, SUMO test data, and later TraCI.
"""

from typing import Dict, List, Optional

from prediction.predictor import predict_network
from prediction.confidence import build_confidence_map
from prediction.shock_propagation import propagate_shock


def run_prediction_cycle(
    traffic_state: Dict,
    demand_multiplier: float = 1.0,
    historical_data=None,
    event: Optional[Dict] = None,
) -> Dict:
    """
    Run one prediction cycle.

    Returns predictions, confidence and shock information.
    """

    predictions = predict_network(
        traffic_state,
        demand_multiplier=demand_multiplier,
        historical_data=historical_data,
    )

    confidence = build_confidence_map(
        traffic_state,
        predictions,
    )

    shock_map = propagate_shock(
        traffic_state,
        event,
    )

    return {
        "predictions": predictions,
        "confidence": confidence,
        "shock_map": shock_map,
    }


def run_rolling_prediction(
    traffic_states: List[Dict],
    demand_multiplier: float = 1.0,
    historical_data=None,
    events: Optional[List[Optional[Dict]]] = None,
) -> List[Dict]:
    """
    Run prediction over multiple traffic snapshots.

    Each item in traffic_states represents traffic at a later
    simulation time.

    Example:

        traffic_states = [
            state_at_t0,
            state_at_t1,
            state_at_t2,
        ]
    """

    results = []

    if events is None:
        events = [None] * len(traffic_states)

    for step, traffic_state in enumerate(traffic_states):

        event = (
            events[step]
            if step < len(events)
            else None
        )

        cycle = run_prediction_cycle(
            traffic_state=traffic_state,
            demand_multiplier=demand_multiplier,
            historical_data=historical_data,
            event=event,
        )

        results.append(
            {
                "step": step,
                "traffic_state": traffic_state,
                **cycle,
            }
        )

    return results