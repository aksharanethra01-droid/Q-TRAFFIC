import csv
import json
import time
from pathlib import Path

from quantum.qubo_builder import build_qubo
from quantum.qaoa_optimizer import run_qaoa, result_to_dict
from quantum.classical_baseline import exact_classical_qubo


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# TEST SCENARIOS
# ---------------------------------------------------------

SCENARIOS = {

    "NORMAL": {
        "J1": {
            "vehicles": 18,
            "queue": 5,
            "waiting": 20,
            "capacity": 50,
            "congestion": 0.36,
            "shock": "NORMAL",
            "emergency_delay": 0,
        },
        "J2": {
            "vehicles": 22,
            "queue": 7,
            "waiting": 25,
            "capacity": 50,
            "congestion": 0.44,
            "shock": "NORMAL",
            "emergency_delay": 0,
        },
        "J3": {
            "vehicles": 20,
            "queue": 6,
            "waiting": 22,
            "capacity": 50,
            "congestion": 0.40,
            "shock": "NORMAL",
            "emergency_delay": 0,
        },
        "J4": {
            "vehicles": 16,
            "queue": 4,
            "waiting": 18,
            "capacity": 50,
            "congestion": 0.32,
            "shock": "NORMAL",
            "emergency_delay": 0,
        },
    },

    "PEAK": {
        "J1": {
            "vehicles": 35,
            "queue": 16,
            "waiting": 75,
            "capacity": 50,
            "congestion": 0.70,
            "shock": "MEDIUM",
            "emergency_delay": 0,
        },
        "J2": {
            "vehicles": 42,
            "queue": 22,
            "waiting": 95,
            "capacity": 50,
            "congestion": 0.84,
            "shock": "HIGH",
            "emergency_delay": 0,
        },
        "J3": {
            "vehicles": 38,
            "queue": 19,
            "waiting": 88,
            "capacity": 50,
            "congestion": 0.76,
            "shock": "MEDIUM",
            "emergency_delay": 0,
        },
        "J4": {
            "vehicles": 31,
            "queue": 14,
            "waiting": 65,
            "capacity": 50,
            "congestion": 0.62,
            "shock": "MEDIUM",
            "emergency_delay": 0,
        },
    },

    "ACCIDENT_EMERGENCY": {
        "J1": {
            "vehicles": 30,
            "queue": 14,
            "waiting": 70,
            "capacity": 50,
            "congestion": 0.60,
            "shock": "HIGH",
            "emergency_delay": 60,
        },
        "J2": {
            "vehicles": 45,
            "queue": 25,
            "waiting": 120,
            "capacity": 50,
            "congestion": 0.90,
            "shock": "CRITICAL",
            "emergency_delay": 60,
        },
        "J3": {
            "vehicles": 48,
            "queue": 30,
            "waiting": 145,
            "capacity": 50,
            "congestion": 0.96,
            "shock": "CRITICAL",
            "emergency_delay": 60,
        },
        "J4": {
            "vehicles": 36,
            "queue": 18,
            "waiting": 90,
            "capacity": 50,
            "congestion": 0.72,
            "shock": "HIGH",
            "emergency_delay": 60,
        },
    },
}


# ---------------------------------------------------------
# RUN ONE BENCHMARK
# ---------------------------------------------------------

def run_benchmark():

    results = []

    print("=" * 70)
    print("QUANTUM vs CLASSICAL QUBO BENCHMARK")
    print("=" * 70)

    for scenario_name, context in SCENARIOS.items():

        print()
        print("-" * 70)
        print(f"SCENARIO: {scenario_name}")
        print("-" * 70)

        # -------------------------------------------------
        # Build exactly the same QUBO for both methods
        # -------------------------------------------------

        model = build_qubo(context)

        print(
            f"QUBO variables: {model.metadata['n_variables']}"
        )

        print(
            f"Junctions: {model.metadata['n_junctions']}"
        )

        # -------------------------------------------------
        # CLASSICAL EXACT SOLVER
        # -------------------------------------------------

        print()
        print("[CLASSICAL] Running exact QUBO search...")

        classical = exact_classical_qubo(model)

        classical_objective = float(
            classical["objective"]
        )

        classical_time = float(
            classical["execution_time"]
        )

        classical_plans = classical[
            "selected_plan"
        ]

        print(
            f"[CLASSICAL] Objective: "
            f"{classical_objective:.4f}"
        )

        print(
            f"[CLASSICAL] Time: "
            f"{classical_time:.4f}s"
        )

        print(
            f"[CLASSICAL] Plans: "
            f"{classical_plans}"
        )

        # -------------------------------------------------
        # QAOA
        #
        # p=1 is intentionally used for a fast benchmark.
        # Both methods optimize the SAME QUBO model.
        # -------------------------------------------------

        print()
        print("[QAOA] Running QAOA...")

        qaoa_start = time.perf_counter()

        qaoa_result = run_qaoa(
            model,
            p=1,
            shots=256,
            seed=7,
        )

        qaoa_wall_time = (
            time.perf_counter()
            - qaoa_start
        )

        qaoa_data = result_to_dict(
            qaoa_result
        )

        qaoa_objective = qaoa_result.objective_value

        if qaoa_objective is None:
            qaoa_objective = float("inf")
        else:
            qaoa_objective = float(
                qaoa_objective
            )

        qaoa_plans = qaoa_result.selected_plans

        print(
            f"[QAOA] Status: "
            f"{qaoa_result.status}"
        )

        print(
            f"[QAOA] Objective: "
            f"{qaoa_objective:.4f}"
        )

        print(
            f"[QAOA] Time: "
            f"{qaoa_wall_time:.4f}s"
        )

        print(
            f"[QAOA] Plans: "
            f"{qaoa_plans}"
        )

        # -------------------------------------------------
        # OBJECTIVE GAP
        # -------------------------------------------------

        if classical_objective != 0:

            objective_gap = (
                (
                    qaoa_objective
                    - classical_objective
                )
                / abs(classical_objective)
            ) * 100.0

        else:
            objective_gap = 0.0

        # -------------------------------------------------
        # EXACT MATCH
        # -------------------------------------------------

        exact_match = (
            abs(
                qaoa_objective
                - classical_objective
            )
            < 1e-6
        )

        # -------------------------------------------------
        # STORE RESULT
        # -------------------------------------------------

        record = {
            "scenario": scenario_name,

            "classical_method":
                classical["method"],

            "quantum_method":
                qaoa_result.method,

            "classical_objective":
                round(
                    classical_objective,
                    6
                ),

            "qaoa_objective":
                round(
                    qaoa_objective,
                    6
                ),

            "objective_gap_percent":
                round(
                    objective_gap,
                    4
                ),

            "classical_time_seconds":
                round(
                    classical_time,
                    6
                ),

            "qaoa_time_seconds":
                round(
                    qaoa_wall_time,
                    6
                ),

            "qaoa_circuit_execution_time":
                round(
                    qaoa_result.execution_time,
                    6
                ),

            "qaoa_status":
                qaoa_result.status,

            "qaoa_depth":
                qaoa_result.circuit_depth,

            "exact_objective_match":
                exact_match,

            "classical_plans":
                classical_plans,

            "qaoa_plans":
                qaoa_plans,

            "qaoa_bitstring":
                qaoa_result.best_bitstring,
        }

        results.append(record)

        print()
        print(
            f"Objective gap: "
            f"{objective_gap:.2f}%"
        )

        print(
            f"Exact objective match: "
            f"{exact_match}"
        )

    return results


# ---------------------------------------------------------
# SAVE CSV
# ---------------------------------------------------------

def save_csv(results):

    output_file = (
        OUTPUT_DIR
        / "quantum_vs_classical.csv"
    )

    fieldnames = [
        "scenario",
        "classical_method",
        "quantum_method",
        "classical_objective",
        "qaoa_objective",
        "objective_gap_percent",
        "classical_time_seconds",
        "qaoa_time_seconds",
        "qaoa_circuit_execution_time",
        "qaoa_status",
        "qaoa_depth",
        "exact_objective_match",
        "classical_plans",
        "qaoa_plans",
        "qaoa_bitstring",
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in results:
            writer.writerow(row)

    print()
    print(
        f"CSV saved: {output_file}"
    )


# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------

def save_json(results):

    output_file = (
        OUTPUT_DIR
        / "quantum_vs_classical.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            default=str,
        )

    print(
        f"JSON saved: {output_file}"
    )


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

def save_summary(results):

    valid_results = [
        r
        for r in results
        if r["qaoa_status"] != "FALLBACK"
    ]

    if valid_results:

        average_gap = sum(
            r["objective_gap_percent"]
            for r in valid_results
        ) / len(valid_results)

        average_classical_time = sum(
            r["classical_time_seconds"]
            for r in valid_results
        ) / len(valid_results)

        average_qaoa_time = sum(
            r["qaoa_time_seconds"]
            for r in valid_results
        ) / len(valid_results)

    else:

        average_gap = 0.0
        average_classical_time = 0.0
        average_qaoa_time = 0.0

    summary = {

        "benchmark": (
            "Quantum QAOA vs Exact Classical QUBO"
        ),

        "scenarios_tested":
            len(results),

        "successful_qaoa_runs":
            len(valid_results),

        "average_objective_gap_percent":
            round(
                average_gap,
                4
            ),

        "average_classical_time_seconds":
            round(
                average_classical_time,
                6
            ),

        "average_qaoa_time_seconds":
            round(
                average_qaoa_time,
                6
            ),

        "same_qubo_used":
            True,

        "quantum_advantage_claimed":
            False,

        "note": (
            "QAOA and exact classical optimization "
            "were evaluated on the same QUBO scenarios. "
            "Results are measured experimentally; "
            "no quantum advantage is assumed."
        ),

        "scenarios": results,
    }

    output_file = (
        OUTPUT_DIR
        / "benchmark_summary.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
            default=str,
        )

    print(
        f"Summary saved: {output_file}"
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    results = run_benchmark()

    save_csv(results)

    save_json(results)

    save_summary(results)

    print()
    print("=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)

    for result in results:

        print(
            f"{result['scenario']:22s} | "
            f"Classical: "
            f"{result['classical_objective']:10.4f} | "
            f"QAOA: "
            f"{result['qaoa_objective']:10.4f} | "
            f"Gap: "
            f"{result['objective_gap_percent']:8.2f}%"
        )