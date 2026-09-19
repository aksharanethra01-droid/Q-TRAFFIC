from dataclasses import dataclass

@dataclass
class EmergencyVehicle:
    vehicle_id: str
    start: str
    destination: str
    priority: str = "HIGH"
    vehicle_type: str = "AMBULANCE"
    current_speed: float = 0.0
