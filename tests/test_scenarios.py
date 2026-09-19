from config.scenarios import get_scenario

def test_coimbatore_textile_festival():
    scenario = get_scenario("Coimbatore", "TEXTILE_FESTIVAL")
    assert scenario["event_type"] == "PUBLIC_EVENT"
    assert scenario["demand_multiplier"] > 1.0
