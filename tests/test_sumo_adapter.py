from integration.sumo_adapter import convert_sumo_observation


def test_sumo_conversion():

    sumo_data = {
        "J1": {
            "vehicle_count": 30,
            "queue_length": 12,
            "mean_speed": 24,
            "capacity": 60,
            "signal": "NS_GREEN"
        },
        "J2": {
            "vehicle_count": 45,
            "queue_length": 22,
            "mean_speed": 18,
            "capacity": 60,
            "signal": "EW_GREEN"
        }
    }

    result = convert_sumo_observation(sumo_data)

    assert result["J1"]["vehicles"] == 30
    assert result["J1"]["queue"] == 12
    assert result["J1"]["speed"] == 24

    assert result["J2"]["vehicles"] == 45
    assert result["J2"]["queue"] == 22
    assert result["J2"]["speed"] == 18