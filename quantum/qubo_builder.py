from dataclasses import dataclass
from typing import List, Mapping

import numpy as np

from config import (
    JUNCTIONS,
    QUBO_PENALTY,
    OBJECTIVE_WEIGHTS,
)


@dataclass
class QUBOModel:
    variables: List[str]
    matrix: np.ndarray
    linear: np.ndarray
    constant: float
    metadata: dict

    def evaluate(self, bits) -> float:
        x = np.asarray(bits, dtype=float)

        return float(
            self.constant
            + self.linear @ x
            + x @ self.matrix @ x
        )


# ---------------------------------------------------------
# SIGNAL PLANS
# ---------------------------------------------------------

PLAN_DURATION = {
    "P1": 30.0,
    "P2": 45.0,
    "P3": 60.0,
}

PLAN_RELIEF = {
    "P1": 0.67,
    "P2": 1.00,
    "P3": 1.33,
}


# ---------------------------------------------------------
# TRAFFIC SHOCK LEVELS
# ---------------------------------------------------------

SHOCK_LEVEL = {
    "NORMAL": 0.0,
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
    "CRITICAL": 1.00,
}


def variable_names() -> List[str]:

    return [
        f"{junction}_{plan}"
        for junction in JUNCTIONS
        for plan in ("P1", "P2", "P3")
    ]


def _get_shock_value(value) -> float:

    if isinstance(value, str):

        return SHOCK_LEVEL.get(
            value.upper(),
            0.0
        )

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# ---------------------------------------------------------
# ADAPTIVE PLAN FEATURES
# ---------------------------------------------------------

def _plan_features(
    junction,
    plan,
    context
):

    state = context.get(
        junction,
        {}
    )

    vehicles = max(
        float(state.get("vehicles", 0)),
        0.0
    )

    queue = max(
        float(state.get("queue", 0)),
        0.0
    )

    waiting = max(
        float(state.get("waiting", 0)),
        0.0
    )

    capacity = max(
        float(state.get("capacity", 50)),
        1.0
    )

    congestion = max(
        float(
            state.get(
                "congestion",
                vehicles / capacity
            )
        ),
        0.0
    )

    shock = _get_shock_value(
        state.get("shock", 0)
    )

    emergency_delay = max(
        float(
            state.get(
                "emergency_delay",
                0
            )
        ),
        0.0
    )

    duration = PLAN_DURATION[plan]

    relief = PLAN_RELIEF[plan]

    # -----------------------------------------------------
    # DEMAND
    # -----------------------------------------------------

    demand_ratio = min(
        vehicles / capacity,
        2.0
    )

    queue_ratio = min(
        queue / capacity,
        2.0
    )

    # -----------------------------------------------------
    # PLAN SUITABILITY
    #
    # Low demand:
    #     shorter green preferred
    #
    # Medium demand:
    #     PLAN_2 preferred
    #
    # Heavy demand:
    #     PLAN_3 preferred
    # -----------------------------------------------------

    if demand_ratio < 0.45:

        ideal_duration = 30.0

    elif demand_ratio < 0.85:

        ideal_duration = 45.0

    else:

        ideal_duration = 60.0

    duration_distance = abs(
        duration - ideal_duration
    )

    duration_penalty = (
        duration_distance
        * (2.5 + 3.0 * demand_ratio)
    )

    # -----------------------------------------------------
    # QUEUE PRESSURE
    # -----------------------------------------------------

    queue_pressure = (
        queue_ratio
        * 30.0
    )

    # Longer plans help when queue is high.
    queue_relief = (
        queue_ratio
        * relief
        * 18.0
    )

    # -----------------------------------------------------
    # WAITING
    # -----------------------------------------------------

    estimated_waiting = (
        waiting
        / max(relief, 0.50)
    )

    # Heavy traffic makes waiting more important.
    estimated_waiting += (
        vehicles
        * demand_ratio
        * 0.8
    )

    # -----------------------------------------------------
    # THROUGHPUT
    # -----------------------------------------------------

    service_capacity = (
        vehicles
        * relief
    )

    throughput_gain = (
        service_capacity
        * (
            0.5
            + 0.8 * demand_ratio
            + 0.5 * queue_ratio
        )
    )

    # Throughput is a benefit,
    # therefore it enters the objective negatively.
    throughput_cost = -throughput_gain

    # -----------------------------------------------------
    # CONGESTION
    # -----------------------------------------------------

    congestion_cost = (
        congestion
        * 25.0
        / max(relief, 0.50)
    )

    # -----------------------------------------------------
    # SPILLBACK
    # -----------------------------------------------------

    spill_pressure = max(
        0.0,
        queue - capacity * 0.50
    )

    spillback = (
        spill_pressure
        / max(relief, 0.50)
    )

    spillback *= (
        1.0
        + shock
    )

    # -----------------------------------------------------
    # SHOCK RESPONSE
    # -----------------------------------------------------

    shock_cost = (
        shock
        * vehicles
        * 1.5
        / max(relief, 0.50)
    )

    # Critical/high shocks benefit from
    # longer clearance time.
    shock_duration_penalty = 0.0

    if shock >= 0.75:

        if plan == "P1":
            shock_duration_penalty = 30.0

        elif plan == "P2":
            shock_duration_penalty = 10.0

        else:
            shock_duration_penalty = -20.0

    elif shock >= 0.50:

        if plan == "P1":
            shock_duration_penalty = 15.0

        elif plan == "P2":
            shock_duration_penalty = 4.0

        else:
            shock_duration_penalty = -8.0

    # -----------------------------------------------------
    # EMERGENCY
    # -----------------------------------------------------

    emergency_cost = (
        emergency_delay
        / max(relief, 0.50)
    )

    if emergency_delay > 0:

        if plan == "P1":
            emergency_cost += 30.0

        elif plan == "P2":
            emergency_cost += 8.0

        else:
            emergency_cost -= 20.0

    # -----------------------------------------------------
    # FUEL
    # -----------------------------------------------------

    fuel = (
        estimated_waiting * 0.035
        + queue * 0.012
        + vehicles * 0.004
        + congestion * vehicles * 0.006
    )

    # -----------------------------------------------------
    # CO2
    # -----------------------------------------------------

    co2 = (
        estimated_waiting * 0.09
        + queue * 0.025
        + vehicles * 0.011
        + congestion * vehicles * 0.015
    )

    return {

        "duration": duration,

        "relief": relief,

        "waiting": estimated_waiting,

        "queue": queue_pressure,

        "throughput": throughput_cost,

        "congestion": congestion_cost,

        "spillback": spillback,

        "emergency_delay": emergency_cost,

        "fuel": max(
            fuel,
            0.0
        ),

        "co2": max(
            co2,
            0.0
        ),

        "duration_penalty":
            duration_penalty,

        "queue_relief":
            queue_relief,

        "shock_cost":
            shock_cost,

        "shock_duration_penalty":
            shock_duration_penalty,

        "demand_ratio":
            demand_ratio,

        "queue_ratio":
            queue_ratio,

        "shock":
            shock,
    }


# ---------------------------------------------------------
# BUILD QUBO
# ---------------------------------------------------------

def build_qubo(
    context: Mapping[str, dict],
    previous_plans: Mapping[str, str] | None = None,
    penalty: float = QUBO_PENALTY
) -> QUBOModel:

    names = variable_names()

    n = len(names)

    linear = np.zeros(
        n,
        dtype=float
    )

    matrix = np.zeros(
        (n, n),
        dtype=float
    )

    constant = 0.0

    # -----------------------------------------------------
    # PLAN COSTS
    # -----------------------------------------------------

    for i, name in enumerate(names):

        junction, plan = name.split("_")

        features = _plan_features(
            junction,
            plan,
            context
        )

        cost = (

            OBJECTIVE_WEIGHTS["waiting"]
            * features["waiting"]

            + OBJECTIVE_WEIGHTS["queue"]
            * features["queue"]

            + OBJECTIVE_WEIGHTS["throughput"]
            * features["throughput"]

            + OBJECTIVE_WEIGHTS["congestion"]
            * features["congestion"]

            + OBJECTIVE_WEIGHTS["spillback"]
            * features["spillback"]

            + OBJECTIVE_WEIGHTS["emergency_delay"]
            * features["emergency_delay"]

            + OBJECTIVE_WEIGHTS["fuel"]
            * features["fuel"]

            + OBJECTIVE_WEIGHTS["co2"]
            * features["co2"]

        )

        # -------------------------------------------------
        # ADAPTIVE DURATION
        # -------------------------------------------------

        cost += (
            features["duration_penalty"]
        )

        # Queue relief reduces objective.
        cost -= (
            features["queue_relief"]
        )

        # -------------------------------------------------
        # SHOCK RESPONSE
        # -------------------------------------------------

        cost += (
            features["shock_cost"]
        )

        cost += (
            features[
                "shock_duration_penalty"
            ]
        )

        # -------------------------------------------------
        # PREVIOUS SIGNAL PLAN
        # -------------------------------------------------

        if previous_plans:

            previous = previous_plans.get(
                junction
            )

            current_name = plan.replace(
                "P",
                "PLAN_"
            )

            if (
                previous is not None
                and previous != current_name
            ):

                cost += (
                    OBJECTIVE_WEIGHTS[
                        "signal_change"
                    ]
                )

        # -------------------------------------------------
        # Store cost
        # -------------------------------------------------

        linear[i] += cost

    # ---------------------------------------------------------
    # EXACTLY ONE PLAN PER JUNCTION
    #
    # (x1 + x2 + x3 - 1)^2
    # ---------------------------------------------------------

    plans_per_junction = 3

    number_of_junctions = len(
        JUNCTIONS
    )

    for block in range(
        number_of_junctions
    ):

        start = (
            block
            * plans_per_junction
        )

        indices = [
            start + k
            for k in range(
                plans_per_junction
            )
        ]

        # Linear penalty
        for i in indices:

            linear[i] += penalty

        # Pairwise penalty
        for a in range(
            plans_per_junction
        ):

            for b in range(
                a + 1,
                plans_per_junction
            ):

                i = indices[a]

                j = indices[b]

                matrix[i, j] += (
                    -penalty
                )

                matrix[j, i] += (
                    -penalty
                )

        constant += penalty

    # ---------------------------------------------------------
    # METADATA
    # ---------------------------------------------------------

    metadata = {

        "objective_weights":
            dict(OBJECTIVE_WEIGHTS),

        "penalty":
            penalty,

        "n_variables":
            n,

        "n_junctions":
            number_of_junctions,

        "plans_per_junction":
            plans_per_junction,

        "plan_durations":
            dict(PLAN_DURATION),

        "description":
            "Adaptive multi-objective QUBO "
            "for urban traffic signal timing.",

        "objectives": [

            "waiting_time",

            "queue_length",

            "throughput",

            "congestion",

            "spillback",

            "emergency_delay",

            "fuel",

            "co2",

        ],

        "adaptive_inputs": [

            "vehicles",

            "queue",

            "waiting",

            "capacity",

            "congestion",

            "shock",

            "emergency_delay",

            "previous_signal_plan",

        ],

        "plan_logic": {

            "PLAN_1":
                "30s - low demand",

            "PLAN_2":
                "45s - medium demand",

            "PLAN_3":
                "60s - high demand",

        },

    }

    return QUBOModel(
        names,
        matrix,
        linear,
        constant,
        metadata
    )


def evaluate_solution(
    model: QUBOModel,
    bits
) -> float:

    return model.evaluate(bits)