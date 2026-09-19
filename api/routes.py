from fastapi import APIRouter

from api.schemas import (
    ScenarioRequest,
    PredictionRequest,
    EmergencyRouteRequest,
)

from data.scenarios import apply_scenario

# SHREE TRAFFIC PREDICTION INTEGRATION
from integration.shree_prediction_adapter import predict_live_traffic

from emergency.san_integration import run_san_emergency

from quantum.qaoa_optimizer import optimize_with_qaoa

from audit.blockchain import AuditBlockchain

from simulation import run_simulation


router = APIRouter()


# =========================================================
# GLOBAL STATE
# =========================================================

audit_store = AuditBlockchain()

latest_result = {}


# =========================================================
# SHREE PREDICTION HELPER
# =========================================================

def run_shree_prediction(traffic_state):
    """
    Run Shree's traffic prediction module on the current
    junction traffic state.

    Output:
        {
            "J1": {
                "1min": ...,
                "3min": ...,
                "5min": ...
            },
            ...
        }
    """

    return predict_live_traffic(
        traffic_state,
        demand_multiplier=1.0,
    )


def attach_shree_predictions(traffic_state):
    """
    Attach Shree's predictions directly to each junction.

    This keeps the prediction information available to
    downstream QAOA/QUBO and dashboard layers.
    """

    predictions = run_shree_prediction(traffic_state)

    enriched_state = {}

    for junction, state in traffic_state.items():

        enriched_state[junction] = dict(state)

        enriched_state[junction]["predicted"] = predictions.get(
            junction,
            {
                "1min": 0,
                "3min": 0,
                "5min": 0,
            },
        )

    return enriched_state, predictions


# =========================================================
# JSON-SAFE QAOA RESULT
# =========================================================

def qaoa_audit_summary(qaoa_result):
    """
    Convert the QAOA result into JSON-safe data.

    Qiskit objects such as QuantumCircuit cannot be returned
    directly through FastAPI.
    """

    quantum_result = qaoa_result.get(
        "quantum_result",
        {},
    )

    return {
        "bitstring": quantum_result.get("bitstring"),
        "energy": quantum_result.get("energy"),
        "counts": quantum_result.get("counts"),
        "signal_plan": qaoa_result.get(
            "signal_plan",
            {},
        ),
    }


def json_safe_qaoa_result(qaoa_result):
    """
    Complete JSON-safe representation of the QAOA result.
    """

    quantum_result = qaoa_result.get(
        "quantum_result",
        {},
    )

    return {
        "qubo": qaoa_result.get(
            "qubo",
            {},
        ),

        "quantum_result": {
            "bitstring": quantum_result.get(
                "bitstring"
            ),

            "energy": quantum_result.get(
                "energy"
            ),

            "counts": quantum_result.get(
                "counts"
            ),
        },

        "signal_plan": qaoa_result.get(
            "signal_plan",
            {},
        ),

        "reference_solution": qaoa_result.get(
            "reference_solution",
            {},
        ),
    }


# =========================================================
# HEALTH
# =========================================================

@router.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Q-TRAFFIC API",
        "san_integration": "enabled",
        "qaoa_integration": "enabled",
        "shree_prediction": "enabled",
        "audit_blockchain": "enabled",
    }


# =========================================================
# LOCATIONS
# =========================================================

@router.get("/locations")
def locations():

    return {
        "locations": [
            "Coimbatore",
            "Chennai",
            "Madurai",
            "Salem",
        ]
    }


# =========================================================
# SCENARIOS
# =========================================================

@router.get("/scenarios")
def scenarios():

    return {
        "scenarios": [
            "Normal Traffic",
            "School Peak",
            "Textile Festival",
            "Accident",
            "Vehicle Obstruction",
            "Ambulance Emergency",
        ]
    }


# =========================================================
# TRAFFIC PREDICTION
# =========================================================

@router.post("/traffic/prediction")
def traffic_prediction(request: PredictionRequest):

    # apply_scenario expects the location name.
    scenario_result = apply_scenario(
        request.location,
        request.scenario,
    )

    traffic_state = scenario_result["junctions"]

    # Run Shree's real prediction module.
    predictions = run_shree_prediction(
        traffic_state
    )

    return {
        "location": request.location,
        "scenario": request.scenario,
        "predictions": predictions,
        "prediction_source": "Shree traffic prediction module",
    }


# =========================================================
# EMERGENCY ROUTE
# =========================================================

@router.post("/emergency/route")
def emergency_route(request: EmergencyRouteRequest):

    # Use San's real emergency integration.
    if (
        request.vehicle == "AMB01"
        and request.start == "J1"
        and request.destination == "J5"
    ):

        result = run_san_emergency()

        audit_block = audit_store.add_decision(
            decision_type="GREEN_CORRIDOR",
            scenario="Ambulance Emergency",
            route=result.get(
                "selected_route"
            ),
            signal_plan=result.get(
                "junctions"
            ),
            metrics=result.get(
                "fuel_co2_estimate"
            ),
        )

        return {
            "emergency": result,
            "audit": audit_block,
            "audit_valid": audit_store.verify_chain(),
        }

    # Generic fallback.
    return {
        "vehicle": request.vehicle,
        "start": request.start,
        "destination": request.destination,
        "priority": request.priority,
        "status": "ROUTE_REQUEST_RECEIVED",
    }


# =========================================================
# SIGNAL OPTIMIZATION
# =========================================================

@router.post("/signal/optimize")
def signal_optimize(request: ScenarioRequest):

    scenario_result = apply_scenario(
        request.location,
        request.scenario,
    )

    traffic_state = scenario_result["junctions"]

    # Add Shree's prediction to the traffic state.
    traffic_state, predictions = attach_shree_predictions(
        traffic_state
    )

    emergency_junctions = []

    if request.scenario == "Ambulance Emergency":

        emergency_junctions = [
            "J1",
            "J2",
            "J3",
            "J4",
        ]

    # -----------------------------------------------------
    # RUN NILA'S QAOA
    # -----------------------------------------------------

    qaoa_result = optimize_with_qaoa(
        traffic_state,
        emergency_junctions=emergency_junctions,
    )

    # -----------------------------------------------------
    # AUDIT
    # -----------------------------------------------------

    audit_block = audit_store.add_decision(
        decision_type="QAOA_SIGNAL_OPTIMIZATION",
        scenario=request.scenario,
        signal_plan=qaoa_result.get(
            "signal_plan"
        ),
        metrics=qaoa_audit_summary(
            qaoa_result
        ),
    )

    return {
        "location": request.location,
        "scenario": request.scenario,

        "predictions": predictions,

        "qaoa": json_safe_qaoa_result(
            qaoa_result
        ),

        "audit": audit_block,

        "audit_valid": audit_store.verify_chain(),
    }


# =========================================================
# COMPLETE SCENARIO RUN
# =========================================================

@router.post("/scenario/run")
def scenario_run(request: ScenarioRequest):

    global latest_result

    # -----------------------------------------------------
    # 1. RUN CUSTOM TRAFFIC SIMULATION
    # -----------------------------------------------------

    simulation_result = run_simulation(
        request.location,
        request.scenario,
    )

    # -----------------------------------------------------
    # 2. SHREE TRAFFIC PREDICTION
    # -----------------------------------------------------

    traffic_state = simulation_result["junctions"]

    enriched_traffic_state, predictions = (
        attach_shree_predictions(
            traffic_state
        )
    )

    # -----------------------------------------------------
    # 3. EMERGENCY INTEGRATION
    # -----------------------------------------------------

    emergency_result = None

    if request.scenario == "Ambulance Emergency":

        emergency_result = run_san_emergency()

    # -----------------------------------------------------
    # 4. PREPARE QAOA INPUT
    # -----------------------------------------------------

    emergency_junctions = []

    if emergency_result:

        selected_route = emergency_result.get(
            "selected_route",
            [],
        )

        emergency_junctions = [
            junction
            for junction in selected_route
            if junction in enriched_traffic_state
        ]

    # -----------------------------------------------------
    # 5. RUN NILA'S QAOA
    # -----------------------------------------------------

    qaoa_result = optimize_with_qaoa(
        enriched_traffic_state,
        emergency_junctions=emergency_junctions,
    )

    # -----------------------------------------------------
    # 6. AUDIT QAOA DECISION
    # -----------------------------------------------------

    qaoa_summary = qaoa_audit_summary(
        qaoa_result
    )

    audit_block = audit_store.add_decision(
        decision_type="SCENARIO_OPTIMIZATION",
        scenario=request.scenario,

        route=(
            emergency_result.get(
                "selected_route"
            )
            if emergency_result
            else None
        ),

        signal_plan=qaoa_result.get(
            "signal_plan"
        ),

        metrics=qaoa_summary,
    )

    # -----------------------------------------------------
    # 7. JSON-SAFE CONTROLLERS
    # -----------------------------------------------------

    controllers = simulation_result.get(
        "controllers",
        {},
    )

    # -----------------------------------------------------
    # 8. FINAL API RESULT
    # -----------------------------------------------------

    latest_result = {

        "location": simulation_result.get(
            "location"
        ),

        "scenario": simulation_result.get(
            "scenario"
        ),

        # Current traffic + Shree predictions.
        "junctions": enriched_traffic_state,

        "event": simulation_result.get(
            "event"
        ),

        # Shree prediction output.
        "predictions": predictions,

        # San emergency output.
        "emergency": emergency_result,

        # Existing simulation optimization input.
        "optimization_input": simulation_result.get(
            "optimization_input",
            {},
        ),

        # QAOA result.
        "qaoa": json_safe_qaoa_result(
            qaoa_result
        ),

        # Classical + hybrid controllers.
        "controllers": controllers,

        # Metrics.
        "metrics": {
            name: controller.get(
                "metrics",
                {},
            )
            for name, controller
            in controllers.items()
        },

        # Audit.
        "audit": audit_block,

        "audit_valid": audit_store.verify_chain(),

        # Integration information.
        "integration": {
            "shree_prediction": "connected",
            "san_emergency": (
                "connected"
                if emergency_result
                else "not_required"
            ),
            "nila_qaoa": "connected",
            "audit": "connected",
        },
    }

    return latest_result


# =========================================================
# DASHBOARD STATE
# =========================================================

@router.get("/dashboard/state")
def dashboard_state():

    if not latest_result:

        return {
            "status": "no_simulation_run",
            "message": "Run /scenario/run first.",
        }

    return latest_result


# =========================================================
# METRICS
# =========================================================

@router.get("/metrics")
def metrics():

    if not latest_result:

        return {
            "status": "no_simulation_run",
            "metrics": {},
        }

    controllers = latest_result.get(
        "controllers",
        {},
    )

    return {
        "location": latest_result.get(
            "location"
        ),

        "scenario": latest_result.get(
            "scenario"
        ),

        "metrics": {
            name: controller.get(
                "metrics",
                {},
            )
            for name, controller
            in controllers.items()
        },
    }


# =========================================================
# AUDIT
# =========================================================

@router.get("/audit")
def audit():

    return {
        "chain": audit_store.get_chain(),
        "valid": audit_store.verify_chain(),
        "blocks": len(
            audit_store.get_chain()
        ),
    }


# =========================================================
# ROOT
# =========================================================

@router.get("/")
def root():

    return {
        "service": "Q-TRAFFIC",

        "description": (
            "Quantum-Enhanced Adaptive "
            "Urban Traffic Optimization"
        ),

        "status": "running",
    }