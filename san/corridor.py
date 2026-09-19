def build_green_corridor(route, priority="HIGH"):
    return {
        "priority": priority,
        "corridor": list(route or []),
        "status": "READY" if route else "NO_ROUTE"
    }


def junction_states(route, status="ACTIVE"):
    return {
        j: ("GREEN" if status == "ACTIVE" else "NORMAL")
        for j in (route or [])
    }


def clearance_check(junction_state):
    clear = (
        float(junction_state.get("queue", 0)) <= 5
        and bool(junction_state.get("downstream_clear", True))
    )

    return {
        "clear": clear,
        "action": "PROCEED" if clear else "HOLD_OR_MODIFY"
    }


def route_clearance_check(route, traffic_state):
    """
    Check the actual traffic conditions
    on every junction in the emergency route.
    """

    if not route:
        return {
            "clear": False,
            "action": "NO_ROUTE",
            "junctions": []
        }

    route_data = []

    for junction in route:

        values = traffic_state["junctions"].get(junction, {})

        queue = float(values.get("queue", 0))
        predicted = float(values.get("predicted", 0))
        capacity = float(values.get("capacity", 1))

        route_data.append({
            "junction": junction,
            "queue": queue,
            "predicted": predicted,
            "capacity": capacity,
            "within_capacity": predicted <= capacity
        })

    clear = all(
        item["queue"] <= 15
        and item["within_capacity"]
        for item in route_data
    )

    return {
        "clear": clear,
        "action": "PROCEED" if clear else "HOLD_OR_MODIFY",
        "junctions": route_data
    }