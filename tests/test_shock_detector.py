from prediction.shock_detector import (
    calculate_changes,
    calculate_shock_score,
    classify_severity,
    detect_traffic_shock,
)


def test_calculate_changes():

    previous = {
        "J3": {
            "vehicles": 31,
            "queue": 15,
            "speed": 21,
        }
    }

    current = {
        "J3": {
            "vehicles": 42,
            "queue": 21,
            "speed": 18,
        }
    }

    changes = calculate_changes(
        previous,
        current,
    )

    assert changes["J3"]["vehicles"] == 11
    assert changes["J3"]["queue"] == 6
    assert changes["J3"]["speed"] == -3


def test_shock_score():

    change = {
        "vehicles": 11,
        "queue": 6,
        "speed": -3,
    }

    score = calculate_shock_score(change)

    assert score > 0


def test_severity():

    assert classify_severity(0.5) == "LOW"
    assert classify_severity(1.0) == "MEDIUM"
    assert classify_severity(2.0) == "HIGH"


def test_detect_traffic_shock():

    previous = {
        "J1": {
            "vehicles": 30,
            "queue": 12,
            "speed": 24,
        },
        "J3": {
            "vehicles": 31,
            "queue": 15,
            "speed": 21,
        },
    }

    current = {
        "J1": {
            "vehicles": 32,
            "queue": 13,
            "speed": 23,
        },
        "J3": {
            "vehicles": 50,
            "queue": 25,
            "speed": 17,
        },
    }

    result = detect_traffic_shock(
        previous,
        current,
    )

    assert result["detected"] is True
    assert result["source"] == "J3"
    assert result["severity"] in {
        "MEDIUM",
        "HIGH",
    }