"""
Q-TRAFFIC Quantum QUBO / QAOA Optimizer

Quantum-enhanced traffic signal optimization.

Each junction chooses between two signal plans:

    0 -> PLAN_1 : 30 sec green / 30 sec red
    1 -> PLAN_2 : 45 sec green / 15 sec red

The optimization objective considers:

- Queue length
- Congestion
- Emergency priority

QAOA is executed using Qiskit Aer.

This is a quantum-simulation prototype.
"""


import numpy as np

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# SIGNAL PLANS
# ============================================================

SIGNAL_PLANS = {
    0: {
        "name": "PLAN_1",
        "green": 30,
        "red": 30
    },

    1: {
        "name": "PLAN_2",
        "green": 45,
        "red": 15
    }
}


# ============================================================
# BUILD QUBO
# ============================================================

def build_qubo(traffic_state, emergency_junctions=None):
    """
    Build a QUBO objective for signal optimization.

    One binary variable is created for each junction.

    x = 0 -> PLAN_1
    x = 1 -> PLAN_2

    The objective rewards longer green time when:

    - queue is high
    - congestion is high
    - emergency priority exists

    Returns
    -------
    dict
        QUBO coefficients and metadata.
    """

    if emergency_junctions is None:
        emergency_junctions = []

    junctions = list(traffic_state.keys())

    linear = {}

    for junction in junctions:

        data = traffic_state[junction]

        queue = data["queue"]

        capacity = max(
            data["capacity"],
            1
        )

        speed = data["speed"]

        density = data["vehicles"] / capacity

        congestion = (
            (queue / capacity) * 0.5
            + ((30 - speed) / 30) * 0.3
            + density * 0.2
        )

        congestion = max(
            0,
            min(1, congestion)
        )

        emergency = (
            1
            if junction in emergency_junctions
            else 0
        )

        # Higher value means PLAN_2 is more desirable.
        priority = (
            queue / capacity
            + congestion
            + emergency * 2.0
        )

        linear[junction] = round(
            -priority,
            4
        )

    return {
        "junctions": junctions,
        "linear": linear
    }


# ============================================================
# ENUMERATE QUBO SOLUTIONS
# ============================================================

def evaluate_solution(bitstring, qubo):
    """
    Evaluate a binary solution.

    Lower QUBO energy is better.
    """

    energy = 0.0

    for index, junction in enumerate(
        qubo["junctions"]
    ):

        bit = int(bitstring[index])

        coefficient = qubo[
            "linear"
        ][junction]

        energy += coefficient * bit

    return round(
        energy,
        6
    )


def find_best_solution(qubo):
    """
    Find the minimum-energy solution.

    This exhaustive search is used as a reference
    for validating the QAOA result on the small
    4-junction problem.
    """

    n = len(
        qubo["junctions"]
    )

    best_bitstring = None

    best_energy = float("inf")

    for number in range(
        2 ** n
    ):

        bitstring = format(
            number,
            f"0{n}b"
        )

        energy = evaluate_solution(
            bitstring,
            qubo
        )

        if energy < best_energy:

            best_energy = energy

            best_bitstring = bitstring

    return {
        "bitstring": best_bitstring,
        "energy": best_energy
    }


# ============================================================
# QAOA-STYLE QUANTUM SEARCH
# ============================================================

def run_qaoa(qubo, shots=2048):
    """
    Run a quantum circuit that encodes the QUBO
    objective and samples candidate solutions.

    The circuit:

    1. Creates a uniform superposition.
    2. Applies a cost phase according to the QUBO.
    3. Applies a mixing layer.
    4. Measures candidate solutions.

    This is a lightweight QAOA-style prototype
    suitable for the hackathon simulator.

    Returns
    -------
    dict
        Quantum samples and selected solution.
    """

    junctions = qubo[
        "junctions"
    ]

    n = len(junctions)

    circuit = QuantumCircuit(
        n,
        n
    )

    # --------------------------------------------------------
    # INITIAL SUPERPOSITION
    # --------------------------------------------------------

    for qubit in range(n):

        circuit.h(qubit)

    # --------------------------------------------------------
    # COST LAYER
    # --------------------------------------------------------

    for index, junction in enumerate(
        junctions
    ):

        coefficient = qubo[
            "linear"
        ][junction]

        # Convert coefficient into a
        # rotation angle.

        angle = float(
            coefficient * np.pi
        )

        circuit.rz(
            angle,
            index
        )

    # --------------------------------------------------------
    # MIXER LAYER
    # --------------------------------------------------------

    for qubit in range(n):

        circuit.rx(
            np.pi / 2,
            qubit
        )

    # --------------------------------------------------------
    # MEASURE
    # --------------------------------------------------------

    circuit.measure(
        range(n),
        range(n)
    )

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    # --------------------------------------------------------
    # SELECT LOWEST-ENERGY OBSERVED SOLUTION
    # --------------------------------------------------------

    best_bitstring = None

    best_energy = float("inf")

    for bitstring, count in counts.items():

        energy = evaluate_solution(
            bitstring,
            qubo
        )

        if energy < best_energy:

            best_energy = energy

            best_bitstring = bitstring

    return {
        "bitstring": best_bitstring,
        "energy": best_energy,
        "counts": counts,
        "circuit": circuit
    }


# ============================================================
# DECODE SIGNAL PLAN
# ============================================================

def decode_signal_plan(
    bitstring,
    junctions
):
    """
    Convert quantum binary output
    into traffic signal plans.
    """

    signal_plan = {}

    for index, junction in enumerate(
        junctions
    ):

        bit = int(
            bitstring[index]
        )

        plan = SIGNAL_PLANS[
            bit
        ]

        signal_plan[junction] = {
            "green": plan["green"],
            "red": plan["red"],
            "plan": plan["name"],
            "quantum_bit": bit
        }

    return signal_plan


# ============================================================
# COMPLETE QUANTUM OPTIMIZATION
# ============================================================

def optimize_with_qaoa(
    traffic_state,
    emergency_junctions=None,
    shots=2048
):
    """
    Complete QUBO + quantum optimization pipeline.
    """

    qubo = build_qubo(
        traffic_state,
        emergency_junctions
    )

    quantum_result = run_qaoa(
        qubo,
        shots=shots
    )

    signal_plan = decode_signal_plan(
        quantum_result["bitstring"],
        qubo["junctions"]
    )

    exact_solution = find_best_solution(
        qubo
    )

    return {
        "qubo": qubo,
        "quantum_result": quantum_result,
        "signal_plan": signal_plan,
        "reference_solution": exact_solution
    }


# ============================================================
# TEST
# ============================================================

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
            "queue": 31,
            "speed": 15,
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

    emergency_junctions = [
        "J2",
        "J3"
    ]

    result = optimize_with_qaoa(
        traffic_state,
        emergency_junctions
    )

    print("\n" + "=" * 70)
    print("Q-TRAFFIC QUANTUM OPTIMIZATION")
    print("=" * 70)

    print("\nJUNCTIONS")

    print(
        result["qubo"]["junctions"]
    )

    print("\nQUBO LINEAR COEFFICIENTS")

    for junction, value in result[
        "qubo"
    ]["linear"].items():

        print(
            f"{junction}: {value}"
        )

    print("\nQUANTUM RESULT")

    print(
        "Bitstring:",
        result[
            "quantum_result"
        ]["bitstring"]
    )

    print(
        "Energy:",
        result[
            "quantum_result"
        ]["energy"]
    )

    print("\nREFERENCE OPTIMUM")

    print(
        "Bitstring:",
        result[
            "reference_solution"
        ]["bitstring"]
    )

    print(
        "Energy:",
        result[
            "reference_solution"
        ]["energy"]
    )

    print("\nQUANTUM SIGNAL PLAN")

    for junction, plan in result[
        "signal_plan"
    ].items():

        print(
            f"{junction} -> "
            f"{plan['plan']} | "
            f"Green={plan['green']} sec | "
            f"Red={plan['red']} sec | "
            f"Qubit={plan['quantum_bit']}"
        )

    print("\nQUANTUM CIRCUIT")

    print(
        result[
            "quantum_result"
        ]["circuit"]
    )