"""
Q-TRAFFIC Location-Based Simulation Scenarios

These are simulated, location-inspired traffic scenarios.
They are NOT live traffic data.
"""


LOCATION_SCENARIOS = {

    "Coimbatore": {
        "description": "Textile and commercial traffic inspired scenario",

        "junctions": {
            "J1": {
                "name": "Gandhipuram",
                "vehicles": 55,
                "queue": 28,
                "speed": 18,
                "capacity": 60,
                "signal": "NS_GREEN"
            },

            "J2": {
                "name": "Ukkadam",
                "vehicles": 48,
                "queue": 22,
                "speed": 20,
                "capacity": 60,
                "signal": "EW_GREEN"
            },

            "J3": {
                "name": "Singanallur",
                "vehicles": 42,
                "queue": 19,
                "speed": 23,
                "capacity": 60,
                "signal": "NS_GREEN"
            },

            "J4": {
                "name": "Peelamedu",
                "vehicles": 36,
                "queue": 14,
                "speed": 25,
                "capacity": 60,
                "signal": "EW_GREEN"
            }
        }
    },


    "Chennai": {
        "description": "Dense metropolitan traffic inspired scenario",

        "junctions": {
            "J1": {
                "name": "T Nagar",
                "vehicles": 65,
                "queue": 34,
                "speed": 15,
                "capacity": 70,
                "signal": "NS_GREEN"
            },

            "J2": {
                "name": "Guindy",
                "vehicles": 58,
                "queue": 29,
                "speed": 17,
                "capacity": 70,
                "signal": "EW_GREEN"
            },

            "J3": {
                "name": "Velachery",
                "vehicles": 52,
                "queue": 25,
                "speed": 19,
                "capacity": 65,
                "signal": "NS_GREEN"
            },

            "J4": {
                "name": "Adyar",
                "vehicles": 45,
                "queue": 20,
                "speed": 22,
                "capacity": 65,
                "signal": "EW_GREEN"
            }
        }
    },


    "Madurai": {
        "description": "Urban and tourist traffic inspired scenario",

        "junctions": {
            "J1": {
                "name": "Mattuthavani",
                "vehicles": 50,
                "queue": 24,
                "speed": 21,
                "capacity": 60,
                "signal": "NS_GREEN"
            },

            "J2": {
                "name": "Periyar",
                "vehicles": 46,
                "queue": 21,
                "speed": 20,
                "capacity": 60,
                "signal": "EW_GREEN"
            },

            "J3": {
                "name": "Goripalayam",
                "vehicles": 39,
                "queue": 17,
                "speed": 24,
                "capacity": 60,
                "signal": "NS_GREEN"
            },

            "J4": {
                "name": "Thiruppalai",
                "vehicles": 32,
                "queue": 12,
                "speed": 26,
                "capacity": 60,
                "signal": "EW_GREEN"
            }
        }
    },


    "Salem": {
        "description": "Highway-connected urban traffic inspired scenario",

        "junctions": {
            "J1": {
                "name": "Five Roads",
                "vehicles": 52,
                "queue": 25,
                "speed": 20,
                "capacity": 65,
                "signal": "NS_GREEN"
            },

            "J2": {
                "name": "New Bus Stand",
                "vehicles": 44,
                "queue": 19,
                "speed": 23,
                "capacity": 65,
                "signal": "EW_GREEN"
            },

            "J3": {
                "name": "Hasthampatti",
                "vehicles": 38,
                "queue": 15,
                "speed": 25,
                "capacity": 60,
                "signal": "NS_GREEN"
            },

            "J4": {
                "name": "Fairlands",
                "vehicles": 30,
                "queue": 11,
                "speed": 27,
                "capacity": 60,
                "signal": "EW_GREEN"
            }
        }
    }
}


def get_location_scenario(location):
    """
    Return a copy of the selected location scenario.
    """

    if location not in LOCATION_SCENARIOS:
        raise ValueError(f"Unknown location: {location}")

    import copy

    return copy.deepcopy(LOCATION_SCENARIOS[location])


if __name__ == "__main__":

    for location in LOCATION_SCENARIOS:

        scenario = get_location_scenario(location)

        print(f"\n{location}")
        print("-" * 40)
        print(scenario["description"])

        for junction, data in scenario["junctions"].items():
            print(
                f"{junction} - {data['name']} | "
                f"Vehicles: {data['vehicles']} | "
                f"Queue: {data['queue']} | "
                f"Speed: {data['speed']} km/h"
            )