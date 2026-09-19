from san.main import build_demo_network, apply_traffic_state
from san.traffic_adapter import load_and_adapt
from san.emergency import EmergencyVehicle
from san.routing import candidate_routes, select_best_route
from san.corridor import (
    build_green_corridor,
    junction_states,
    route_clearance_check,
)
from san.recovery import recovery_plan
from san.emissions import estimate_fuel_and_co2
from san.dashboard_output import build_dashboard_output


def run_san_emergency(
    vehicle_id="AMB01",
    start="J1",
    destination="J5",
    priority="HIGH",
):
    """
    Run San's emergency Green Corridor workflow
    for integration with the Q-TRAFFIC API.
    """

    # 1. Load traffic + prediction data
    traffic_state = load_and_adapt(
        "data/dashboard_traffic.json",
        "data/prediction_for_qubo.json",
    )

    # 2. Build the road network
    graph = build_demo_network()

    # 3. Apply traffic prediction/shock information
    graph = apply_traffic_state(
        graph,
        traffic_state,
    )

    # 4. Create emergency vehicle
    ambulance = EmergencyVehicle(
        vehicle_id,
        start,
        destination,
        priority,
        "AMBULANCE",
        20,
    )

    # 5. Generate candidate routes
    routes = candidate_routes(
        graph,
        start,
        destination,
        3,
    )

    # 6. Select best route
    best = select_best_route(routes)

    if not best:
        raise ValueError(
            f"No emergency route available from {start} to {destination}"
        )

    route = best["route"]

    # 7. Create Green Corridor
    corridor = build_green_corridor(
        route,
        priority,
    )

    # 8. Set junction signals
    junctions = junction_states(route)

    # 9. Check route clearance
    clearance = route_clearance_check(
        route,
        traffic_state,
    )

    # 10. Recovery after emergency passes
    recovery = recovery_plan(route)

    # 11. Estimate fuel and CO2
    fuel_co2 = estimate_fuel_and_co2(
        30,
        5,
        10,
    )

    # 12. Build dashboard-ready output
    result = build_dashboard_output(
        ambulance,
        route,
        corridor["status"],
        junctions,
        clearance,
        recovery,
        fuel_co2,
        routes,
    )

    # Include traffic intelligence
    result["traffic_input"] = traffic_state

    return result