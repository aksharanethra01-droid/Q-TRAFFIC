from prediction.demand_forecast import forecast_demand


def test_peak_event_increases_demand():
    traffic = {
        "J1": {"vehicles": 100},
        "J2": {"vehicles": 50},
    }

    result = forecast_demand(
        traffic,
        is_peak_hour=True,
        event_type="COLLEGE_EVENT",
        event_severity="HIGH",
    )

    assert result["J1"] > 100
    assert result["J2"] > 50
