import json
import networkx as nx
from san.traffic_adapter import load_and_adapt
from san.emergency import EmergencyVehicle
from san.routing import candidate_routes,select_best_route
from san.corridor import (
    build_green_corridor,
    junction_states,
    clearance_check,
    route_clearance_check
)
from san.recovery import recovery_plan
from san.emissions import estimate_fuel_and_co2
from san.dashboard_output import build_dashboard_output

def build_demo_network():
    g=nx.DiGraph()
    roads=[
        ("J1","J2",2,20,.20,3,False),("J2","J3",2,20,.85,12,False),
        ("J3","J5",3,20,.75,10,False),("J1","J4",2,20,.30,4,False),
        ("J4","J3",2,20,.20,2,False),("J4","J5",3,20,.25,3,False),
        ("J2","J4",2,20,.40,5,False)]
    for u,v,d,s,c,q,closed in roads:
        g.add_edge(u,v,distance=d,speed=s,congestion=c,queue=q,capacity=60,closed=closed)
    return g
def apply_traffic_state(graph, traffic_state):

    for junction, values in traffic_state["junctions"].items():

        congestion = min(
            float(values["congestion"]) +
            0.5 * float(values["shock_intensity"]),
            1.0
        )

        queue = float(values["queue"])
        speed = max(float(values["speed"]), 1)

        for _, _, data in graph.out_edges(junction, data=True):

            data["queue"] = queue
            data["speed"] = speed
            data["congestion"] = congestion
            data["capacity"] = values["capacity"]

    return graph

def run_demo():

    # 1. Build the road network
    graph = build_demo_network()

    # 2. Load Shree's traffic prediction
    traffic_state = load_and_adapt(
        "data/dashboard_traffic.json",
        "data/prediction_for_qubo.json"
    )

    # 3. Apply Shree's traffic data to our road network
    graph = apply_traffic_state(
        graph,
        traffic_state
    )

    # 4. Create emergency vehicle
    ambulance = EmergencyVehicle(
        "AMB01",
        "J1",
        "J5",
        "HIGH",
        "AMBULANCE",
        20
    )

    # 5. Find possible emergency routes
    routes = candidate_routes(
        graph,
        ambulance.start,
        ambulance.destination,
        3
    )

    # 6. Select the best route
    best = select_best_route(routes)

    route = best["route"] if best else []

    # 7. Create Green Corridor
    corridor = build_green_corridor(
        route,
        ambulance.priority
    )

    # 8. Set junction signals
    junctions = junction_states(route)

    # 9. Check clearance
    clearance = route_clearance_check(
    route,
    traffic_state
)
    # 10. Recovery after ambulance passes
    recovery = recovery_plan(route)

    # 11. Estimate fuel and CO2
    fuel_co2 = estimate_fuel_and_co2(
        30,
        5,
        10
    )

    # 12. Create dashboard output
    result = build_dashboard_output(
        ambulance,
        route,
        corridor["status"],
        junctions,
        clearance,
        recovery,
        fuel_co2,
        routes
    )

    # Include Shree's traffic information
    result["traffic_input"] = traffic_state

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_demo()