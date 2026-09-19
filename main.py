import json
from pathlib import Path

from config.scenarios import get_scenario

from prediction.traffic_state import (
    load_traffic_state,
    normalize_traffic_state,
)

from prediction.predictor import (
    load_historical_traffic,
    predict_network,
)

from prediction.confidence import build_confidence_map

from prediction.shock_propagation import (
    propagate_shock,
    build_shock_visualization,
)

from prediction.demand_forecast import (
    demand_multiplier,
    forecast_demand,
)

from integration.output_interface import (
    build_dashboard_output,
    build_qubo_input,
)

from integration.sumo_adapter import (
    convert_sumo_observation,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TRAFFIC_FILE = (
    BASE_DIR
    / "data"
    / "sample"
    / "traffic_state.json"
)

HISTORICAL_FILE = (
    BASE_DIR
    / "data"
    / "sample"
    / "historical_traffic.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "output"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "dashboard_traffic.json"
)

QUBO_OUTPUT_FILE = (
    OUTPUT_DIR
    / "prediction_for_qubo.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

LOCATION = "Coimbatore"
SCENARIO = "TEXTILE_FESTIVAL"

# SAMPLE -> use traffic_state.json
# SUMO   -> use SUMO-style test data
INPUT_MODE = "SUMO"


# ============================================================
# SUMO TEST DATA
# ============================================================

SUMO_TEST_DATA = {
    "J1": {
        "vehicle_count": 30,
        "queue_length": 12,
        "mean_speed": 24,
        "capacity": 60,
        "signal": "NS_GREEN",
    },
    "J2": {
        "vehicle_count": 45,
        "queue_length": 22,
        "mean_speed": 18,
        "capacity": 60,
        "signal": "EW_GREEN",
    },
    "J3": {
        "vehicle_count": 31,
        "queue_length": 15,
        "mean_speed": 21,
        "capacity": 50,
        "signal": "NS_GREEN",
    },
    "J4": {
        "vehicle_count": 25,
        "queue_length": 9,
        "mean_speed": 27,
        "capacity": 55,
        "signal": "EW_GREEN",
    },
    "J5": {
        "vehicle_count": 20,
        "queue_length": 8,
        "mean_speed": 29,
        "capacity": 50,
        "signal": "NS_GREEN",
    },
}


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 60)
print("Q-TRAFFIC — SHREE PREDICTION MODULE")
print("=" * 60)

print(f"\nLocation   : {LOCATION}")
print(f"Scenario   : {SCENARIO}")
print(f"Input Mode : {INPUT_MODE}")


# ============================================================
# 1. LOAD SCENARIO
# ============================================================

scenario = get_scenario(
    LOCATION,
    SCENARIO,
)

print("\nScenario configuration loaded.")


# ============================================================
# 2. LOAD CURRENT TRAFFIC
# ============================================================

if INPUT_MODE == "SUMO":

    print("\nLoading SUMO-style traffic observation...")

    traffic_state = convert_sumo_observation(
        SUMO_TEST_DATA
    )

else:

    print("\nLoading sample traffic state...")

    traffic_state = load_traffic_state(
        TRAFFIC_FILE
    )


# Convert SAMPLE/SUMO data to common internal format.

traffic_state = normalize_traffic_state(
    traffic_state
)


# ============================================================
# 3. LOAD HISTORICAL TRAFFIC
# ============================================================

historical_data = load_historical_traffic(
    HISTORICAL_FILE
)


# ============================================================
# 4. CALCULATE DEMAND MULTIPLIER
# ============================================================

multiplier = demand_multiplier(
    scenario_multiplier=scenario["demand_multiplier"],
    is_peak_hour=False,
    event_type=scenario["event_type"],
    event_severity=scenario["event_severity"],
)

print(
    f"\nEffective demand multiplier : {multiplier}"
)


# ============================================================
# 5. TRAFFIC PREDICTION
# ============================================================

predictions = predict_network(
    traffic_state,
    demand_multiplier=multiplier,
    historical_data=historical_data,
)


# ============================================================
# 6. CONFIDENCE
# ============================================================

confidence = build_confidence_map(
    traffic_state,
    predictions,
)


# ============================================================
# 7. TRAFFIC SHOCK PROPAGATION
# ============================================================

incident = scenario.get(
    "default_incident"
)

shock_map = propagate_shock(
    traffic_state,
    incident,
)


# ============================================================
# 8. SHOCK VISUALIZATION
# ============================================================

shock_visualization = build_shock_visualization(
    shock_map,
    incident,
)


# ============================================================
# 9. DEMAND FORECAST
# ============================================================

demand = forecast_demand(
    traffic_state,
    multiplier=multiplier,
    is_peak_hour=False,
    event_type=scenario["event_type"],
    event_severity=scenario["event_severity"],
    scenario_multiplier=scenario["demand_multiplier"],
)


# ============================================================
# 10. BUILD DASHBOARD OUTPUT
# ============================================================
#
# Actual signature:
#
# build_dashboard_output(
#     location,
#     scenario,
#     traffic_state,
#     predictions,
#     confidence,
#     shock_map,
#     shock_visualization,
#     demand,
#     scenario_description=''
# )
# ============================================================

dashboard_output = build_dashboard_output(
    location=LOCATION,
    scenario=SCENARIO,
    traffic_state=traffic_state,
    predictions=predictions,
    confidence=confidence,
    shock_map=shock_map,
    shock_visualization=shock_visualization,
    demand=demand,
    scenario_description=scenario["description"],
)


# ============================================================
# 11. BUILD QUBO INPUT
# ============================================================
#
# Actual signature:
#
# build_qubo_input(
#     location,
#     scenario,
#     traffic_state,
#     predictions,
#     confidence,
#     shock_map,
#     shock_visualization,
#     demand
# )
# ============================================================

qubo_output = build_qubo_input(
    location=LOCATION,
    scenario=SCENARIO,
    traffic_state=traffic_state,
    predictions=predictions,
    confidence=confidence,
    shock_map=shock_map,
    shock_visualization=shock_visualization,
    demand=demand,
)


# ============================================================
# 12. CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 13. SAVE DASHBOARD OUTPUT
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        dashboard_output,
        file,
        indent=2,
    )


# ============================================================
# 14. SAVE QUBO OUTPUT
# ============================================================

with open(
    QUBO_OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        qubo_output,
        file,
        indent=2,
    )


# ============================================================
# 15. DISPLAY TRAFFIC STATE
# ============================================================

print("\n" + "=" * 60)
print("TRAFFIC STATE")
print("=" * 60)

print(
    json.dumps(
        traffic_state,
        indent=2,
    )
)


# ============================================================
# 16. DISPLAY PREDICTIONS
# ============================================================

print("\n" + "=" * 60)
print("PREDICTIONS")
print("=" * 60)

print(
    json.dumps(
        predictions,
        indent=2,
    )
)


# ============================================================
# 17. DISPLAY CONFIDENCE
# ============================================================

print("\n" + "=" * 60)
print("CONFIDENCE")
print("=" * 60)

print(
    json.dumps(
        confidence,
        indent=2,
    )
)


# ============================================================
# 18. DISPLAY TRAFFIC SHOCK
# ============================================================

print("\n" + "=" * 60)
print("TRAFFIC SHOCK")
print("=" * 60)

print(
    json.dumps(
        shock_visualization,
        indent=2,
    )
)


# ============================================================
# 19. DISPLAY DEMAND FORECAST
# ============================================================

print("\n" + "=" * 60)
print("DEMAND FORECAST")
print("=" * 60)

print(
    json.dumps(
        demand,
        indent=2,
    )
)


# ============================================================
# 20. OUTPUT FILES
# ============================================================

print("\n" + "=" * 60)
print("OUTPUT FILES")
print("=" * 60)

print(f"Dashboard : {OUTPUT_FILE}")
print(f"QUBO      : {QUBO_OUTPUT_FILE}")


# ============================================================
# 21. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)