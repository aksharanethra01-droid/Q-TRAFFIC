from dataclasses import dataclass, asdict
from typing import Dict, List
from collections import deque
import math

HORIZONS = [30, 60, 120, 300]
LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")

@dataclass
class Prediction:
    horizon_seconds: int
    predicted_vehicles: float
    predicted_queue: float
    predicted_waiting: float
    congestion_level: str

def _level(v_ratio: float, q_ratio: float) -> str:
    score = max(v_ratio, q_ratio)
    if score >= 1.15:
        return "CRITICAL"
    if score >= 0.85:
        return "HIGH"
    if score >= 0.55:
        return "MEDIUM"
    return "LOW"

class TrafficPredictor:
    def __init__(self, window: int = 6):
        self.window = window
        self.history: Dict[str, deque] = {}

    def observe(self, junction_id: str, vehicles: float, queue: float, waiting: float, capacity: float):
        self.history.setdefault(junction_id, deque(maxlen=self.window)).append(
            {"vehicles": float(vehicles), "queue": float(queue), "waiting": float(waiting), "capacity": float(capacity)}
        )

    def predict(self, junction_id: str) -> List[Prediction]:
        hist = list(self.history.get(junction_id, []))
        if not hist:
            raise ValueError(f"No observations for {junction_id}")
        weights = list(range(1, len(hist) + 1))
        total = sum(weights)
        avg = {k: sum(w * x[k] for w, x in zip(weights, hist)) / total for k in ("vehicles", "queue", "waiting")}
        if len(hist) >= 2:
            prev, last = hist[-2], hist[-1]
            trend = {k: (last[k] - prev[k]) for k in ("vehicles", "queue", "waiting")}
        else:
            trend = {k: 0.0 for k in ("vehicles", "queue", "waiting")}
        cap = max(hist[-1]["capacity"], 1.0)
        out = []
        for h in HORIZONS:
            steps = h / 30.0
            vals = {}
            for k in ("vehicles", "queue", "waiting"):
                # Weighted moving average + trend extrapolation with a dampening term.
                vals[k] = max(0.0, avg[k] + trend[k] * steps * (0.70 / (1 + 0.15 * steps)))
            out.append(Prediction(h, vals["vehicles"], vals["queue"], vals["waiting"],
                                  _level(vals["vehicles"] / cap, vals["queue"] / cap)))
        return out

    def predict_all(self) -> Dict[str, List[Prediction]]:
        return {j: self.predict(j) for j in self.history}
