from dataclasses import dataclass, asdict
from typing import Dict, Any
from datetime import datetime, timezone
import json

@dataclass
class TrafficState:
    junction_id: str
    vehicles: int
    density: float
    queue_length: float
    road_capacity: int
    waiting_time: float
    throughput: float
    signal_state: str
    timestamp: str

    def validate(self) -> None:
        if not self.junction_id:
            raise ValueError("junction_id is required")
        if self.vehicles < 0 or self.queue_length < 0 or self.waiting_time < 0:
            raise ValueError("traffic counts cannot be negative")
        if self.road_capacity <= 0:
            raise ValueError("road_capacity must be positive")
        if self.density < 0 or self.throughput < 0:
            raise ValueError("density/throughput cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def deserialize(cls, payload: str) -> "TrafficState":
        obj = cls(**json.loads(payload))
        obj.validate()
        return obj

def create_state(junction_id: str, vehicles: int, queue_length: float, capacity: int,
                 waiting_time: float, throughput: float, signal_state: str = "NS_GREEN",
                 timestamp: str | None = None) -> TrafficState:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    state = TrafficState(junction_id, int(vehicles), float(vehicles / capacity),
                         float(queue_length), int(capacity), float(waiting_time),
                         float(throughput), signal_state, ts)
    state.validate()
    return state

def states_to_contract(states: Dict[str, TrafficState]) -> Dict[str, dict]:
    return {k: v.to_dict() for k, v in states.items()}

def states_from_contract(data: Dict[str, dict]) -> Dict[str, TrafficState]:
    return {k: TrafficState(**v) for k, v in data.items()}
