from data.schemas import TRAFFIC_STATE


def adaptive_signal(traffic_state):
    """
    Simple rule-based adaptive traffic signal controller.

    Higher queue -> longer green time.

    Constraints:
    - Minimum green: 30 seconds
    - Maximum green: 50 seconds
    - Cycle length: 60 seconds
    """

    signal_plan = {}

    for junction, data in traffic_state.items():

        queue = data["queue"]

        if queue >= 20:
            green = 50

        elif queue >= 10:
            green = 45

        else:
            green = 30

        red = 60 - green

        signal_plan[junction] = {
            "green": green,
            "red": red
        }

    return signal_plan


if __name__ == "__main__":

    result = adaptive_signal(TRAFFIC_STATE)

    print("\nCLASSICAL ADAPTIVE SIGNAL PLAN")
    print("--------------------------------")

    for junction, plan in result.items():

        print(
            f"{junction}: "
            f"Green = {plan['green']} sec | "
            f"Red = {plan['red']} sec"
        )