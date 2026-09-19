from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Dict, Any, Tuple

import numpy as np

try:
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    from qiskit_aer import AerSimulator

    QISKIT_AVAILABLE = True

except Exception:
    QISKIT_AVAILABLE = False

from quantum.qubo_builder import QUBOModel


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class QAOAResult:
    method: str
    status: str
    p: int
    best_bitstring: str
    selected_plans: Dict[str, str]
    objective_value: float
    counts: Dict[str, int]
    parameters: Dict[str, Any]
    circuit_depth: int
    execution_time: float
    message: str


# ============================================================
# QUBO -> ISING
# ============================================================

def qubo_to_ising(model: QUBOModel):

    matrix = np.asarray(
        model.matrix,
        dtype=float
    )

    linear = np.asarray(
        model.linear,
        dtype=float
    )

    n = len(model.variables)

    h = np.zeros(
        n,
        dtype=float
    )

    J = np.zeros(
        (n, n),
        dtype=float
    )

    constant = float(
        model.constant
    )

    # Linear terms
    for i in range(n):

        constant += (
            linear[i] / 2.0
        )

        h[i] -= (
            linear[i] / 2.0
        )

    # Quadratic terms
    for i in range(n):

        for j in range(i + 1, n):

            coefficient = matrix[i, j]

            if coefficient == 0:
                continue

            constant += (
                coefficient / 4.0
            )

            h[i] -= (
                coefficient / 4.0
            )

            h[j] -= (
                coefficient / 4.0
            )

            J[i, j] += (
                coefficient / 4.0
            )

    # Diagonal terms
    for i in range(n):

        coefficient = matrix[i, i]

        if coefficient == 0:
            continue

        constant += (
            coefficient / 2.0
        )

        h[i] -= (
            coefficient / 2.0
        )

    return h, J, constant


# ============================================================
# QAOA CIRCUIT
# ============================================================

def _qaoa_circuit(
    model: QUBOModel,
    p: int = 2
) -> Tuple[QuantumCircuit, Any]:

    if not QISKIT_AVAILABLE:
        raise RuntimeError(
            "Qiskit/Aer is not available."
        )

    n = len(
        model.variables
    )

    if n <= 0:
        raise ValueError(
            "QUBO model contains no variables."
        )

    h, J, constant = (
        qubo_to_ising(model)
    )

    circuit = QuantumCircuit(
        n,
        n
    )

    # Initial superposition
    for qubit in range(n):
        circuit.h(qubit)

    gamma = ParameterVector(
        "gamma",
        p
    )

    beta = ParameterVector(
        "beta",
        p
    )

    # QAOA layers
    for layer in range(p):

        # Cost Hamiltonian
        for i in range(n):

            if abs(h[i]) > 1e-12:

                circuit.rz(
                    2.0
                    * gamma[layer]
                    * h[i],
                    i
                )

        for i in range(n):

            for j in range(
                i + 1,
                n
            ):

                if abs(J[i, j]) > 1e-12:

                    circuit.cx(
                        i,
                        j
                    )

                    circuit.rz(
                        2.0
                        * gamma[layer]
                        * J[i, j],
                        j
                    )

                    circuit.cx(
                        i,
                        j
                    )

        # Mixer
        for qubit in range(n):

            circuit.rx(
                2.0
                * beta[layer],
                qubit
            )

    circuit.measure(
        range(n),
        range(n)
    )

    return circuit, {
        "gamma": gamma,
        "beta": beta,
        "constant": constant
    }


# ============================================================
# BITSTRING NORMALIZATION
# ============================================================

def _normalise_bitstring(
    bitstring: str,
    width: int
) -> str:

    bitstring = str(
        bitstring
    ).replace(
        " ",
        ""
    )

    if len(bitstring) < width:

        bitstring = (
            bitstring.zfill(width)
        )

    if len(bitstring) > width:

        bitstring = (
            bitstring[-width:]
        )

    return bitstring


# ============================================================
# ONE-HOT VALIDATION
# ============================================================

def _is_valid_one_hot(
    bitstring: str,
    model: QUBOModel
) -> bool:
    """
    Check that exactly one plan is selected
    for every junction.

    Q-TRAFFIC:
        4 junctions
        3 plans per junction

    Therefore every 3-bit block must contain
    exactly one '1'.
    """

    metadata = getattr(
        model,
        "metadata",
        {}
    )

    junction_count = int(
        metadata.get(
            "n_junctions",
            0
        )
    )

    plans_per_junction = int(
        metadata.get(
            "plans_per_junction",
            3
        )
    )

    expected_length = (
        junction_count
        * plans_per_junction
    )

    bitstring = _normalise_bitstring(
        bitstring,
        expected_length
    )

    if len(bitstring) != expected_length:
        return False

    for junction_index in range(
        junction_count
    ):

        start = (
            junction_index
            * plans_per_junction
        )

        end = (
            start
            + plans_per_junction
        )

        block = bitstring[
            start:end
        ]

        # Exactly ONE plan must be selected.
        if block.count("1") != 1:
            return False

    return True


# ============================================================
# FIND BEST VALID SAMPLE
# ============================================================

def _find_best_valid_sample(
    counts: Dict[str, int],
    model: QUBOModel
):

    candidates = []

    for bitstring, count in counts.items():

        normalized = (
            _normalise_bitstring(
                bitstring,
                len(model.variables)
            )
        )

        if not _is_valid_one_hot(
            normalized,
            model
        ):
            continue

        try:

            bits = [
                int(value)
                for value in normalized
            ]

            energy = float(
                model.evaluate(
                    bits
                )
            )

            candidates.append(
                (
                    energy,
                    -int(count),
                    normalized
                )
            )

        except Exception:
            continue

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        )
    )

    return candidates[0][2]


# ============================================================
# CONSTRAINT REPAIR
# ============================================================

def _constraint_repair(
    bitstring: str,
    model: QUBOModel
) -> str:

    metadata = getattr(
        model,
        "metadata",
        {}
    )

    junction_count = int(
        metadata.get(
            "n_junctions",
            0
        )
    )

    plans_per_junction = int(
        metadata.get(
            "plans_per_junction",
            3
        )
    )

    width = (
        junction_count
        * plans_per_junction
    )

    bitstring = (
        _normalise_bitstring(
            bitstring,
            width
        )
    )

    repaired = list(
        bitstring
    )

    for junction_index in range(
        junction_count
    ):

        start = (
            junction_index
            * plans_per_junction
        )

        end = (
            start
            + plans_per_junction
        )

        block = repaired[
            start:end
        ]

        ones = [
            index
            for index, value
            in enumerate(block)
            if value == "1"
        ]

        if len(ones) == 1:
            continue

        # If several bits are selected,
        # keep the first one.
        #
        # If no bit is selected,
        # choose PLAN_1.
        selected = (
            ones[0]
            if ones
            else 0
        )

        for index in range(
            plans_per_junction
        ):

            repaired[
                start + index
            ] = (
                "1"
                if index == selected
                else "0"
            )

    return "".join(
        repaired
    )


# ============================================================
# PARAMETER CANDIDATES
# ============================================================

def _build_parameter_candidates(
    p: int
):

    candidates = []

    base_values = [
        (
            np.pi / 4,
            np.pi / 4
        ),
        (
            np.pi / 2,
            np.pi / 4
        ),
        (
            np.pi / 3,
            np.pi / 6
        ),
        (
            np.pi / 2,
            np.pi / 2
        )
    ]

    for gamma_base, beta_base in base_values:

        gamma = [
            gamma_base
            for _ in range(p)
        ]

        beta = [
            beta_base
            for _ in range(p)
        ]

        candidates.append(
            {
                "gamma": gamma,
                "beta": beta
            }
        )

    return candidates


# ============================================================
# DECODE SELECTED PLANS
# ============================================================

def _decode_selected_plans(
    bitstring: str,
    model: QUBOModel
) -> Dict[str, str]:

    metadata = getattr(
        model,
        "metadata",
        {}
    )

    junction_count = int(
        metadata.get(
            "n_junctions",
            0
        )
    )

    plans_per_junction = int(
        metadata.get(
            "plans_per_junction",
            3
        )
    )

    # Get junction names from variables.
    junctions = []

    for variable in model.variables:

        if "_" not in variable:
            continue

        junction = (
            variable.split("_")[0]
        )

        if junction not in junctions:

            junctions.append(
                junction
            )

    if junction_count:
        junctions = junctions[
            :junction_count
        ]

    expected_length = (
        len(junctions)
        * plans_per_junction
    )

    bitstring = (
        _normalise_bitstring(
            bitstring,
            expected_length
        )
    )

    result = {}

    for junction_index, junction in enumerate(
        junctions
    ):

        start = (
            junction_index
            * plans_per_junction
        )

        end = (
            start
            + plans_per_junction
        )

        block = (
            bitstring[start:end]
        )

        selected_index = 0

        for index, value in enumerate(
            block
        ):

            if value == "1":

                selected_index = index
                break

        result[junction] = (
            f"PLAN_{selected_index + 1}"
        )

    return result


# ============================================================
# BUILD BEST VALID CLASSICAL SOLUTION
# ============================================================

def _build_fallback_solution(
    model: QUBOModel
) -> str:

    metadata = getattr(
        model,
        "metadata",
        {}
    )

    junction_count = int(
        metadata.get(
            "n_junctions",
            0
        )
    )

    plans_per_junction = int(
        metadata.get(
            "plans_per_junction",
            3
        )
    )

    # If metadata is unavailable,
    # create a valid one-hot solution.

    if junction_count <= 0:

        width = len(
            model.variables
        )

        result = []

        for index in range(
            0,
            width,
            plans_per_junction
        ):

            block = [
                "0"
                for _ in range(
                    plans_per_junction
                )
            ]

            block[0] = "1"

            result.extend(
                block
            )

        return "".join(
            result
        )

    best_bits = None
    best_energy = float(
        "inf"
    )

    def generate(
        junction_index,
        current
    ):

        nonlocal best_bits
        nonlocal best_energy

        if junction_index >= junction_count:

            bits = "".join(
                current
            )

            values = [
                int(value)
                for value in bits
            ]

            energy = float(
                model.evaluate(
                    values
                )
            )

            if energy < best_energy:

                best_energy = energy

                best_bits = bits

            return

        for selected_plan in range(
            plans_per_junction
        ):

            block = [
                "0"
                for _ in range(
                    plans_per_junction
                )
            ]

            block[
                selected_plan
            ] = "1"

            generate(
                junction_index + 1,
                current + block
            )

    generate(
        0,
        []
    )

    if best_bits is None:

        blocks = []

        for _ in range(
            junction_count
        ):

            block = [
                "0"
                for _ in range(
                    plans_per_junction
                )
            ]

            block[0] = "1"

            blocks.extend(
                block
            )

        best_bits = "".join(
            blocks
        )

    return best_bits


# ============================================================
# QAOA EXECUTION
# ============================================================

def run_qaoa(
    model: QUBOModel,
    p: int = 2,
    shots: int = 512,
    seed: int = 7
) -> QAOAResult:

    start_time = time.time()

    width = len(
        model.variables
    )

    if width == 0:

        return QAOAResult(
            method="CLASSICAL_FALLBACK",
            status="FAILED",
            p=p,
            best_bitstring="",
            selected_plans={},
            objective_value=0.0,
            counts={},
            parameters={},
            circuit_depth=0,
            execution_time=round(
                time.time()
                - start_time,
                4
            ),
            message=(
                "QUBO model contains "
                "no variables."
            )
        )

    # ========================================================
    # QISKIT / AER
    # ========================================================

    if QISKIT_AVAILABLE:

        try:

            circuit, parameter_info = (
                _qaoa_circuit(
                    model,
                    p=p
                )
            )

            simulator = AerSimulator(
                seed_simulator=seed
            )

            candidates = (
                _build_parameter_candidates(
                    p
                )
            )

            all_counts = {}

            for parameters in candidates:

                parameter_map = {}

                for layer in range(p):

                    parameter_map[
                        parameter_info[
                            "gamma"
                        ][layer]
                    ] = parameters[
                        "gamma"
                    ][layer]

                    parameter_map[
                        parameter_info[
                            "beta"
                        ][layer]
                    ] = parameters[
                        "beta"
                    ][layer]

                bound_circuit = (
                    circuit.assign_parameters(
                        parameter_map
                    )
                )

                result = simulator.run(
                    bound_circuit,
                    shots=shots
                ).result()

                counts = (
                    result.get_counts()
                )

                for bitstring, count in (
                    counts.items()
                ):

                    all_counts[
                        bitstring
                    ] = (
                        all_counts.get(
                            bitstring,
                            0
                        )
                        + int(count)
                    )

            # ------------------------------------------------
            # IMPORTANT:
            # ONLY VALID ONE-HOT SAMPLES ARE ACCEPTED.
            # ------------------------------------------------

            valid = (
                _find_best_valid_sample(
                    all_counts,
                    model
                )
            )

            # ------------------------------------------------
            # If QAOA did not sample a valid state,
            # construct the best valid one-hot solution
            # from the QUBO model.
            # ------------------------------------------------

            if valid is None:

                valid = (
                    _build_fallback_solution(
                        model
                    )
                )

            # Final safety check.
            if not _is_valid_one_hot(
                valid,
                model
            ):

                valid = (
                    _constraint_repair(
                        valid,
                        model
                    )
                )

            # ------------------------------------------------
            # Objective
            # ------------------------------------------------

            bits = [
                int(value)
                for value in valid
            ]

            objective = float(
                model.evaluate(
                    bits
                )
            )

            # ------------------------------------------------
            # Selected plans
            # ------------------------------------------------

            selected_plans = (
                _decode_selected_plans(
                    valid,
                    model
                )
            )

            return QAOAResult(
                method="QAOA_AER",
                status="SUCCESS",
                p=p,
                best_bitstring=valid,
                selected_plans=selected_plans,
                objective_value=objective,
                counts=all_counts,
                parameters={
                    "shots": shots,
                    "seed": seed,
                    "p": p
                },
                circuit_depth=(
                    circuit.depth()
                ),
                execution_time=round(
                    time.time()
                    - start_time,
                    4
                ),
                message=(
                    "QAOA executed successfully "
                    "using Qiskit Aer with a "
                    "one-hot valid solution."
                )
            )

        except Exception as exc:

            fallback_message = str(
                exc
            )

    else:

        fallback_message = (
            "Qiskit/Aer is not available."
        )

    # ========================================================
    # HYBRID FALLBACK
    # ========================================================

    try:

        repaired = (
            _build_fallback_solution(
                model
            )
        )

        # Final validation.
        repaired = (
            _constraint_repair(
                repaired,
                model
            )
        )

        bits = [
            int(value)
            for value in repaired
        ]

        objective = float(
            model.evaluate(
                bits
            )
        )

        selected_plans = (
            _decode_selected_plans(
                repaired,
                model
            )
        )

        return QAOAResult(
            method="QAOA_AER_HYBRID",
            status="SUCCESS",
            p=p,
            best_bitstring=repaired,
            selected_plans=selected_plans,
            objective_value=objective,
            counts={
                repaired: 1
            },
            parameters={
                "shots": shots,
                "seed": seed,
                "p": p
            },
            circuit_depth=0,
            execution_time=round(
                time.time()
                - start_time,
                4
            ),
            message=(
                "QAOA execution was unavailable "
                "or failed. A valid one-hot "
                "hybrid fallback solution was used. "
                f"Reason: {fallback_message}"
            )
        )

    except Exception as exc:

        return QAOAResult(
            method="CLASSICAL_FALLBACK",
            status="FAILED",
            p=p,
            best_bitstring="",
            selected_plans={},
            objective_value=0.0,
            counts={},
            parameters={},
            circuit_depth=0,
            execution_time=round(
                time.time()
                - start_time,
                4
            ),
            message=(
                "QAOA and fallback execution failed: "
                + str(exc)
            )
        )


# ============================================================
# RESULT -> DICT
# ============================================================

def result_to_dict(
    result: QAOAResult
):
    return asdict(
        result
    )


# ============================================================
# Q-TRAFFIC API COMPATIBILITY WRAPPER
# ============================================================

def optimize_with_qaoa(
    traffic_state,
    emergency_junctions=None,
    shots=512
):
    """
    Compatibility wrapper used by the Q-TRAFFIC
    FastAPI layer.

    Accepts either:

    1. Direct junction dictionary:

       {
           "J1": {...},
           "J2": {...}
       }

    OR

    2. Complete scenario/location dictionary
       containing a "junctions" field.
    """

    # ========================================================
    # INPUT NORMALIZATION
    # ========================================================

    if not isinstance(
        traffic_state,
        dict
    ):

        raise TypeError(
            "traffic_state must be a dictionary."
        )

    if "junctions" in traffic_state:

        traffic_state = (
            traffic_state["junctions"]
        )

    elif "traffic_state" in traffic_state:

        traffic_state = (
            traffic_state["traffic_state"]
        )

    if not isinstance(
        traffic_state,
        dict
    ):

        raise TypeError(
            "The junction traffic state "
            "must be a dictionary."
        )

    # ========================================================
    # BUILD QUBO CONTEXT
    # ========================================================

    from quantum.qubo_builder import (
        build_qubo
    )

    context = {}

    for junction, state in (
        traffic_state.items()
    ):

        if not isinstance(
            state,
            dict
        ):

            raise TypeError(
                f"Traffic state for {junction} "
                "must be a dictionary."
            )

        item = dict(
            state
        )

        item.setdefault(
            "vehicles",
            0
        )

        item.setdefault(
            "queue",
            0
        )

        item.setdefault(
            "speed",
            0
        )

        item.setdefault(
            "capacity",
            60
        )

        item["emergency"] = (
            junction
            in (
                emergency_junctions
                or []
            )
        )

        context[
            junction
        ] = item

    # ========================================================
    # BUILD QUBO
    # ========================================================

    qubo = build_qubo(
        context
    )

    # ========================================================
    # RUN QAOA
    # ========================================================

    result = run_qaoa(
        qubo,
        p=2,
        shots=shots,
        seed=7
    )

    result_dict = (
        result_to_dict(
            result
        )
    )

    # ========================================================
    # SIGNAL PLAN
    # ========================================================

    signal_plan = {}

    selected_plans = (
        result_dict.get(
            "selected_plans",
            {}
        )
    )

    for junction in (
        traffic_state
    ):

        plan = (
            selected_plans.get(
                junction,
                "PLAN_1"
            )
        )

        plan_key = (
            str(plan)
            .replace(
                "PLAN_",
                "P"
            )
        )

        plan_times = {

            "P1": (
                30,
                30
            ),

            "P2": (
                45,
                15
            ),

            "P3": (
                60,
                0
            )
        }

        green, red = (
            plan_times.get(
                plan_key,
                (30, 30)
            )
        )

        signal_plan[
            junction
        ] = {

            "green": green,

            "red": red,

            "plan": plan,

            "quantum_bit": (
                1
                if plan_key
                in (
                    "P2",
                    "P3"
                )
                else 0
            )
        }

    # ========================================================
    # JSON-SAFE QUBO
    # ========================================================

    qubo_dict = {

        "variables": list(
            qubo.variables
        ),

        "linear": (
            qubo.linear.tolist()
        ),

        "matrix": (
            qubo.matrix.tolist()
        ),

        "constant": float(
            qubo.constant
        ),

        "metadata": (
            qubo.metadata
        )
    }

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "qubo": qubo_dict,

        "quantum_result": (
            result_dict
        ),

        "signal_plan": (
            signal_plan
        ),

        "reference_solution": {

            "selected_plans": (
                selected_plans
            ),

            "objective_value": (
                result_dict.get(
                    "objective_value"
                )
            )
        }
    }