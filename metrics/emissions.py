def estimate_co2(fuel_litres: float) -> float:
    # SIMULATION ESTIMATE: 2.31 kg CO2 per litre of petrol-equivalent fuel.
    return max(0.0, fuel_litres * 2.31)
