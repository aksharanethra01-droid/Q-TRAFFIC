from fastapi import APIRouter, HTTPException

from api.schemas import (
    ScenarioRequest,
    TrafficPredictionRequest,
    EmergencyRouteRequest,
    SignalOptimizationRequest
)

from data.locations import get_location_scenario
from data.scenarios import SCENARIOS, apply_scenario

from prediction.congestion import predict_congestion

from emergency.green_corridor import build_emergency_plan

from quantum.qaoa_optimizer import optimize_with_qaoa

from simulation import (
    simulate_controller,
    apply_emergency_priority,
    estimate_emergency_travel_time
)

from audit.blockchain import AuditBlockchain


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# AUDIT BLOCKCHAIN
# ============================================================

# Local in-memory SHA-256 audit chain.
#
# This is a lightweight tamper-evident audit mechanism.
# It is NOT a decentralized blockchain network.

audit_store = AuditBlockchain()


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "Q-TRAFFIC API"
    }


# ============================================================
# LOCATIONS
# ============================================================

@router.get("/locations")
def locations():

    return {
        "locations": [
            "Coimbatore",
            "Chennai",
            "Madurai",
            "Salem"
        ]
    }


# ============================================================
# SCENARIOS
# ============================================================

@router.get("/scenarios")
def scenarios():

    return {
        "scenarios": SCENARIOS
    }


# ============================================================
# TRAFFIC PREDICTION
# ============================================================

@router.post("/traffic/prediction")
def traffic_prediction(
    request: TrafficPredictionRequest
):

    try:

        prediction = predict_congestion(
            request.traffic_state
        )

        return {
            "status": "success",
            "prediction": prediction
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# EMERGENCY ROUTE
# ============================================================

@router.post("/emergency/route")
def emergency_route(
    request: EmergencyRouteRequest
):

    try:

        emergency_plan = build_emergency_plan(
            vehicle=request.vehicle,
            start=request.start,
            destination=request.destination,
            priority=request.priority
        )

        return {
            "status": "success",
            "emergency": emergency_plan
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# SIGNAL OPTIMIZATION
# ============================================================

@router.post("/signal/optimize")
def signal_optimize(
    request: SignalOptimizationRequest
):

    try:

        result = optimize_with_qaoa(
            traffic_state=request.traffic_state,
            emergency_junctions=request.emergency_junctions
        )

        return {
            "status": "success",

            "signal_plan":
                result["signal_plan"],

            "quantum_result": {

                "bitstring":
                    result["quantum_result"]["bitstring"],

                "energy":
                    result["quantum_result"]["energy"]
            },

            "reference_solution":
                result["reference_solution"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# COMPLETE SCENARIO PIPELINE
# ============================================================

@router.post("/scenario/run")
def scenario_run(
    request: ScenarioRequest
):

    try:

        # ----------------------------------------------------
        # 1. APPLY SCENARIO
        # ----------------------------------------------------

        scenario_result = apply_scenario(
            request.location,
            request.scenario
        )

        junctions = scenario_result["junctions"]

        event = scenario_result["event"]


        # ----------------------------------------------------
        # 2. TRAFFIC PREDICTION
        # ----------------------------------------------------

        predictions = predict_congestion(
            junctions
        )


        # ----------------------------------------------------
        # 3. EMERGENCY ROUTING
        # ----------------------------------------------------

        emergency_plan = None

        if request.scenario == "Ambulance Emergency":

            emergency_plan = build_emergency_plan(
                vehicle="AMB01",
                start="J1",
                destination="J4",
                priority="HIGH"
            )


        # ----------------------------------------------------
        # 4. GET EMERGENCY JUNCTIONS
        # ----------------------------------------------------

        emergency_junctions = []

        if emergency_plan is not None:

            emergency_junctions = (
                emergency_plan["route"]
            )


        # ----------------------------------------------------
        # 5. QUBO / QAOA
        # ----------------------------------------------------

        quantum_result = optimize_with_qaoa(

            traffic_state=junctions,

            emergency_junctions=
                emergency_junctions

        )


        # ----------------------------------------------------
        # 6. GET QUANTUM SIGNAL PLAN
        # ----------------------------------------------------

        optimized_plan = (
            quantum_result["signal_plan"]
        )


        # ----------------------------------------------------
        # 7. APPLY EMERGENCY GREEN CORRIDOR
        # ----------------------------------------------------

        if emergency_plan is not None:

            optimized_plan = (
                apply_emergency_priority(
                    optimized_plan,
                    emergency_plan
                )
            )


        # ----------------------------------------------------
        # 8. RUN TRAFFIC SIMULATION
        # ----------------------------------------------------

        metrics = simulate_controller(

            junctions,

            optimized_plan

        )


        # ----------------------------------------------------
        # 9. EMERGENCY TRAVEL TIME
        # ----------------------------------------------------

        emergency_travel_time = None

        if emergency_plan is not None:

            emergency_travel_time = (
                estimate_emergency_travel_time(

                    emergency_plan["route"],

                    junctions,

                    optimized_plan

                )
            )

            metrics[
                "emergency_travel_time"
            ] = emergency_travel_time


        # ----------------------------------------------------
        # 10. ADD DECISION TO AUDIT BLOCKCHAIN
        # ----------------------------------------------------

        audit_block = audit_store.add_decision(

            decision_type=(
                "GREEN_CORRIDOR"
                if emergency_plan is not None
                else "SIGNAL_OPTIMIZATION"
            ),

            scenario=request.scenario,

            route=(
                emergency_plan["route"]
                if emergency_plan is not None
                else None
            ),

            signal_plan=optimized_plan,

            metrics=metrics

        )


        # ----------------------------------------------------
        # 11. COMPLETE RESPONSE
        # ----------------------------------------------------

        return {

            "status": "success",

            "location":
                request.location,

            "scenario":
                request.scenario,

            "event":
                event,

            "traffic_state":
                junctions,

            "prediction":
                predictions,

            "emergency":
                emergency_plan,

            "quantum": {

                "bitstring":
                    quantum_result[
                        "quantum_result"
                    ]["bitstring"],

                "energy":
                    quantum_result[
                        "quantum_result"
                    ]["energy"],

                "reference_solution":
                    quantum_result[
                        "reference_solution"
                    ]

            },

            "signal_plan":
                optimized_plan,

            "metrics":
                metrics,

            "audit": {

                "block_index":
                    audit_block["index"],

                "hash":
                    audit_block["hash"],

                "previous_hash":
                    audit_block["previous_hash"]

            }

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ============================================================
# DASHBOARD STATE
# ============================================================

@router.get("/dashboard/state")
def dashboard_state():

    try:

        result = apply_scenario(
            "Coimbatore",
            "Normal Traffic"
        )

        return {

            "status": "success",

            "location":
                result["location"],

            "scenario":
                result["scenario"],

            "event":
                result["event"],

            "junctions":
                result["junctions"]

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ============================================================
# METRICS
# ============================================================

@router.get("/metrics")
def metrics():

    return {

        "status": "success",

        "message":
            "Metrics are calculated during scenario execution."

    }


# ============================================================
# AUDIT
# ============================================================

@router.get("/audit")
def audit():

    return {

        "status": "success",

        "chain_valid":
            audit_store.verify_chain(),

        "blocks":
            audit_store.get_chain()

    }