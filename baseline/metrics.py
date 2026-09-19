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

    Parameters:
        waiting_times: list of vehicle waiting times
        queues: list of queue lengths
        throughput: number of vehicles processed
        emergency_travel_time: emergency vehicle travel time
        fuel: fuel consumption
        co2: CO2 emissions
    """

    # Average waiting time
    if waiting_times:
        average_waiting = sum(waiting_times) / len(waiting_times)
    else:
        average_waiting = 0

    # Total queue
    total_queue = sum(queues)

    metrics = {
        "average_waiting_time": round(average_waiting, 2),
        "total_queue": total_queue,
        "throughput": throughput,
        "emergency_travel_time": emergency_travel_time,
        "fuel": fuel,
        "co2": co2
    }

    return metrics


if __name__ == "__main__":

    # Temporary test data.
    # Later this will come from SUMO.
    waiting_times = [20, 30, 15, 25, 10]
    queues = [12, 20, 15, 8]

    result = calculate_metrics(
        waiting_times=waiting_times,
        queues=queues,
        throughput=100,
        emergency_travel_time=85,
        fuel=42.5,
        co2=98.3
    )

    print("\nTRAFFIC PERFORMANCE METRICS")
    print("--------------------------------")

    for metric, value in result.items():
        print(f"{metric}: {value}")