"""
SUMO -> Q-TRAFFIC traffic-state adapter.

Converts SUMO/TraCI-style observations into the common
traffic-state format expected by the Shree prediction module.
"""


def convert_sumo_observation(sumo_data, junction_mapping=None):
    """
    Convert SUMO traffic observations into Q-TRAFFIC format.

    Expected SUMO-style input:

    {
        "J1": {
            "vehicle_count": 30,
            "queue_length": 12,
            "mean_speed": 24,
            "capacity": 60,
            "signal": "NS_GREEN"
        }
    }

    Output:

    {
        "J1": {
            "vehicles": 30,
            "queue": 12,
            "speed": 24,
            "capacity": 60,
            "signal": "NS_GREEN"
        }
    }
    """

    if not isinstance(sumo_data, dict):
        raise TypeError("SUMO data must be a dictionary.")

    converted = {}

    for junction_id, data in sumo_data.items():

        if not isinstance(data, dict):
            raise ValueError(
                f"Traffic data for {junction_id} must be a dictionary."
            )

        converted[junction_id] = {
            "vehicles": data.get(
                "vehicle_count",
                data.get("vehicles", 0)
            ),
            "queue": data.get(
                "queue_length",
                data.get("queue", 0)
            ),
            "speed": data.get(
                "mean_speed",
                data.get("speed", 0)
            ),
            "capacity": data.get("capacity", 0),
            "signal": data.get(
                "signal",
                "UNKNOWN"
            )
        }

    return converted


def validate_sumo_observation(sumo_data):
    """
    Validate the minimum fields required from SUMO.
    """

    if not isinstance(sumo_data, dict):
        return False

    required_fields = [
        "vehicle_count",
        "queue_length",
        "mean_speed"
    ]

    for junction_id, data in sumo_data.items():

        if not isinstance(data, dict):
            return False

        for field in required_fields:
            if field not in data and field.replace(
                "_count", "s"
            ) not in data:
                return False

    return True