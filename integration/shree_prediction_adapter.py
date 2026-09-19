"""
Shree Prediction Adapter
------------------------
Connects the live SUMO traffic state from Q-TRAFFIC to Shree's
independent prediction module.

The adapter adds this field to every junction:

    state["predicted"] = {
        "1min": ...,
        "3min": ...,
        "5min": ...
    }

The QUBO builder already understands this field.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict


# ------------------------------------------------------------------
# SHREE PROJECT LOCATION
# ------------------------------------------------------------------

SHREE_PROJECT = Path(
    r"C:\Users\shree\Downloads\Q-TRAFFIC-Shree-v2\Q-TRAFFIC-Shree"
)

if SHREE_PROJECT.exists():
    project_path = str(SHREE_PROJECT)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)


# ------------------------------------------------------------------
# IMPORT SHREE PREDICTOR
# ------------------------------------------------------------------

try:
    from prediction.predictor import predict_network
    PREDICTOR_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as exc:
    predict_network = None
    PREDICTOR_AVAILABLE = False
    IMPORT_ERROR = exc


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fallback_prediction(state: Dict[str, Any]) -> Dict[str, int]:
    """Safe fallback if the external Shree predictor cannot be imported."""

    vehicles = max(_safe_float(state.get("vehicles", 0)), 0.0)
    queue = max(_safe_float(state.get("queue", 0)), 0.0)
    capacity = max(_safe_float(state.get("capacity", 50)), 1.0)

    pressure = min(
        (vehicles + queue) / capacity,
        2.0,
    )

    growth = max(
        1.0,
        vehicles * (0.03 + 0.08 * pressure),
    )

    return {
        "1min": int(round(vehicles + growth)),
        "3min": int(round(vehicles + growth * 2)),
        "5min": int(round(vehicles + growth * 3)),
    }


def _normalize_prediction(
    prediction: Any,
    state: Dict[str, Any],
) -> Dict[str, int]:

    fallback = _fallback_prediction(state)

    if not isinstance(prediction, dict):
        return fallback

    return {
        "1min": int(round(max(
            _safe_float(prediction.get("1min"), fallback["1min"]),
            0.0,
        ))),
        "3min": int(round(max(
            _safe_float(prediction.get("3min"), fallback["3min"]),
            0.0,
        ))),
        "5min": int(round(max(
            _safe_float(prediction.get("5min"), fallback["5min"]),
            0.0,
        ))),
    }


# ------------------------------------------------------------------
# LIVE PREDICTION
# ------------------------------------------------------------------

def predict_live_traffic(
    traffic_context: Dict[str, Dict[str, Any]],
    demand_multiplier: float = 1.0,
) -> Dict[str, Dict[str, int]]:
    """
    Run Shree's predictor against the current live SUMO state.
    """

    prediction_input: Dict[str, Dict[str, Any]] = {}

    for junction_id, state in traffic_context.items():
        prediction_input[junction_id] = {
            "vehicles": max(
                _safe_float(state.get("vehicles", 0)),
                0.0,
            ),
            "queue": max(
                _safe_float(state.get("queue", 0)),
                0.0,
            ),
            "speed": max(
                _safe_float(state.get("speed", 0)),
                0.0,
            ),
            "capacity": max(
                _safe_float(state.get("capacity", 50)),
                1.0,
            ),
            "signal": state.get("signal", "UNKNOWN"),
        }

    if not PREDICTOR_AVAILABLE:
        print(
            "[PREDICTION] Shree predictor unavailable; using fallback.",
            IMPORT_ERROR,
        )

        return {
            junction_id: _fallback_prediction(state)
            for junction_id, state in prediction_input.items()
        }

    try:
        raw_predictions = predict_network(
            prediction_input,
            demand_multiplier=demand_multiplier,
        )

    except Exception as exc:
        print(
            "[PREDICTION] Shree predictor failed; using fallback:",
            type(exc).__name__,
            str(exc),
        )

        return {
            junction_id: _fallback_prediction(state)
            for junction_id, state in prediction_input.items()
        }

    predictions: Dict[str, Dict[str, int]] = {}

    for junction_id, state in prediction_input.items():
        predictions[junction_id] = _normalize_prediction(
            raw_predictions.get(junction_id, {}),
            state,
        )

    return predictions


# ------------------------------------------------------------------
# ATTACH TO LIVE CONTEXT
# ------------------------------------------------------------------

def attach_predictions(
    traffic_context: Dict[str, Dict[str, Any]],
    demand_multiplier: float = 1.0,
) -> Dict[str, Dict[str, Any]]:
    """
    Mutates and returns the live SUMO context by adding
    the 1/3/5 minute prediction for every junction.
    """

    predictions = predict_live_traffic(
        traffic_context,
        demand_multiplier=demand_multiplier,
    )

    for junction_id, prediction in predictions.items():
        if junction_id not in traffic_context:
            continue

        traffic_context[junction_id]["predicted"] = prediction

    return traffic_context


# ------------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------------

def print_prediction_summary(
    traffic_context: Dict[str, Dict[str, Any]],
) -> None:

    print()
    print("PREDICTIVE TRAFFIC INTELLIGENCE")
    print("-" * 60)

    for junction_id in sorted(traffic_context):
        state = traffic_context[junction_id]
        predicted = state.get("predicted", {})

        print(
            f"{junction_id}: "
            f"current={_safe_float(state.get('vehicles', 0)):.1f} | "
            f"1min={_safe_float(predicted.get('1min', 0)):.1f} | "
            f"3min={_safe_float(predicted.get('3min', 0)):.1f} | "
            f"5min={_safe_float(predicted.get('5min', 0)):.1f}"
        )

    print()
