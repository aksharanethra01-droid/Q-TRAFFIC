from pathlib import Path
import csv


class MetricsCollector:

    def __init__(self, output_file=None):

        base = Path(__file__).resolve().parent.parent

        self.output_file = Path(
            output_file
            or base / "outputs" / "metrics.csv"
        )

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.records = []

    def record(
        self,
        time_seconds,
        event,
        context,
        plans,
        qaoa_time=0.0,
        throughput=0.0,
        emergency_delay=0.0
    ):

        total_vehicles = 0.0
        total_queue = 0.0
        total_waiting = 0.0
        total_fuel = 0.0
        total_co2 = 0.0

        for state in context.values():

            vehicles = float(
                state.get("vehicles", 0.0)
            )

            queue = float(
                state.get("queue", 0.0)
            )

            waiting = float(
                state.get("waiting", 0.0)
            )

            capacity = max(
                float(
                    state.get("capacity", 50.0)
                ),
                1.0
            )

            congestion = min(
                vehicles / capacity,
                1.0
            )

            fuel = (
                waiting * 0.035
                + vehicles * 0.004
                + congestion * 0.02
            )

            co2 = (
                waiting * 0.09
                + vehicles * 0.011
                + congestion * 0.05
            )

            total_vehicles += vehicles
            total_queue += queue
            total_waiting += waiting
            total_fuel += fuel
            total_co2 += co2

        record = {
            "time_seconds": time_seconds,
            "event": event,
            "vehicles": round(
                total_vehicles,
                3
            ),
            "queue": round(
                total_queue,
                3
            ),
            "waiting_time": round(
                total_waiting,
                3
            ),
            "throughput": round(
                float(throughput),
                3
            ),
            "fuel": round(
                total_fuel,
                3
            ),
            "co2": round(
                total_co2,
                3
            ),
            "emergency_delay": round(
                float(emergency_delay),
                3
            ),
            "qaoa_time": round(
                float(qaoa_time),
                6
            ),
            "plans": str(
                plans
            )
        }

        self.records.append(record)

        self._write()

        return record

    def _write(self):

        fieldnames = [
            "time_seconds",
            "event",
            "vehicles",
            "queue",
            "waiting_time",
            "throughput",
            "fuel",
            "co2",
            "emergency_delay",
            "qaoa_time",
            "plans"
        ]

        with open(
            self.output_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(
                self.records
            )

    def summary(self):

        if not self.records:
            return {
                "average_waiting_time": 0.0,
                "average_queue": 0.0,
                "average_throughput": 0.0,
                "total_fuel": 0.0,
                "total_co2": 0.0,
                "total_emergency_delay": 0.0
            }

        count = len(
            self.records
        )

        return {
            "average_waiting_time": round(
                sum(
                    r["waiting_time"]
                    for r in self.records
                ) / count,
                3
            ),
            "average_queue": round(
                sum(
                    r["queue"]
                    for r in self.records
                ) / count,
                3
            ),
            "average_throughput": round(
                sum(
                    r["throughput"]
                    for r in self.records
                ) / count,
                3
            ),
            "total_fuel": round(
                sum(
                    r["fuel"]
                    for r in self.records
                ),
                3
            ),
            "total_co2": round(
                sum(
                    r["co2"]
                    for r in self.records
                ),
                3
            ),
            "total_emergency_delay": round(
                sum(
                    r["emergency_delay"]
                    for r in self.records
                ),
                3
            )
        }