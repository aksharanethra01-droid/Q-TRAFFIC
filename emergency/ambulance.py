from dataclasses import dataclass
from typing import List

@dataclass
class EmergencyVehicle:
    vehicle_id: str = "AMB01"
    vehicle_type: str = "AMBULANCE"
    route: List[str] = None
    current_junction: str = "J1"
    priority: str = "HIGH"
    estimated_arrival: float = 0.0
    active: bool = True

    def __post_init__(self):
        if self.route is None:
            self.route = ["J1", "J2", "J3", "J4"]

    def next_junction(self):
        try:
            idx = self.route.index(self.current_junction)
            return self.route[idx + 1] if idx + 1 < len(self.route) else None
        except ValueError:
            return None

    def move_to(self, junction: str):
        if junction not in self.route:
            raise ValueError("Junction is not on emergency route")
        self.current_junction = junction
        if junction == self.route[-1]:
            self.active = False
