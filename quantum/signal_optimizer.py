"""
Q-TRAFFIC Signal Optimization Interface

This module prepares traffic information for
quantum-based signal optimization.

The actual QUBO/QAOA implementation can later
replace the prototype optimizer.
"""


SIGNAL_PLANS = {
    "PLAN_1": {
        "green": 30,
        "red": 30
    },

    "PLAN_2": {
        "green": 45,
        "red": 15
    },

    "PLAN_3": {
        "green": 50,
        "red": 10
    }
}


def generate_candidate_plans():
    """
    Return available signal timing candidates.
    """

    return SIGNAL_PLANS


def build_optimization_input(
    traffic_state,
    congestion_predictions,
    emergency_junctions=None
):
    """
    Prepare the optimization input.

    Higher congestion increases the importance
    of giving a junction more green time.

    Emergency junctions receive additional priority.
    """

    if emergency_junctions is None:
        emergency_junctions = []

    optimization_input = {}

    for junction, data in traffic_state.items():

        prediction = congestion_predictions[junction]

        queue = data["queue"]
        congestion_score = prediction["congestion_score"]

        emergency_priority = (
            1 if junction in emergency_junctions else 0
        )

        optimization_input[junction] = {

            "queue": queue,

            "congestion_score": congestion_score,

            "emergency_priority": emergency_priority,

            "capacity": data["capacity"],

            "current_signal": data["signal"]
        }

    return optimization_input


def select_prototype_plan(optimization_input):
    """
    Temporary classical selection logic.

    IMPORTANT:
    This is NOT QAOA.

    It only provides a working interface until
    the actual QUBO/QAOA implementation is connected.
    """

    optimized_plan = {}

    for junction, data in optimization_input.items():

        queue = data["queue"]
        congestion = data["congestion_score"]
        emergency = data["emergency_priority"]

        if emergency == 1:

            plan = "PLAN_3"

        elif queue >= 30 or congestion >= 0.60:

            plan = "PLAN_3"

        elif queue >= 20 or congestion >= 0.40:

            plan = "PLAN_2"

        else:

            plan = "PLAN_1"

        optimized_plan[junction] = plan

    return optimized_plan


if __name__ == "__main__":

    traffic_state = {

        "J1": {
            "vehicles": 55,
            "queue": 28,
            "speed": 18,
            "capacity": 60,
            "signal": "NS_GREEN"
        },

        "J2": {
            "vehicles": 48,
            "queue": 22,
            "speed": 20,
            "capacity": 60,
            "signal": "EW_GREEN"
        },

        "J3": {
            "vehicles": 52,
            "queue": 39,
            "speed": 13,
            "capacity": 60,
            "signal": "NS_GREEN"
        },

        "J4": {
            "vehicles": 36,
            "queue": 14,
            "speed": 25,
            "capacity": 60,
            "signal": "EW_GREEN"
        }
    }

    congestion_predictions = {

        "J1": {
            "congestion_score": 0.54
        },

        "J2": {
            "congestion_score": 0.44
        },

        "J3": {
            "congestion_score": 0.67
        },

        "J4": {
            "congestion_score": 0.29
        }
    }

    # Example: no emergency yet
    emergency_junctions = []

    optimization_input = build_optimization_input(
        traffic_state,
        congestion_predictions,
        emergency_junctions
    )

    print("\nQ-TRAFFIC OPTIMIZATION INPUT")
    print("=" * 50)

    for junction, data in optimization_input.items():

        print(
            f"{junction} | "
            f"Queue: {data['queue']} | "
            f"Congestion: {data['congestion_score']} | "
            f"Emergency: {data['emergency_priority']}"
        )

    optimized_plan = select_prototype_plan(
        optimization_input
    )

    print("\nPROTOTYPE SIGNAL PLAN")
    print("=" * 50)

    for junction, plan in optimized_plan.items():

        timing = SIGNAL_PLANS[plan]

        print(
            f"{junction} -> {plan} | "
            f"Green: {timing['green']} sec | "
            f"Red: {timing['red']} sec"
        )