def calculate_confidence(queue, capacity, speed, predicted_value, current_value):
    """Prototype model-confidence score; not a statistical probability."""
    capacity = max(float(capacity), 1.0)
    congestion = min(max(float(queue) / capacity, 0.0), 1.0)
    speed_stability = max(0.0, min(float(speed) / 60.0, 1.0))
    if current_value <= 0:
        change_stability = 0.5
    else:
        change = abs(predicted_value - current_value) / current_value
        change_stability = max(0.0, 1.0 - min(change, 1.0))
    confidence = (0.4 * (1.0 - congestion) + 0.3 * speed_stability + 0.3 * change_stability)
    return round(confidence * 100, 1)

def build_confidence_map(traffic_state, predictions):
    result = {}
    for junction, state in traffic_state.items():
        result[junction] = {}
        for horizon, predicted in predictions[junction].items():
            result[junction][horizon] = calculate_confidence(
                state["queue"], state["capacity"], state["speed"], predicted, state["vehicles"]
            )
    return result
