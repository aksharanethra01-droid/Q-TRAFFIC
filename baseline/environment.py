"""
Q-TRAFFIC Environmental Impact Model

Estimates fuel consumption and CO2 emissions
from simulated traffic waiting time and queue length.

These are prototype simulation estimates,
not real-world measurements.
"""


def estimate_fuel(
    waiting_time,
    total_queue,
    throughput
):
    """
    Estimate fuel consumption.

    The model uses:
    - waiting time
    - queue length
    - throughput

    Returns fuel estimate in litres.
    """

    idle_fuel = waiting_time * 0.02

    queue_fuel = total_queue * 0.01

    movement_fuel = throughput * 0.03

    fuel = (
        idle_fuel
        + queue_fuel
        + movement_fuel
    )

    return round(fuel, 2)


def estimate_co2(fuel):
    """
    Estimate CO2 emissions from fuel consumption.

    Prototype conversion factor:
    1 litre fuel ≈ 2.31 kg CO2
    """

    co2 = fuel * 2.31

    return round(co2, 2)


def calculate_environment_metrics(
    waiting_time,
    total_queue,
    throughput
):
    """
    Calculate both fuel and CO2 estimates.
    """

    fuel = estimate_fuel(
        waiting_time,
        total_queue,
        throughput
    )

    co2 = estimate_co2(
        fuel
    )

    return {
        "fuel": fuel,
        "co2": co2
    }


if __name__ == "__main__":

    result = calculate_environment_metrics(
        waiting_time=18.0,
        total_queue=61,
        throughput=155
    )

    print("\nEnvironmental Metrics")
    print("-" * 40)

    print(
        "Fuel :",
        result["fuel"],
        "litres"
    )

    print(
        "CO2  :",
        result["co2"],
        "kg"
    )