def build_dashboard_output(
    location,
    scenario,
    traffic_state,
    predictions,
    confidence,
    shock_map,
    shock_visualization,
    demand,
    scenario_description="",
):
    """
    Build dashboard-ready output for Shree's
    predictive traffic intelligence module.
    """

    prediction_output = {}

    for junction, state in traffic_state.items():

        prediction_data = predictions.get(
            junction,
            {}
        )

        confidence_data = confidence.get(
            junction,
            {}
        )

        prediction_1min = prediction_data.get(
            "1min",
            0
        )

        prediction_3min = prediction_data.get(
            "3min",
            0
        )

        prediction_5min = prediction_data.get(
            "5min",
            0
        )

        prediction_output[junction] = {
            "density": state.get(
                "vehicles",
                0
            ),

            "queue": state.get(
                "queue",
                0
            ),

            "speed": state.get(
                "speed",
                0
            ),

            "capacity": state.get(
                "capacity",
                0
            ),

            "predicted": prediction_5min,

            "prediction_1min": prediction_1min,

            "prediction_3min": prediction_3min,

            "prediction_5min": prediction_5min,

            "confidence_1min": confidence_data.get(
                "1min",
                0
            ),

            "confidence_3min": confidence_data.get(
                "3min",
                0
            ),

            "confidence_5min": confidence_data.get(
                "5min",
                0
            ),
        }

    # ------------------------------------------
    # Dashboard output
    # ------------------------------------------

    dashboard_output = {
        "location": location,

        "scenario": scenario,

        "scenario_description": scenario_description,

        "prediction": prediction_output,

        "shock": {
            "source": shock_visualization.get(
                "source"
            ),

            "propagation": shock_visualization.get(
                "propagation",
                []
            ),

            "intensity": shock_map,
        },

        "demand_forecast": demand,

        "dashboard_notes": {
            "traffic_source": "SIMULATED",

            "location_type": "LOCATION_INSPIRED",

            "live_traffic_claim": False,
        },
    }

    return dashboard_output


# ==========================================================
# SHREE → NILA QUBO INTERFACE
# ==========================================================

def build_qubo_input(
    location,
    scenario,
    traffic_state,
    predictions,
    confidence,
    shock_map,
    shock_visualization,
    demand,
):
    """
    Build a clean prediction interface for Nila's
    QUBO/QAOA optimization module.

    This function exposes the traffic intelligence
    required by the optimization layer.
    """

    predicted_traffic = {}

    current_congestion = {}

    current_traffic = {}

    confidence_output = {}

    # ------------------------------------------------------
    # Build junction-level optimization data
    # ------------------------------------------------------

    for junction, state in traffic_state.items():

        prediction_data = predictions.get(
            junction,
            {}
        )

        confidence_data = confidence.get(
            junction,
            {}
        )

        # Future traffic predictions
        predicted_traffic[junction] = {
            "1min": prediction_data.get(
                "1min",
                0
            ),

            "3min": prediction_data.get(
                "3min",
                0
            ),

            "5min": prediction_data.get(
                "5min",
                0
            ),
        }

        # Current traffic state
        vehicles = state.get(
            "vehicles",
            0
        )

        queue = state.get(
            "queue",
            0
        )

        speed = state.get(
            "speed",
            0
        )

        capacity = state.get(
            "capacity",
            0
        )

        signal = state.get(
            "signal",
            "UNKNOWN"
        )

        current_traffic[junction] = {
            "vehicles": vehicles,

            "queue": queue,

            "speed": speed,

            "capacity": capacity,

            "signal": signal,
        }

        # Current congestion ratio
        if capacity > 0:

            current_congestion[junction] = round(
                queue / capacity,
                4
            )

        else:

            current_congestion[junction] = 0

        # Prediction confidence
        confidence_output[junction] = {
            "1min": confidence_data.get(
                "1min",
                0
            ),

            "3min": confidence_data.get(
                "3min",
                0
            ),

            "5min": confidence_data.get(
                "5min",
                0
            ),
        }

    # ------------------------------------------------------
    # Final QUBO interface
    # ------------------------------------------------------

    qubo_output = {

        # Interface version
        "schema_version": "1.0",

        # Prediction horizons supplied by Shree
        "prediction_horizon": [
            "1min",
            "3min",
            "5min"
        ],

        "location": location,

        "scenario": scenario,

        # Current observed traffic
        "current_traffic": current_traffic,

        # Current queue/capacity congestion
        "current_congestion": current_congestion,

        # Future predicted traffic
        "predicted_traffic": predicted_traffic,

        # Traffic shock information
        "shock": {
            "source": shock_visualization.get(
                "source"
            ),

            "propagation": shock_visualization.get(
                "propagation",
                []
            ),

            "intensity": shock_map,
        },

        # Forecast demand
        "demand_forecast": demand,

        # Prediction confidence
        "confidence": confidence_output,
    }

    return qubo_output