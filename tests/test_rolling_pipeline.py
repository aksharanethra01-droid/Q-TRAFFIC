from prediction.rolling_pipeline import (
    run_integrated_cycle,
    run_integrated_rolling_pipeline,
)


def state_t0():
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
        "J3": {
            "vehicles": 31,
            "queue": 15,
            "speed": 21,
            "capacity": 50,
            "signal": "NS_GREEN",
        },
    }


def state_t1():
    return {
        "J1": {
            "vehicles": 36,
            "queue": 16,
            "speed": 22,
            "capacity": 60,
            "signal": "NS_GREEN",
        },
        "J2": {
            "vehicles": 51,
            "queue": 27,
            "speed": 16,
            "capacity": 60,
            "signal": "EW_GREEN",
        },
        "J3": {
            "vehicles": 42,
            "queue": 21,
            "speed": 18,
            "capacity": 50,
            "signal": "NS_GREEN",
        },
    }


def test_integrated_cycle_without_previous_state():

    result = run_integrated_cycle(
        traffic_state=state_t0(),
        demand_multiplier=1.55,
    )

    assert "traffic_state" in result
    assert "predictions" in result
    assert "confidence" in result
    assert "shock_event" in result
    assert "shock_map" in result

    assert result["shock_event"]["detected"] is False


def test_integrated_cycle_detects_shock():

    result = run_integrated_cycle(
        traffic_state=state_t1(),
        demand_multiplier=1.55,
        previous_state=state_t0(),
    )

    assert result["shock_event"]["detected"] is True
    assert result["shock_event"]["source"] == "J3"

    assert result["shock_event"]["severity"] in {
        "MEDIUM",
        "HIGH",
    }

    assert result["shock_map"]["J3"] == 1.0


def test_integrated_rolling_pipeline():

    states = [
        state_t0(),
        state_t1(),
    ]

    results = run_integrated_rolling_pipeline(
        traffic_states=states,
        demand_multiplier=1.55,
    )

    assert len(results) == 2

    assert results[0]["step"] == 0
    assert results[1]["step"] == 1

    assert results[0]["shock_event"]["detected"] is False
    assert results[1]["shock_event"]["detected"] is True

    assert results[1]["shock_event"]["source"] == "J3"