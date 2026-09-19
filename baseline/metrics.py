"""
Q-TRAFFIC Traffic Performance Metrics

Calculates common performance metrics for:
- Fixed-Time control
- Adaptive control
- Quantum-Hybrid control

The function does NOT generate or assume performance values.
All values must come from an actual simulation/controller.
"""


def calculate_metrics(
    waiting_times,
    queues,
    throughput,
    emergency_travel_time=None,
    fuel=None,
    co2=None
):
    """
    Calculate traffic performance metrics.

    Parameters
    ----------
    waiting_times : list
        Waiting time values collected from the simulation.

    queues : list
        Queue lengths collected from junctions.

    throughput : int/float
        Number of vehicles successfully processed.

    emergency_travel_time : float, optional
        Emergency vehicle travel time.

    fuel : float, optional
        Fuel consumption.

    co2 : float, optional
        CO2 emissions.

    Returns
    -------
    dict
        Standardized traffic performance metrics.
    """

    # Average waiting time
    if waiting_times:
        average_waiting_time = sum(waiting_times) / len(waiting_times)
    else:
        average_waiting_time = 0.0

    # Total queue across all junctions
    total_queue = sum(queues) if queues else 0

    return {
        "average_waiting_time": round(average_waiting_time, 2),
        "total_queue": total_queue,
        "throughput": throughput,
        "emergency_travel_time": emergency_travel_time,
        "fuel": fuel,
        "co2": co2
    }


def validate_metrics(metrics):
    """
    Check whether a metrics dictionary contains
    the required fields for comparison.
    """

    required_fields = [
        "average_waiting_time",
        "total_queue",
        "throughput"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in metrics
    ]

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields
    }