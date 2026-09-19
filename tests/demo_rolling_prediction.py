import json

from prediction.rolling_predictor import run_rolling_prediction


STATE_T0 = {
    "J1": {
        "vehicles": 30,
        "queue": 12,
        "speed": 24,
        "capacity": 60,
        "signal": "NS_GREEN",
    },
    "J2": {
        "vehicles": 45,
        "queue": 22,
        "speed": 18,
        "capacity": 60,
        "signal": "EW_GREEN",
    },
    "J3": {
        "vehicles": 31,
        "queue": 15,
        "speed": 21,
        "capacity": 50,
        "signal": "NS_GREEN",
    },
}

STATE_T1 = {
    "J1": {
        "vehicles": 36,
        "queue": 16,
        "speed": 22,
        "capacity": 60,
        "signal": "NS_GREEN",
    },
    "J2": {
        "vehicles": 51,
        "queue": 27,
        "speed": 16,
        "capacity": 60,
        "signal": "EW_GREEN",
    },
    "J3": {
        "vehicles": 42,
        "queue": 21,
        "speed": 18,
        "capacity": 50,
        "signal": "NS_GREEN",
    },
}

STATE_T2 = {
    "J1": {
        "vehicles": 44,
        "queue": 22,
        "speed": 19,
        "capacity": 60,
        "signal": "NS_GREEN",
    },
    "J2": {
        "vehicles": 60,
        "queue": 34,
        "speed": 13,
        "capacity": 60,
        "signal": "EW_GREEN",
    },
    "J3": {
        "vehicles": 55,
        "queue": 30,
        "speed": 15,
        "capacity": 50,
        "signal": "NS_GREEN",
    },
}


def main():

    traffic_states = [
        STATE_T0,
        STATE_T1,
        STATE_T2,
    ]

    results = run_rolling_prediction(
        traffic_states=traffic_states,
        demand_multiplier=1.55,
    )

    print("\n" + "=" * 60)
    print("Q-TRAFFIC — ROLLING PREDICTION DEMO")
    print("=" * 60)

    for result in results:

        print(f"\nSimulation Step: {result['step']}")

        print("\nCurrent Vehicles:")

        for junction, data in result["traffic_state"].items():
            print(
                f"  {junction}: "
                f"{data['vehicles']} vehicles"
            )

        print("\nPredicted Traffic:")

        for junction, prediction in result["predictions"].items():
            print(
                f"  {junction}: "
                f"1min={prediction['1min']}, "
                f"3min={prediction['3min']}, "
                f"5min={prediction['5min']}"
            )

    print("\n" + "=" * 60)
    print("ROLLING PREDICTION COMPLETED")
    print("=" * 60)

    print(
        json.dumps(
            results,
            indent=2
        )
    )


if __name__ == "__main__":
    main()