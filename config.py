from pathlib import Path

JUNCTIONS = ["J1", "J2", "J3", "J4"]
SIGNAL_PLANS = {"PLAN_1": 30, "PLAN_2": 45, "PLAN_3": 60}
PLAN_ORDER = list(SIGNAL_PLANS)
QAOA_DEPTH = 2
QUBO_PENALTY = 80.0
ROLLING_HORIZON_SECONDS = 60
LOCATION_DEFAULT = "Coimbatore"
LOCATIONS = {
    "Coimbatore": {"traffic_multiplier": 1.00, "peak_multiplier": 1.25, "event_intensity": 1.00, "capacity_factor": 1.00},
    "Chennai": {"traffic_multiplier": 1.25, "peak_multiplier": 1.40, "event_intensity": 1.15, "capacity_factor": 0.92},
    "Madurai": {"traffic_multiplier": 0.92, "peak_multiplier": 1.18, "event_intensity": 0.95, "capacity_factor": 0.98},
    "Salem": {"traffic_multiplier": 0.88, "peak_multiplier": 1.12, "event_intensity": 0.90, "capacity_factor": 1.02},
}
EMERGENCY_VEHICLE = "AMB01"
EMERGENCY_ROUTE = ["J1", "J2", "J3", "J4"]
OBJECTIVE_WEIGHTS = {
    "waiting": 1.0, "queue": 1.2, "throughput": 1.5, "congestion": 1.0,
    "spillback": 1.4, "emergency_delay": 3.0, "fuel": 0.25, "co2": 0.20,
    "signal_change": 2.0,
}
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
SUMO_DIR = Path(__file__).resolve().parent / "sumo"
