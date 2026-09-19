"""
Q-TRAFFIC Custom Traffic Simulation

Generates simulation results for:
- Fixed-Time
- Adaptive
- Quantum-Hybrid Prototype
- Emergency Green Corridor
- Fuel and CO2 estimation

This is a prototype simulation, not live traffic data.
"""

from data.scenarios import apply_scenario

from baseline.fixed_time import fixed_time_signal
from baseline.adaptive import adaptive_signal
from baseline.metrics import calculate_metrics
from baseline.environment import calculate_environment_metrics

from prediction.congestion import predict_congestion

from quantum.signal_optimizer import (
    SIGNAL_PLANS,
    build_optimization_input,
    select_prototype_plan
)

from emergency.green_corridor import (
    build_emergency_plan
)


def simulate_controller(junctions, signal_plan):
    """
    Simulate traffic response to a signal plan.
    """

    waiting_times = []
    queues = []
    throughput = 0

    for junction, data in junctions.items():

        queue = data["queue"]
        vehicles = data["vehicles"]

        green = signal_plan[junction]["green"]

        reduction_factor = green / 60

        simulated_queue = max(
            0,
            round(
                queue * (1 - 0.35 * reduction_factor)
            )
        )

        waiting_time = max(
            0,
            round(
                queue * 2.0 - green * 0.5,
                2
            )
        )

        processed = min(
            vehicles,
            round(
                vehicles * reduction_factor
            )
        )

        queues.append(simulated_queue)
        waiting_times.append(waiting_time)

        throughput += processed

    # Basic traffic metrics
    metrics = calculate_metrics(
        waiting_times=waiting_times,
        queues=queues,
        throughput=throughput
    )

    # Environmental metrics
    environment = calculate_environment_metrics(
        waiting_time=metrics["average_waiting_time"],
        total_queue=metrics["total_queue"],
        throughput=metrics["throughput"]
    )

    metrics["fuel"] = environment["fuel"]
    metrics["co2"] = environment["co2"]

    return metrics


def apply_emergency_priority(
    signal_plan,
    emergency_plan
):
    """
    Apply emergency green-corridor priority
    to an existing signal plan.
    """

    if emergency_plan is None:
        return signal_plan

    emergency_signal_plan = {}

    for junction, plan in signal_plan.items():

        emergency_signal_plan[junction] = plan.copy()

    for junction in emergency_plan["route"]:

        if junction in emergency_signal_plan:

            emergency_signal_plan[junction] = {
                "green": 50,
                "red": 10,
                "plan": "EMERGENCY_GREEN"
            }

    return emergency_signal_plan


def estimate_emergency_travel_time(
    route,
    junctions,
    signal_plan
):
    """
    Estimate emergency vehicle travel time.

    This is a prototype estimate,
    not live traffic data.
    """

    total_time = 0

    for junction in route:

        data = junctions[junction]

        speed = max(
            data["speed"],
            5
        )

        green = signal_plan[junction]["green"]

        travel_time = 60 / speed

        signal_delay = max(
            0,
            30 - green * 0.5
        )

        total_time += (
            travel_time +
            signal_delay
        )

    return round(total_time, 2)


def run_simulation(location, scenario):

    # ==================================================
    # 1. APPLY SCENARIO
    # ==================================================

    scenario_result = apply_scenario(
        location,
        scenario
    )

    junctions = scenario_result["junctions"]

    event = scenario_result["event"]

    # ==================================================
    # 2. EMERGENCY GREEN CORRIDOR
    # ==================================================

    emergency_plan = None

    if scenario == "Ambulance Emergency":

        emergency_plan = build_emergency_plan(
            vehicle="AMB01",
            start="J1",
            destination="J4",
            priority="HIGH"
        )

    # ==================================================
    # 3. FIXED-TIME CONTROLLER
    # ==================================================

    fixed_plan = fixed_time_signal()

    fixed_metrics = simulate_controller(
        junctions,
        fixed_plan
    )

    # ==================================================
    # 4. ADAPTIVE CONTROLLER
    # ==================================================

    adaptive_plan = adaptive_signal(
        junctions
    )

    adaptive_metrics = simulate_controller(
        junctions,
        adaptive_plan
    )

    # ==================================================
    # 5. CONGESTION PREDICTION
    # ==================================================

    predictions = predict_congestion(
        junctions
    )

    # ==================================================
    # 6. OPTIMIZATION INPUT
    # ==================================================

    emergency_junctions = []

    if emergency_plan is not None:

        emergency_junctions = emergency_plan[
            "route"
        ]

    optimization_input = build_optimization_input(
        junctions,
        predictions,
        emergency_junctions
    )

    # ==================================================
    # 7. PROTOTYPE OPTIMIZER
    # ==================================================

    optimized_plan_names = select_prototype_plan(
        optimization_input
    )

    optimized_plan = {}

    for junction, plan_name in optimized_plan_names.items():

        optimized_plan[junction] = {
            "green": SIGNAL_PLANS[
                plan_name
            ]["green"],

            "red": SIGNAL_PLANS[
                plan_name
            ]["red"],

            "plan": plan_name
        }

    # ==================================================
    # 8. APPLY EMERGENCY GREEN CORRIDOR
    # ==================================================

    if emergency_plan is not None:

        optimized_plan = apply_emergency_priority(
            optimized_plan,
            emergency_plan
        )

    # ==================================================
    # 9. OPTIMIZED SIMULATION
    # ==================================================

    optimized_metrics = simulate_controller(
        junctions,
        optimized_plan
    )

    # ==================================================
    # 10. EMERGENCY TRAVEL TIME
    # ==================================================

    emergency_travel_time = None

    if emergency_plan is not None:

        emergency_travel_time = (
            estimate_emergency_travel_time(
                emergency_plan["route"],
                junctions,
                optimized_plan
            )
        )

        optimized_metrics[
            "emergency_travel_time"
        ] = emergency_travel_time

    # ==================================================
    # 11. FINAL RESULT
    # ==================================================

    return {

        "location": location,

        "scenario": scenario,

        "junctions": junctions,

        "event": event,

        "emergency": emergency_plan,

        "predictions": predictions,

        "optimization_input": optimization_input,

        "controllers": {

            "Fixed-Time": {

                "signal_plan": fixed_plan,

                "metrics": fixed_metrics
            },

            "Adaptive": {

                "signal_plan": adaptive_plan,

                "metrics": adaptive_metrics
            },

            "Quantum-Hybrid Prototype": {

                "signal_plan": optimized_plan,

                "metrics": optimized_metrics
            }
        }
    }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    result = run_simulation(
        "Coimbatore",
        "Ambulance Emergency"
    )

    print("\n" + "=" * 70)
    print("Q-TRAFFIC SIMULATION")
    print("=" * 70)

    print(
        "Location :",
        result["location"]
    )

    print(
        "Scenario :",
        result["scenario"]
    )

    # --------------------------------------------------
    # EVENT
    # --------------------------------------------------

    print("\nEVENT")
    print("-" * 70)

    print(
        "Type :",
        result["event"]["type"]
    )

    # --------------------------------------------------
    # EMERGENCY
    # --------------------------------------------------

    if result["emergency"]:

        emergency = result["emergency"]

        print("\nEMERGENCY GREEN CORRIDOR")
        print("-" * 70)

        print(
            "Vehicle     :",
            emergency["vehicle"]
        )

        print(
            "Start       :",
            emergency["start"]
        )

        print(
            "Destination :",
            emergency["destination"]
        )

        print(
            "Priority    :",
            emergency["priority"]
        )

        print(
            "Route       :",
            " -> ".join(
                emergency["route"]
            )
        )

        print(
            "Status      :",
            emergency["status"]
        )

    # --------------------------------------------------
    # CONTROLLER RESULTS
    # --------------------------------------------------

    print("\nCONTROLLER RESULTS")
    print("-" * 70)

    for controller, data in result[
        "controllers"
    ].items():

        print(
            f"\n{controller}"
        )

        print("-" * 40)

        for metric, value in data[
            "metrics"
        ].items():

            print(
                f"  {metric}: {value}"
            )

    # --------------------------------------------------
    # SIGNAL PLANS
    # --------------------------------------------------

    print("\nSIGNAL PLANS")
    print("-" * 70)

    optimized = result[
        "controllers"
    ][
        "Quantum-Hybrid Prototype"
    ][
        "signal_plan"
    ]

    for junction, plan in optimized.items():

        print(
            f"{junction} : "
            f"Green={plan['green']} sec | "
            f"Red={plan['red']} sec | "
            f"Plan={plan.get('plan', 'N/A')}"
        )