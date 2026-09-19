from prediction.rolling_predictor import (
    run_prediction_cycle,
    run_rolling_prediction,
)


def sample_state():
    return {
        "J1": {
            "vehicles": 30,
            "queue": 12,
            "speed": 24,
            "capacity": 60,
            "signal": "NS_GREEN",
        },
        "J2": {
            "vehicles": 45,
            "queue": 22,
            "speed": 18,
            "capacity": 60,
            "signal": "EW_GREEN",
        },
    }


def increased_state():
    return {
        "J1": {
            "vehicles": 40,
            "queue": 18,
            "speed": 20,
            "capacity": 60,
            "signal": "NS_GREEN",
        },
        "J2": {
            "vehicles": 55,
            "queue": 30,
            "speed": 15,
            "capacity": 60,
            "signal": "EW_GREEN",
        },
    }


def test_single_prediction_cycle():

    result = run_prediction_cycle(
        sample_state(),
        demand_multiplier=1.0,
    )

    assert "predictions" in result
    assert "confidence" in result
    assert "shock_map" in result

    assert "J1" in result["predictions"]


def test_rolling_prediction():

    states = [
        sample_state(),
        increased_state(),
    ]

    results = run_rolling_prediction(
        states,
        demand_multiplier=1.0,
    )

    assert len(results) == 2

    assert results[0]["step"] == 0
    assert results[1]["step"] == 1

    assert "predictions" in results[0]
    assert "predictions" in results[1]

    # Traffic increased between the two snapshots.
    assert (
        results[1]["traffic_state"]["J1"]["vehicles"]
        >
        results[0]["traffic_state"]["J1"]["vehicles"]
    )