from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from ai.predictor import TrafficPredictor
from ai.shock_propagation import propagate_shock
from quantum.qubo_builder import build_qubo
from quantum.qaoa_optimizer import run_qaoa, result_to_dict
from emergency.ambulance import EmergencyVehicle
from emergency.green_corridor import GreenCorridorController
from alerts.bilingual_alerts import generate_alert
from metrics.collector import MetricsCollector
from .events import EVENT_TIMELINE

@dataclass
class ScenarioResult:
    time: int
    event: str
    qaoa: dict
    plans: dict
    shock: dict
    emergency: dict
    alert: dict | None

class ScenarioEngine:
    def __init__(self, location="Coimbatore"):
        self.location = location
        self.predictor = TrafficPredictor()
        self.ambulance = EmergencyVehicle()
        self.corridor = GreenCorridorController(self.ambulance.route)
        self.metrics = MetricsCollector()
        self.previous_plans = None
        self.results = []

    def _base_traffic(self, event, source):
        base = {"J1": (28, 9, 50), "J2": (36, 14, 52), "J3": (42, 18, 55), "J4": (30, 10, 50)}
        factor = 1.0
        if event in ("SCHOOL_PEAK", "TEXTILE_FESTIVAL", "CROWD_SURGE"): factor = 1.22
        if event == "ACCIDENT" and source == "J3": factor = 1.45
        if event == "VEHICLE_OBSTRUCTION" and source == "J2": factor = 1.32
        context = {}
        for j, (v, q, cap) in base.items():
            v *= factor
            q *= factor
            wait = q * 1.8
            throughput = max(0, v - q * 0.3)
            context[j] = {"vehicles": v, "queue": q, "capacity": cap, "waiting": wait,
                          "throughput": throughput, "congestion": v/cap, "shock": 0.0,
                          "emergency_delay": 0.0, "occupancy": min(1.0, v/cap),
                          "fuel": wait*0.035+v*0.004, "co2": wait*0.09+v*0.011}
        return context

    def step(self, event, time_seconds, source=None):
        context = self._base_traffic(event, source)
        for j, s in context.items():
            self.predictor.observe(j, s["vehicles"], s["queue"], s["waiting"], s["capacity"])
        preds = self.predictor.predict_all()
        shock = propagate_shock(event, source)
        for j, score in shock.severity_score.items():
            context[j]["shock"] = score
        if event == "AMBULANCE":
            for j in context:
                context[j]["emergency_delay"] = 15.0 if j in self.ambulance.route else 0.0
        model = build_qubo(context, self.previous_plans)
        qres = run_qaoa(model)
        plans = qres.selected_plans
        if qres.status == "FALLBACK":
            # Explicit fallback uses exact classical search; it is not reported as QAOA.
            from quantum.classical_baseline import exact_classical_qubo
            classical = exact_classical_qubo(model)
            plans = classical["selected_plan"]
        self.previous_plans = plans
        alert = None
        if event in ("VEHICLE_OBSTRUCTION", "ACCIDENT", "AMBULANCE"):
            alert = generate_alert(event, source or "J1",
                                   vehicle_id=("TN38AB1234" if event == "VEHICLE_OBSTRUCTION" else "AMB01" if event == "AMBULANCE" else ""),
                                   vehicle_model=("Sedan" if event == "VEHICLE_OBSTRUCTION" else "Ambulance" if event == "AMBULANCE" else "Unknown"),
                                   impact=shock.affected.get(source or "J1", "HIGH"),
                                   ai_action="Rolling optimization and coordinated signal control")
        emergency = {}
        if event == "AMBULANCE":
            decision = self.corridor.evaluate("J1", context)
            emergency = asdict(decision)
        self.metrics.record(time_seconds, event, context, plans, qres.execution_time, 0.0,
                            emergency_delay=sum(s["emergency_delay"] for s in context.values()))
        result = ScenarioResult(time_seconds, event, result_to_dict(qres), plans,
                                asdict(shock), emergency, alert)
        self.results.append(result)
        return result, preds

    def run(self):
        for event in EVENT_TIMELINE:
            if event["type"] in ("CROWD_SURGE", "RECOVERY"):
                continue
            self.step(event["type"], event["time"], event.get("junction"))
        return self.results
