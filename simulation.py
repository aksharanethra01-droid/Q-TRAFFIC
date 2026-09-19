"""
Q-TRAFFIC Custom Traffic Simulation

Generates simulation results for:
- Fixed-Time
- Adaptive
- Quantum-Hybrid QAOA
- Emergency Green Corridor
- Fuel and CO2 estimation

The Quantum-Hybrid controller uses Nila's
QUBO + QAOA optimizer directly.

This is a prototype simulation, not live traffic data.
"""

from data.scenarios import apply_scenario

from baseline.fixed_time import fixed_time_signal
from baseline.adaptive import adaptive_signal
from baseline.metrics import calculate_metrics
from baseline.environment import calculate_environment_metrics

from prediction.congestion import predict_congestion

from quantum.signal_optimizer import (
    build_optimization_input
)

from quantum.qaoa_optimizer import (
    optimize_with_qaoa
)

from emergency.green_corridor import (
    build_emergency_plan
)


# ============================================================
# SIMULATE A SIGNAL CONTROLLER
# ============================================================

def simulate_controller(
    junctions,
    signal_plan
):
    """
    Simulate traffic response to a signal plan.

    The signal timings supplied here are the actual timings
    selected by the controller being evaluated.
    """

    waiting_times = []
    queues = []
    throughput = 0

    for junction, data in junctions.items():

        queue = data["queue"]
        vehicles = data["vehicles"]

        # Safely obtain the signal plan.
        plan = signal_plan.get(
            junction,
            {
                "green": 30,
                "red": 30
            }
        )

        green = plan.get(
            "green",
            30
        )

        # Keep the value inside a valid range.
        green = max(
            0,
            min(
                60,
                float(green)
            )
        )

        reduction_factor = (
            green / 60
        )

        # ----------------------------------------------------
        # Queue simulation
        # ----------------------------------------------------

        simulated_queue = max(
            0,
            round(
                queue
                * (
                    1
                    - 0.35
                    * reduction_factor
                )
            )
        )

        # ----------------------------------------------------
        # Waiting-time simulation
        # ----------------------------------------------------

        waiting_time = max(
            0,
            round(
                queue * 2.0
                - green * 0.5,
                2
            )
        )

        # ----------------------------------------------------
        # Throughput simulation
        # ----------------------------------------------------

        processed = min(
            vehicles,
            round(
                vehicles
                * reduction_factor
            )
        )

        queues.append(
            simulated_queue
        )

        waiting_times.append(
            waiting_time
        )

        throughput += processed

    # ========================================================
    # TRAFFIC METRICS
    # ========================================================

    metrics = calculate_metrics(
        waiting_times=waiting_times,
        queues=queues,
        throughput=throughput
    )

    # ========================================================
    # ENVIRONMENTAL METRICS
    # ========================================================

    environment = calculate_environment_metrics(
        waiting_time=metrics[
            "average_waiting_time"
        ],
        total_queue=metrics[
            "total_queue"
        ],
        throughput=metrics[
            "throughput"
        ]
    )

    metrics["fuel"] = environment[
        "fuel"
    ]

    metrics["co2"] = environment[
        "co2"
    ]

    return metrics


# ============================================================
# APPLY EMERGENCY PRIORITY
# ============================================================

def apply_emergency_priority(
    signal_plan,
    emergency_plan
):
    """
    Apply emergency green-corridor priority
    to an existing signal plan.

    Only the junctions on the emergency route
    receive emergency priority.
    """

    if emergency_plan is None:
        return signal_plan

    emergency_signal_plan = {}

    # Copy the existing QAOA signal plan.
    for junction, plan in signal_plan.items():

        emergency_signal_plan[
            junction
        ] = plan.copy()

    # Override only the emergency route.
    for junction in emergency_plan.get(
        "route",
        []
    ):

        if junction in emergency_signal_plan:

            emergency_signal_plan[
                junction
            ] = {

                "green": 50,

                "red": 10,

                "plan": "EMERGENCY_GREEN",

                "emergency_priority": True
            }

    return emergency_signal_plan


# ============================================================
# EMERGENCY TRAVEL TIME
# ============================================================

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

        if junction not in junctions:
            continue

        data = junctions[
            junction
        ]

        speed = max(
            data["speed"],
            5
        )

        plan = signal_plan.get(
            junction,
            {
                "green": 30
            }
        )

        green = plan.get(
            "green",
            30
        )

        # Basic movement time.
        travel_time = (
            60 / speed
        )

        # Signal delay.
        signal_delay = max(
            0,
            30
            - green * 0.5
        )

        total_time += (
            travel_time
            + signal_delay
        )

    return round(
        total_time,
        2
    )


# ============================================================
# CONVERT QAOA PLAN TO DASHBOARD-FRIENDLY FORMAT
# ============================================================

def normalize_qaoa_signal_plan(
    signal_plan
):
    """
    Normalize Nila's QAOA signal-plan output.

    Expected input:

        {
            "J1": {
                "green": 30,
                "red": 30,
                "plan": "PLAN_1"
            }
        }

    The function guarantees that every junction
    has green, red and plan fields.
    """

    normalized = {}

    for junction, plan in (
        signal_plan or {}
    ).items():

        if not isinstance(
            plan,
            dict
        ):
            continue

        green = plan.get(
            "green",
            30
        )

        red = plan.get(
            "red",
            30
        )

        plan_name = plan.get(
            "plan",
            "PLAN_1"
        )

        normalized[
            junction
        ] = {

            "green": int(
                green
            ),

            "red": int(
                red
            ),

            "plan": plan_name,

            "quantum_bit": plan.get(
                "quantum_bit",
                0
            )
        }

    return normalized


# ============================================================
# MAIN SIMULATION
# ============================================================

def run_simulation(
    location,
    scenario
):

    # ========================================================
    # 1. APPLY SCENARIO
    # ========================================================

    scenario_result = apply_scenario(
        location,
        scenario
    )

    junctions = scenario_result[
        "junctions"
    ]

    event = scenario_result[
        "event"
    ]

    # ========================================================
    # 2. EMERGENCY GREEN CORRIDOR
    # ========================================================

    emergency_plan = None

    if scenario == "Ambulance Emergency":

        emergency_plan = build_emergency_plan(
            vehicle="AMB01",
            start="J1",
            destination="J4",
            priority="HIGH"
        )

    # ========================================================
    # 3. FIXED-TIME CONTROLLER
    # ========================================================

    fixed_plan = fixed_time_signal()

    fixed_metrics = simulate_controller(
        junctions,
        fixed_plan
    )

    # ========================================================
    # 4. ADAPTIVE CONTROLLER
    # ========================================================

    adaptive_plan = adaptive_signal(
        junctions
    )

    adaptive_metrics = simulate_controller(
        junctions,
        adaptive_plan
    )

    # ========================================================
    # 5. CONGESTION PREDICTION
    # ========================================================

    predictions = predict_congestion(
        junctions
    )

    # ========================================================
    # 6. OPTIMIZATION INPUT
    # ========================================================

    emergency_junctions = []

    if emergency_plan is not None:

        emergency_junctions = (
            emergency_plan.get(
                "route",
                []
            )
        )

    optimization_input = (
        build_optimization_input(
            junctions,
            predictions,
            emergency_junctions
        )
    )

    # ========================================================
    # 7. NILA QUBO + QAOA
    # ========================================================

    qaoa_result = optimize_with_qaoa(
        junctions,
        emergency_junctions=emergency_junctions,
        shots=512
    )

    # ========================================================
    # 8. EXTRACT ACTUAL QAOA SIGNAL PLAN
    # ========================================================

    qaoa_signal_plan = normalize_qaoa_signal_plan(
        qaoa_result.get(
            "signal_plan",
            {}
        )
    )

    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    # If for any reason QAOA does not return all
    # junctions, use a neutral 30/30 plan for
    # the missing junctions.

    for junction in junctions:

        if junction not in qaoa_signal_plan:

            qaoa_signal_plan[
                junction
            ] = {

                "green": 30,

                "red": 30,

                "plan": "PLAN_1",

                "quantum_bit": 0
            }

    # ========================================================
    # 9. APPLY EMERGENCY GREEN CORRIDOR
    # ========================================================

    optimized_plan = (
        apply_emergency_priority(
            qaoa_signal_plan,
            emergency_plan
        )
    )

    # ========================================================
    # 10. ACTUAL QAOA-DRIVEN SIMULATION
    # ========================================================

    optimized_metrics = simulate_controller(
        junctions,
        optimized_plan
    )

    # ========================================================
    # 11. EMERGENCY TRAVEL TIME
    # ========================================================

    emergency_travel_time = None

    if emergency_plan is not None:

        emergency_travel_time = (
            estimate_emergency_travel_time(
                emergency_plan[
                    "route"
                ],
                junctions,
                optimized_plan
            )
        )

        optimized_metrics[
            "emergency_travel_time"
        ] = emergency_travel_time

    # ========================================================
    # 12. QAOA RESULT SUMMARY
    # ========================================================

    quantum_result = (
        qaoa_result.get(
            "quantum_result",
            {}
        )
    )

    qaoa_summary = {

        "method": quantum_result.get(
            "method"
        ),

        "status": quantum_result.get(
            "status"
        ),

        "p": quantum_result.get(
            "p"
        ),

        "best_bitstring": quantum_result.get(
            "best_bitstring"
        ),

        "selected_plans": quantum_result.get(
            "selected_plans",
            {}
        ),

        "objective_value": quantum_result.get(
            "objective_value"
        ),

        "circuit_depth": quantum_result.get(
            "circuit_depth"
        ),

        "execution_time": quantum_result.get(
            "execution_time"
        ),

        "message": quantum_result.get(
            "message"
        )
    }

    # ========================================================
    # 13. FINAL RESULT
    # ========================================================

    return {

        "location": location,

        "scenario": scenario,

        "junctions": junctions,

        "event": event,

        "emergency": emergency_plan,

        "predictions": predictions,

        "optimization_input": optimization_input,

        # ----------------------------------------------------
        # QAOA
        # ----------------------------------------------------

        "qaoa": {

            "result": qaoa_summary,

            "signal_plan": qaoa_signal_plan,

            "applied_signal_plan": optimized_plan
        },

        # ----------------------------------------------------
        # CONTROLLERS
        # ----------------------------------------------------

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

                # IMPORTANT:
                # This is now the ACTUAL Nila QAOA plan,
                # not quantum.signal_optimizer's prototype plan.

                "signal_plan": optimized_plan,

                "metrics": optimized_metrics
            }
        },

        # ----------------------------------------------------
        # DIRECT METRICS
        # ----------------------------------------------------

        "metrics": {

            "Fixed-Time": fixed_metrics,

            "Adaptive": adaptive_metrics,

            "Quantum-Hybrid Prototype": optimized_metrics
        }
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = run_simulation(
        "Coimbatore",
        "Ambulance Emergency"
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "Q-TRAFFIC SIMULATION"
    )

    print(
        "=" * 70
    )

    print(
        "Location :",
        result[
            "location"
        ]
    )

    print(
        "Scenario :",
        result[
            "scenario"
        ]
    )

    # ========================================================
    # EVENT
    # ========================================================

    print(
        "\nEVENT"
    )

    print(
        "-" * 70
    )

    print(
        "Type :",
        result[
            "event"
        ]["type"]
    )

    # ========================================================
    # EMERGENCY
    # ========================================================

    if result[
        "emergency"
    ]:

        emergency = result[
            "emergency"
        ]

        print(
            "\nEMERGENCY GREEN CORRIDOR"
        )

        print(
            "-" * 70
        )

        print(
            "Vehicle     :",
            emergency[
                "vehicle"
            ]
        )

        print(
            "Start       :",
            emergency[
                "start"
            ]
        )

        print(
            "Destination :",
            emergency[
                "destination"
            ]
        )

        print(
            "Priority    :",
            emergency[
                "priority"
            ]
        )

        print(
            "Route       :",
            " -> ".join(
                emergency[
                    "route"
                ]
            )
        )

        print(
            "Status      :",
            emergency[
                "status"
            ]
        )

    # ========================================================
    # QAOA
    # ========================================================

    print(
        "\nNILA QAOA"
    )

    print(
        "-" * 70
    )

    qaoa = result[
        "qaoa"
    ]

    qaoa_result = qaoa[
        "result"
    ]

    print(
        "Method          :",
        qaoa_result[
            "method"
        ]
    )

    print(
        "Status          :",
        qaoa_result[
            "status"
        ]
    )

    print(
        "Bitstring       :",
        qaoa_result[
            "best_bitstring"
        ]
    )

    print(
        "Selected Plans  :",
        qaoa_result[
            "selected_plans"
        ]
    )

    print(
        "Objective Value :",
        qaoa_result[
            "objective_value"
        ]
    )

    # ========================================================
    # CONTROLLER RESULTS
    # ========================================================

    print(
        "\nCONTROLLER RESULTS"
    )

    print(
        "-" * 70
    )

    for controller, data in result[
        "controllers"
    ].items():

        print(
            f"\n{controller}"
        )

        print(
            "-" * 40
        )

        for metric, value in data[
            "metrics"
        ].items():

            print(
                f"  {metric}: {value}"
            )

    # ========================================================
    # QAOA SIGNAL PLANS
    # ========================================================

    print(
        "\nQAOA SIGNAL PLANS"
    )

    print(
        "-" * 70
    )

    for junction, plan in qaoa[
        "signal_plan"
    ].items():

        print(
            f"{junction} : "
            f"Green={plan['green']} sec | "
            f"Red={plan['red']} sec | "
            f"Plan={plan.get('plan', 'N/A')}"
        )

    # ========================================================
    # ACTUAL APPLIED SIGNAL PLANS
    # ========================================================

    print(
        "\nAPPLIED SIGNAL PLANS"
    )

    print(
        "-" * 70
    )

    for junction, plan in qaoa[
        "applied_signal_plan"
    ].items():

        print(
            f"{junction} : "
            f"Green={plan['green']} sec | "
            f"Red={plan['red']} sec | "
            f"Plan={plan.get('plan', 'N/A')}"
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "SIMULATION COMPLETE"
    )

    print(
        "=" * 70
    )