"""
Q-TRAFFIC Emergency Green Corridor

Prototype emergency vehicle routing and signal priority module.

This module:
1. Creates an emergency route through the junction network.
2. Identifies junctions that require green priority.
3. Generates a green-corridor signal plan.

This is a prototype and does not use live traffic data.
"""


NETWORK_ROUTES = {
    ("J1", "J4"): ["J1", "J2", "J3", "J4"],
    ("J1", "J5"): ["J1", "J2", "J3", "J5"],
    ("J2", "J4"): ["J2", "J3", "J4"],
    ("J2", "J5"): ["J2", "J3", "J5"],
}


def find_emergency_route(start, destination):
    """
    Find a predefined emergency route
    between connected junctions.
    """

    route = NETWORK_ROUTES.get((start, destination))

    if route is None:
        raise ValueError(
            f"No emergency route available from {start} to {destination}"
        )

    return route


def create_green_corridor(route):
    """
    Give green priority to every junction
    along the emergency route.
    """

    corridor = {}

    for junction in route:
        corridor[junction] = {
            "priority": "EMERGENCY",
            "signal": "GREEN",
            "green_time": 50
        }

    return corridor


def build_emergency_plan(
    vehicle,
    start,
    destination,
    priority="HIGH"
):
    """
    Build a complete emergency green corridor plan.
    """

    route = find_emergency_route(
        start,
        destination
    )

    green_corridor = create_green_corridor(
        route
    )

    return {
        "vehicle": vehicle,
        "start": start,
        "destination": destination,
        "priority": priority,
        "route": route,
        "green_corridor": green_corridor,
        "status": "ACTIVE"
    }


if __name__ == "__main__":

    result = build_emergency_plan(
        vehicle="AMB01",
        start="J1",
        destination="J4",
        priority="HIGH"
    )

    print("\n" + "=" * 60)
    print("Q-TRAFFIC EMERGENCY GREEN CORRIDOR")
    print("=" * 60)

    print("Vehicle     :", result["vehicle"])
    print("Start       :", result["start"])
    print("Destination :", result["destination"])
    print("Priority    :", result["priority"])
    print("Status      :", result["status"])

    print("\nEmergency Route:")
    print(" -> ".join(result["route"]))

    print("\nGreen Corridor:")

    for junction, signal in result["green_corridor"].items():
        print(
            f"{junction} | "
            f"Signal: {signal['signal']} | "
            f"Priority: {signal['priority']} | "
            f"Green: {signal['green_time']} sec"
        )