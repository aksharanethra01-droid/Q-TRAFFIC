from pathlib import Path
import time

from sumo.traci_controller import TraCIController
from ai.traffic_monitor import TrafficMonitor
from ai.shock_propagation import propagate_shock
from quantum.qubo_builder import build_qubo
from quantum.qaoa_optimizer import run_qaoa
from quantum.classical_baseline import exact_classical_qubo
from scenarios.events import events_at
from alerts.bilingual_alerts import generate_alert
from alerts.tts_alerts import generate_bilingual_tts
from emergency.green_corridor import GreenCorridorController
from emergency.ambulance import EmergencyVehicle
from metrics.collector import MetricsCollector


BASE = Path(__file__).resolve().parent


def build_context(ctl):
    context = {}

    for tls in ctl.traci.trafficlight.getIDList():

        lanes = ctl.traci.trafficlight.getControlledLanes(
            tls
        )

        unique_lanes = list(dict.fromkeys(lanes))

        vehicles = 0
        queue = 0
        waiting = 0.0

        for lane in unique_lanes:

            vehicles += (
                ctl.traci.lane.getLastStepVehicleNumber(
                    lane
                )
            )

            queue += (
                ctl.traci.lane.getLastStepHaltingNumber(
                    lane
                )
            )

            vehicle_ids = (
                ctl.traci.lane.getLastStepVehicleIDs(
                    lane
                )
            )

            for vehicle_id in vehicle_ids:

                waiting += (
                    ctl.traci.vehicle.getWaitingTime(
                        vehicle_id
                    )
                )

        context[tls] = {
            "vehicles": float(vehicles),
            "queue": float(queue),
            "capacity": 50.0,
            "waiting": float(waiting),
            "throughput": 0.0,
            "shock": 0.0,
            "emergency_delay": 0.0,
        }

    return context


def apply_event_effects(
    context,
    event,
    junction=None
):

    if event in (
        "SCHOOL_PEAK",
        "TEXTILE_FESTIVAL",
        "CROWD_SURGE",
    ):

        if junction in context:

            context[junction]["vehicles"] *= 1.35
            context[junction]["queue"] *= 1.35
            context[junction]["waiting"] *= 1.25

    elif event == "VEHICLE_OBSTRUCTION":

        if junction in context:

            context[junction]["vehicles"] *= 1.30
            context[junction]["queue"] *= 1.50
            context[junction]["waiting"] *= 1.40

    elif event == "ACCIDENT":

        if junction in context:

            context[junction]["vehicles"] *= 1.45
            context[junction]["queue"] *= 1.60
            context[junction]["waiting"] *= 1.50

    elif event == "RECOVERY":

        for state in context.values():

            state["queue"] *= 0.70
            state["waiting"] *= 0.65


def run():

    ctl = TraCIController(
        gui=True,
        seed=7
    )

    monitor = TrafficMonitor()
    metrics = MetricsCollector()

    ambulance = EmergencyVehicle()

    corridor = GreenCorridorController(
        ambulance.route
    )

    previous_plans = None

    ctl.start()

    print()
    print("=" * 70)
    print("QUANTUM-ENHANCED ADAPTIVE URBAN TRAFFIC OPTIMIZATION")
    print("=" * 70)
    print()

    interval_arrivals = 0

    try:

        for step in range(0, 601):

            ctl.simulation_step()

            # SUMO reports arrivals for the current simulation step.
            # Accumulate them for each 60-second metric interval.
            if step > 0:

                interval_arrivals += (
                    ctl.traci.simulation.getArrivedNumber()
                )

            if step % 60 != 0:
                continue

            print()
            print("-" * 70)
            print(f"SIMULATION TIME: {step}s")
            print("-" * 70)

            current_events = events_at(step)

            event_names = [
                event["type"]
                for event in current_events
            ]

            event_label = (
                "+".join(event_names)
                if event_names
                else "NORMAL"
            )

            if current_events:

                print(
                    "EVENTS:",
                    ", ".join(event_names)
                )

            context = build_context(ctl)

            # Apply every event occurring at this timestamp.
            for event in current_events:

                apply_event_effects(
                    context,
                    event["type"],
                    event.get("junction")
                )

            # --------------------------------------------------
            # AI TRAFFIC MONITORING
            # --------------------------------------------------

            anomalies = monitor.analyze_network(
                context
            )

            for junction, anomaly in anomalies.items():

                if anomaly.anomaly_type != "NORMAL":

                    print(
                        f"[AI MONITOR] "
                        f"{junction}: "
                        f"{anomaly.anomaly_type} "
                        f"severity={anomaly.severity} "
                        f"score={anomaly.score:.2f}"
                    )

            # --------------------------------------------------
            # TRAFFIC SHOCK PROPAGATION
            # --------------------------------------------------

            for event in current_events:

                shock = propagate_shock(
                    event["type"],
                    event.get("junction")
                )

                for junction, score in (
                    shock.severity_score.items()
                ):

                    if junction in context:

                        context[junction]["shock"] = max(
                            context[junction]["shock"],
                            score
                        )

            # --------------------------------------------------
            # EMERGENCY VEHICLE
            # --------------------------------------------------

            emergency_active = any(
                event["type"] == "AMBULANCE"
                for event in current_events
            )

            emergency_delay = 0.0

            if emergency_active:

                print(
                    "[EMERGENCY] Ambulance detected."
                )

                decision = corridor.evaluate(
                    "J1",
                    context
                )

                print(
                    "[GREEN CORRIDOR]",
                    decision
                )

                if (
                    decision.corridor_status
                    == "ACTIVE"
                ):

                    print(
                        "[GREEN CORRIDOR] "
                        "Applying emergency green..."
                    )

                    for junction in ambulance.route:

                        ctl.set_green(
                            junction
                        )

                    emergency_delay = 60.0

            # --------------------------------------------------
            # AUTOMATIC BILINGUAL ALERTS
            # --------------------------------------------------

            for event in current_events:

                event_type = event["type"]

                if event_type not in (
                    "VEHICLE_OBSTRUCTION",
                    "ACCIDENT",
                    "AMBULANCE",
                ):
                    continue

                junction = (
                    event.get("junction")
                    or "J1"
                )

                if event_type == "VEHICLE_OBSTRUCTION":

                    vehicle_id = event.get(
                        "vehicle_id",
                        "UNKNOWN"
                    )

                    vehicle_model = event.get(
                        "model",
                        "Unknown"
                    )

                elif event_type == "AMBULANCE":

                    vehicle_id = event.get(
                        "vehicle_id",
                        "AMB01"
                    )

                    vehicle_model = "Ambulance"

                else:

                    vehicle_id = ""

                    vehicle_model = "Unknown"

                alert = generate_alert(
                    event_type,
                    junction,
                    vehicle_id=vehicle_id,
                    vehicle_model=vehicle_model,
                    impact="HIGH",
                    ai_action=(
                        "Rolling optimization "
                        "and coordinated signal control"
                    )
                )

                print()
                print("[AI ALERT]")
                print(alert)
                print()

                voice_output = (
                    BASE
                    / "outputs"
                    / "voice_alerts"
                )

                generate_bilingual_tts(
                    english_text=alert["english"],
                    tamil_text=alert["tamil"],
                    output_directory=voice_output,
                    prefix=(
                        f"{step}_"
                        f"{event_type.lower()}"
                    )
                )

            # --------------------------------------------------
            # QUBO / QAOA
            # --------------------------------------------------

            if emergency_active:

                print(
                    "[QAOA] Paused during "
                    "Emergency Green Corridor."
                )

                plans = (
                    previous_plans
                    or {
                        "J1": "PLAN_1",
                        "J2": "PLAN_1",
                        "J3": "PLAN_1",
                        "J4": "PLAN_1",
                    }
                )

                qaoa_time = 0.0

            else:

                qubo_model = build_qubo(
                    context,
                    previous_plans
                )

                qaoa_start = time.perf_counter()

                qaoa_result = run_qaoa(
                    qubo_model
                )

                qaoa_time = (
                    time.perf_counter()
                    - qaoa_start
                )

                if qaoa_result.status == "SUCCESS":

                    plans = (
                        qaoa_result.selected_plans
                    )

                    print(
                        "[QAOA] SUCCESS"
                    )

                else:

                    print(
                        "[QAOA] "
                        "Fallback to classical optimizer."
                    )

                    classical_result = (
                        exact_classical_qubo(
                            qubo_model
                        )
                    )

                    plans = (
                        classical_result[
                            "selected_plan"
                        ]
                    )

                previous_plans = plans

                print(
                    "[SIGNAL PLAN]",
                    plans
                )

                for junction, plan in plans.items():

                    ctl.apply_signal_plan(
                        junction,
                        plan
                    )

            # --------------------------------------------------
            # THROUGHPUT
            # --------------------------------------------------

            throughput = interval_arrivals

            interval_arrivals = 0

            print(
                "[METRICS] "
                f"vehicles={sum(s['vehicles'] for s in context.values()):.1f} "
                f"queue={sum(s['queue'] for s in context.values()):.1f} "
                f"waiting={sum(s['waiting'] for s in context.values()):.1f} "
                f"throughput={throughput}"
            )

            # --------------------------------------------------
            # SAVE METRICS
            # --------------------------------------------------

            record = metrics.record(
                time_seconds=step,
                event=event_label,
                context=context,
                plans=previous_plans,
                qaoa_time=qaoa_time,
                throughput=throughput,
                emergency_delay=emergency_delay
            )

            print(
                "[METRICS SAVED]",
                record
            )

            # --------------------------------------------------
            # RECOVERY
            # --------------------------------------------------

            if event_label == "RECOVERY":

                corridor.clear()

                print(
                    "[EMERGENCY] "
                    "Green Corridor cleared."
                )

                print(
                    "[QAOA] "
                    "Normal optimization resumed."
                )

    finally:

        ctl.close()

        print()
        print("=" * 70)
        print("FINAL METRICS SUMMARY")
        print("=" * 70)

        summary = metrics.summary()

        for key, value in summary.items():

            print(
                f"{key} : {value}"
            )

        print()
        print(
            "Metrics CSV:",
            metrics.output_file
        )


if __name__ == "__main__":
    run()