def estimate_fuel(waiting_seconds: float, idling_vehicles: float, vehicle_count: float) -> float:
    # SIMULATION ESTIMATE: litres, transparent proportional model.
    return max(0.0, waiting_seconds * 0.0007 + idling_vehicles * 0.015 + vehicle_count * 0.002)
