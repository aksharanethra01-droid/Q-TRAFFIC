from dataclasses import dataclass


@dataclass
class TrafficAnomaly:
    junction: str
    anomaly_type: str
    severity: str
    score: float
    reason: str


class TrafficMonitor:

    def __init__(self):
        self.previous_state = {}

    def analyze(self, junction, state):

        vehicles = float(state.get("vehicles", 0))
        queue = float(state.get("queue", 0))
        waiting = float(state.get("waiting", 0))
        capacity = max(float(state.get("capacity", 50)), 1.0)

        congestion = vehicles / capacity

        if queue < 3 and congestion < 0.30 and waiting < 30:

            result = TrafficAnomaly(
                junction=junction,
                anomaly_type="NORMAL",
                severity="LOW",
                score=0.0,
                reason="Traffic conditions are within normal limits."
            )

        else:

            score = 0.0

            if queue >= 3:
                score += 0.30

            if congestion >= 0.30:
                score += 0.30

            if waiting >= 30:
                score += 0.30

            result = TrafficAnomaly(
                junction=junction,
                anomaly_type="CONGESTION",
                severity="MEDIUM",
                score=min(score, 1.0),
                reason=(
                    "Queue, congestion or waiting time "
                    "has exceeded the normal threshold."
                )
            )

        self.previous_state[junction] = state.copy()

        return result

    def analyze_network(self, context):

        results = {}

        for junction, state in context.items():
            results[junction] = self.analyze(
                junction,
                state
            )

        return results