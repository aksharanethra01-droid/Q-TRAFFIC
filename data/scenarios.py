"""
Q-TRAFFIC Scenario Engine

Applies simulated traffic events to a selected
Tamil Nadu location scenario.

These are simulation scenarios, NOT live traffic data.
"""

from data.locations import get_location_scenario


SCENARIOS = [
    "Normal Traffic",
    "School Peak",
    "Textile Festival",
    "Accident",
    "Vehicle Obstruction",
    "Ambulance Emergency"
]


def apply_scenario(location, scenario):
    """
    Apply a traffic scenario to a location.

    Returns:
        Modified traffic state and event information.
    """

    state = get_location_scenario(location)

    junctions = state["junctions"]

    event = {
        "type": "NONE",
        "junction": None,
        "severity": None,
        "vehicle": None
    }

    # --------------------------------------------------
    # NORMAL TRAFFIC
    # --------------------------------------------------

    if scenario == "Normal Traffic":

        event["type"] = "NONE"


    # --------------------------------------------------
    # SCHOOL PEAK
    # --------------------------------------------------

    elif scenario == "School Peak":

        # Increased traffic around selected junctions
        for junction in ["J1", "J2"]:

            junctions[junction]["vehicles"] += 15
            junctions[junction]["queue"] += 8
            junctions[junction]["speed"] -= 4

        event["type"] = "SCHOOL_PEAK"


    # --------------------------------------------------
    # TEXTILE FESTIVAL
    # --------------------------------------------------

    elif scenario == "Textile Festival":

        # Stronger commercial traffic
        for junction in ["J1", "J2", "J3"]:

            junctions[junction]["vehicles"] += 20
            junctions[junction]["queue"] += 10
            junctions[junction]["speed"] -= 5

        event["type"] = "TEXTILE_FESTIVAL"


    # --------------------------------------------------
    # ACCIDENT
    # --------------------------------------------------

    elif scenario == "Accident":

        # Accident occurs at J3
        accident_junction = "J3"

        junctions[accident_junction]["vehicles"] += 10
        junctions[accident_junction]["queue"] += 20
        junctions[accident_junction]["speed"] -= 10

        event["type"] = "ACCIDENT"
        event["junction"] = accident_junction
        event["severity"] = "HIGH"


    # --------------------------------------------------
    # VEHICLE OBSTRUCTION
    # --------------------------------------------------

    elif scenario == "Vehicle Obstruction":

        obstruction_junction = "J2"

        junctions[obstruction_junction]["vehicles"] += 8
        junctions[obstruction_junction]["queue"] += 15
        junctions[obstruction_junction]["speed"] -= 8

        event["type"] = "VEHICLE_OBSTRUCTION"
        event["junction"] = obstruction_junction
        event["severity"] = "MEDIUM"


    # --------------------------------------------------
    # AMBULANCE EMERGENCY
    # --------------------------------------------------

    elif scenario == "Ambulance Emergency":

        event["type"] = "AMBULANCE"
        event["vehicle"] = "AMB01"
        event["severity"] = "HIGH"

        event["start"] = "J1"
        event["destination"] = "J4"

        # Small traffic increase caused by emergency situation
        junctions["J1"]["vehicles"] += 5
        junctions["J1"]["queue"] += 3


    else:

        raise ValueError(
            f"Unknown scenario: {scenario}"
        )


    # Prevent unrealistic negative speeds
    for junction in junctions:

        if junctions[junction]["speed"] < 5:
            junctions[junction]["speed"] = 5

        if junctions[junction]["queue"] < 0:
            junctions[junction]["queue"] = 0


    return {
        "location": location,
        "scenario": scenario,
        "description": state["description"],
        "junctions": junctions,
        "event": event
    }


if __name__ == "__main__":

    location = "Coimbatore"

    for scenario in SCENARIOS:

        result = apply_scenario(
            location,
            scenario
        )

        print("\n" + "=" * 60)
        print(f"LOCATION : {location}")
        print(f"SCENARIO : {scenario}")
        print("=" * 60)

        event = result["event"]

        print(f"Event Type : {event['type']}")

        if event["junction"]:
            print(f"Event Junction : {event['junction']}")

        print("\nTraffic State:")

        for junction, data in result["junctions"].items():

            print(
                f"{junction} - {data['name']} | "
                f"Vehicles: {data['vehicles']} | "
                f"Queue: {data['queue']} | "
                f"Speed: {data['speed']} km/h"
            )