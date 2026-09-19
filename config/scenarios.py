SCENARIOS = {
    "Coimbatore": {
        "TEXTILE_FESTIVAL": {
            "description": "Simulated Coimbatore-inspired textile/commercial event scenario.",
            "demand_multiplier": 1.25,
            "event_type": "PUBLIC_EVENT",
            "event_severity": "HIGH",
            "default_incident": {"type": "ACCIDENT", "junction": "J3", "severity": "HIGH"},
        },
        "SCHOOL_PEAK": {
            "description": "Simulated school-opening/closing peak scenario.",
            "demand_multiplier": 1.15,
            "event_type": "SCHOOL_PEAK",
            "event_severity": "MEDIUM",
            "default_incident": None,
        },
        "NORMAL": {
            "description": "Normal simulated traffic scenario.",
            "demand_multiplier": 1.0,
            "event_type": "NORMAL",
            "event_severity": "LOW",
            "default_incident": None,
        },
    }
}

def get_scenario(location: str, scenario: str) -> dict:
    if location not in SCENARIOS:
        raise ValueError(f"Unsupported simulated location: {location}")
    if scenario not in SCENARIOS[location]:
        raise ValueError(f"Unsupported scenario '{scenario}' for {location}")
    return SCENARIOS[location][scenario]
