def compare_results(classical_fixed, classical_adaptive, optimized):
    """
    Compare traffic performance of different approaches.
    """

    approaches = {
    "Fixed-Time": classical_fixed,
    "Adaptive": classical_adaptive,
    "Quantum-Hybrid Prototype": optimized
}

    print("\nTRAFFIC CONTROL COMPARISON")
    print("=" * 50)

    for name, metrics in approaches.items():

        print(f"\n{name}")
        print("-" * 30)

        print(f"Average Waiting Time : {metrics['average_waiting_time']} sec")
        print(f"Total Queue          : {metrics['total_queue']}")
        print(f"Throughput           : {metrics['throughput']}")

        if metrics.get("emergency_travel_time") is not None:
            print(f"Emergency Travel Time: {metrics['emergency_travel_time']} sec")

        if metrics.get("fuel") is not None:
            print(f"Fuel                 : {metrics['fuel']}")

        if metrics.get("co2") is not None:
            print(f"CO2                  : {metrics['co2']}")


if __name__ == "__main__":

    # Temporary test values only.
    # These will later be replaced by actual simulation results.

    fixed = {
        "average_waiting_time": 40,
        "total_queue": 80,
        "throughput": 90,
        "emergency_travel_time": 120,
        "fuel": 50,
        "co2": 120
    }

    adaptive = {
        "average_waiting_time": 32,
        "total_queue": 65,
        "throughput": 100,
        "emergency_travel_time": 105,
        "fuel": 45,
        "co2": 108
    }

    optimized = {
        "average_waiting_time": 28,
        "total_queue": 55,
        "throughput": 110,
        "emergency_travel_time": 90,
        "fuel": 40,
        "co2": 98
    }

    compare_results(
        fixed,
        adaptive,
        optimized
    )