import time
import math
import numpy as np
from dataclasses import dataclass, asdict

from .qubo_builder import QUBOModel
from .decoder import decode_bitstring


@dataclass
class QAOAResult:
    method: str
    status: str
    p: int
    best_bitstring: str | None
    selected_plans: dict
    objective_value: float | None
    counts: dict
    parameters: dict
    circuit_depth: int | None
    execution_time: float
    message: str = ""


def qubo_to_ising(model: QUBOModel):
    """
    Convert:

        x^T Q x + l^T x + c

    into an Ising representation using:

        x = (1 - Z) / 2
    """

    n = len(model.variables)

    h = np.zeros(n)
    couplings = {}

    const = float(model.constant)

    # Linear terms + diagonal Q terms
    for i in range(n):
        const += (
            0.5 * model.linear[i]
            + 0.25 * model.matrix[i, i]
        )

        h[i] += (
            -0.5 * model.linear[i]
            -0.5 * model.matrix[i, i]
        )

    # Quadratic terms
    for i in range(n):
        for j in range(i + 1, n):

            q = (
                model.matrix[i, j]
                + model.matrix[j, i]
            )

            if q:

                const += q / 4

                h[i] -= q / 4
                h[j] -= q / 4

                couplings[(i, j)] = q / 4

    return const, h, couplings


def _qaoa_circuit(
    model: QUBOModel,
    gammas,
    betas,
    measure=True
):
    """
    Build the actual QAOA circuit.

    Initial state:
        |+>^n

    Cost layer:
        RZ + RZZ

    Mixer:
        RX

    Measurement:
        computational basis
    """

    from qiskit import QuantumCircuit

    n = len(model.variables)

    _, h, couplings = qubo_to_ising(model)

    qc = QuantumCircuit(
        n,
        n if measure else 0
    )

    # Initial superposition
    for q in range(n):
        qc.h(q)

    # QAOA layers
    for layer in range(len(gammas)):

        gamma = gammas[layer]
        beta = betas[layer]

        # Cost Hamiltonian
        for q, coeff in enumerate(h):

            qc.rz(
                2 * gamma * coeff,
                q
            )

        for (i, j), coeff in couplings.items():

            qc.rzz(
                2 * gamma * coeff,
                i,
                j
            )

        # Mixer
        for q in range(n):

            qc.rx(
                2 * beta,
                q
            )

    if measure:

        qc.measure(
            range(n),
            range(n)
        )

    return qc


def _normalise_bitstring(
    raw,
    expected_length
):
    """
    Convert Qiskit's displayed bitstring
    into the project's variable ordering.
    """

    bits = raw.replace(" ", "")[::-1]

    if len(bits) != expected_length:
        return None

    if any(
        b not in ("0", "1")
        for b in bits
    ):
        return None

    return bits


def _is_valid_one_hot(model, bits):
    """
    Verify exactly one selected plan per junction.
    """

    plans_per_junction = int(
        model.metadata.get(
            "plans_per_junction",
            3
        )
    )

    n_junctions = int(
        model.metadata.get(
            "n_junctions",
            len(bits) // plans_per_junction
        )
    )

    expected = (
        n_junctions
        * plans_per_junction
    )

    if len(bits) != expected:
        return False

    for junction in range(n_junctions):

        start = (
            junction
            * plans_per_junction
        )

        end = (
            start
            + plans_per_junction
        )

        group = bits[start:end]

        if sum(
            int(x)
            for x in group
        ) != 1:
            return False

    return True


def _find_best_valid_sample(
    model: QUBOModel,
    counts
):
    """
    Search ALL measured QAOA states and return
    the lowest-energy feasible state.

    This is important because parameter search
    must compare feasible solutions globally.
    """

    best = None

    for raw, count in counts.items():

        bits = _normalise_bitstring(
            raw,
            len(model.variables)
        )

        if bits is None:
            continue

        if not _is_valid_one_hot(
            model,
            bits
        ):
            continue

        energy = model.evaluate(
            [int(x) for x in bits]
        )

        plans, valid = decode_bitstring(
            bits
        )

        if not valid:
            continue

        candidate = (
            float(energy),
            bits,
            plans,
            int(count)
        )

        if (
            best is None
            or candidate[0] < best[0]
        ):
            best = candidate

    return best


def _constraint_repair(
    model: QUBOModel,
    measured_bits
):
    """
    Convert an arbitrary measured QAOA state
    into the nearest feasible one-plan-per-junction
    solution.

    The repaired state is explicitly marked as
    hybrid rather than directly measured.
    """

    plans_per_junction = int(
        model.metadata.get(
            "plans_per_junction",
            3
        )
    )

    n_junctions = int(
        model.metadata.get(
            "n_junctions",
            len(measured_bits)
            // plans_per_junction
        )
    )

    expected = (
        n_junctions
        * plans_per_junction
    )

    if len(measured_bits) != expected:
        raise ValueError(
            f"Expected {expected} bits, "
            f"got {len(measured_bits)}."
        )

    repaired = [0] * expected

    for junction in range(n_junctions):

        start_idx = (
            junction
            * plans_per_junction
        )

        end_idx = (
            start_idx
            + plans_per_junction
        )

        group = measured_bits[
            start_idx:end_idx
        ]

        active = [
            i
            for i, bit in enumerate(group)
            if bit == "1"
        ]

        # If QAOA selected one or more plans,
        # choose the best one according to
        # the complete QUBO objective.
        candidates = []

        if active:

            candidate_indices = active

        else:

            # No active plan:
            # consider every candidate.
            candidate_indices = list(
                range(plans_per_junction)
            )

        for chosen in candidate_indices:

            candidate_bits = repaired.copy()

            candidate_bits[
                start_idx + chosen
            ] = 1

            candidate_energy = model.evaluate(
                candidate_bits
            )

            candidates.append(
                (
                    float(candidate_energy),
                    chosen
                )
            )

        chosen = min(
            candidates,
            key=lambda x: x[0]
        )[1]

        repaired[
            start_idx + chosen
        ] = 1

    repaired_bits = "".join(
        str(x)
        for x in repaired
    )

    plans, valid = decode_bitstring(
        repaired_bits
    )

    if not valid:
        raise RuntimeError(
            "Constraint repair produced "
            "an invalid solution."
        )

    return repaired_bits, plans


def _build_parameter_candidates(p):
    """
    Deterministic compact parameter search.

    p=1:
        25 combinations

    p=2:
        compact grid suitable for the
        12-qubit hackathon prototype.
    """

    if p == 1:

        grid = np.linspace(
            -math.pi,
            math.pi,
            5
        )

        return [
            ((gamma,), (beta,))
            for gamma in grid
            for beta in grid
        ]

    if p == 2:

        gamma1_grid = (
            -math.pi,
            -math.pi / 2,
            0,
            math.pi / 2,
            math.pi
        )

        gamma2_grid = (
            -math.pi,
            0,
            math.pi
        )

        beta_grid = (
            -math.pi / 2,
            0,
            math.pi / 2
        )

        return [
            (
                (g1, g2),
                (b1, b2)
            )
            for g1 in gamma1_grid
            for g2 in gamma2_grid
            for b1 in beta_grid
            for b2 in beta_grid
        ]

    raise ValueError(
        "This prototype currently supports "
        "QAOA depth p=1 or p=2."
    )


def run_qaoa(
    model: QUBOModel,
    p: int = 2,
    shots: int = 512,
    seed: int = 7
) -> QAOAResult:

    start = time.perf_counter()

    # ---------------------------------------------------------
    # 1. Import Qiskit Aer
    # ---------------------------------------------------------

    try:

        from qiskit_aer import AerSimulator
        from qiskit import transpile

    except Exception as exc:

        return QAOAResult(
            "CLASSICAL_FALLBACK",
            "FALLBACK",
            p,
            None,
            {},
            None,
            {},
            {},
            None,
            time.perf_counter() - start,
            f"Qiskit Aer unavailable: {exc}"
        )

    # ---------------------------------------------------------
    # 2. Actual QAOA execution
    # ---------------------------------------------------------

    try:

        simulator = AerSimulator(
            seed_simulator=seed
        )

        candidates = (
            _build_parameter_candidates(p)
        )

        global_best = None
        global_params = None
        global_depth = None
        global_counts = {}

        total_candidates = len(candidates)

        # -----------------------------------------------------
        # Search all QAOA parameter candidates
        # -----------------------------------------------------

        for candidate_index, (
            gammas,
            betas
        ) in enumerate(candidates):

            qc = _qaoa_circuit(
                model,
                gammas,
                betas
            )

            tqc = transpile(
                qc,
                simulator
            )

            run_shots = max(
                128,
                shots // 4
            )

            result = simulator.run(
                tqc,
                shots=run_shots
            ).result()

            counts = result.get_counts()

            valid_sample = (
                _find_best_valid_sample(
                    model,
                    counts
                )
            )

            if valid_sample is None:
                continue

            energy, bits, plans, count = (
                valid_sample
            )

            candidate = (
                float(energy),
                bits,
                plans,
                count
            )

            # IMPORTANT:
            # Compare against the global best,
            # not just the first valid result.
            if (
                global_best is None
                or candidate[0]
                < global_best[0]
            ):

                global_best = candidate

                global_params = {
                    "gammas": list(gammas),
                    "betas": list(betas),
                    "parameter_candidate":
                        candidate_index + 1,
                    "total_parameter_candidates":
                        total_candidates,
                    "search_strategy":
                        "global_best_feasible_sample"
                }

                global_depth = tqc.depth()

                global_counts = counts

        # -----------------------------------------------------
        # 3. Valid QAOA solution found
        # -----------------------------------------------------

        if global_best is not None:

            energy, bits, plans, count = (
                global_best
            )

            elapsed = (
                time.perf_counter()
                - start
            )

            return QAOAResult(
                "QAOA_AER",
                "SUCCESS",
                p,
                bits,
                plans,
                float(energy),
                global_counts,
                global_params or {},
                global_depth,
                elapsed,
                "Actual QAOA circuit executed "
                "on Qiskit Aer. All measured feasible "
                "states across the parameter search "
                "were compared and the lowest-energy "
                "feasible solution was selected."
            )

        # -----------------------------------------------------
        # 4. No valid state naturally measured
        # -----------------------------------------------------

        fallback_gammas = tuple(
            [math.pi / 2] * p
        )

        fallback_betas = tuple(
            [math.pi / 4] * p
        )

        qc = _qaoa_circuit(
            model,
            fallback_gammas,
            fallback_betas
        )

        tqc = transpile(
            qc,
            simulator
        )

        fallback_shots = max(
            1024,
            shots
        )

        result = simulator.run(
            tqc,
            shots=fallback_shots
        ).result()

        counts = result.get_counts()

        # -----------------------------------------------------
        # Lowest-energy raw measured state
        # -----------------------------------------------------

        raw_candidates = []

        for raw, count in counts.items():

            bits = _normalise_bitstring(
                raw,
                len(model.variables)
            )

            if bits is None:
                continue

            energy = model.evaluate(
                [int(x) for x in bits]
            )

            raw_candidates.append(
                (
                    float(energy),
                    int(count),
                    bits
                )
            )

        if not raw_candidates:

            raise RuntimeError(
                "Aer executed but returned "
                "no measurable bitstring."
            )

        raw_energy, raw_count, raw_bits = min(
            raw_candidates,
            key=lambda x: x[0]
        )

        # -----------------------------------------------------
        # Constraint-aware repair
        # -----------------------------------------------------

        repaired_bits, repaired_plans = (
            _constraint_repair(
                model,
                raw_bits
            )
        )

        repaired_energy = model.evaluate(
            [
                int(x)
                for x in repaired_bits
            ]
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        return QAOAResult(
            "QAOA_AER_HYBRID",
            "SUCCESS",
            p,
            repaired_bits,
            repaired_plans,
            float(repaired_energy),
            counts,
            {
                "gammas": list(
                    fallback_gammas
                ),
                "betas": list(
                    fallback_betas
                ),
                "raw_measured_bitstring":
                    raw_bits,
                "raw_measured_energy":
                    float(raw_energy),
                "raw_measured_count":
                    int(raw_count),
                "constraint_repair":
                    True,
                "repair_type":
                    "one-plan-per-junction",
                "search_strategy":
                    "fallback_constraint_repair",
                "note":
                    "The returned feasible solution "
                    "was repaired from a QAOA/Aer "
                    "measured state."
            },
            tqc.depth(),
            elapsed,
            "Actual QAOA circuit executed "
            "on Qiskit Aer. No valid constrained "
            "state was naturally sampled, so "
            "the measured state was passed through "
            "explicit constraint-aware repair."
        )

    # ---------------------------------------------------------
    # 5. Genuine execution failure
    # ---------------------------------------------------------

    except Exception as exc:

        return QAOAResult(
            "CLASSICAL_FALLBACK",
            "FALLBACK",
            p,
            None,
            {},
            None,
            {},
            {},
            None,
            time.perf_counter() - start,
            f"QAOA execution failed: {exc}"
        )


def result_to_dict(
    result: QAOAResult
):
    return asdict(result)