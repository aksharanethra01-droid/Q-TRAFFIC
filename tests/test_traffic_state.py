from prediction.traffic_state import calculate_congestion_ratio, validate_traffic_state


def test_validate_traffic_state():
    data = {
        "J1": {
            "vehicles": 20,
            "queue": 10,
            "speed": 25,
            "capacity": 50,
            "signal": "NS_GREEN",
        }
    }
    validate_traffic_state(data)


def test_congestion_ratio():
    state = {"vehicles": 20, "queue": 25, "speed": 25, "capacity": 50}
    assert calculate_congestion_ratio(state) == 0.5
