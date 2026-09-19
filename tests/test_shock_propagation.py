from prediction.shock_propagation import propagate_shock


def test_accident_propagates():
    traffic = {
        "J2": {"vehicles": 40, "queue": 10, "speed": 20, "capacity": 60, "signal": "NS_GREEN"},
        "J3": {"vehicles": 40, "queue": 10, "speed": 20, "capacity": 60, "signal": "NS_GREEN"},
        "J4": {"vehicles": 40, "queue": 10, "speed": 20, "capacity": 60, "signal": "NS_GREEN"},
    }

    result = propagate_shock(
        traffic,
        {"type": "ACCIDENT", "junction": "J3", "severity": "HIGH"},
    )

    assert result["J3"] == 1.0
    assert result["J2"] > 0
    assert result["J4"] > 0
