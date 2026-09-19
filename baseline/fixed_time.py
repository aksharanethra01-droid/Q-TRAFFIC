def fixed_time_signal():
    """
    Classical fixed-time traffic signal baseline.

    Every junction follows a fixed:
    - 30 second green
    - 30 second red
    """

    signal_plan = {
        "J1": {
            "green": 30,
            "red": 30
        },
        "J2": {
            "green": 30,
            "red": 30
        },
        "J3": {
            "green": 30,
            "red": 30
        },
        "J4": {
            "green": 30,
            "red": 30
        }
    }

    return signal_plan


if __name__ == "__main__":

    result = fixed_time_signal()

    print("\nCLASSICAL FIXED-TIME SIGNAL PLAN")
    print("--------------------------------")

    for junction, plan in result.items():

        print(
            f"{junction}: "
            f"Green = {plan['green']} sec | "
            f"Red = {plan['red']} sec"
        )