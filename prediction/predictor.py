from pathlib import Path
from typing import Dict

import pandas as pd


def load_historical_traffic(
    path: str | Path,
) -> pd.DataFrame:
    """Load historical junction traffic data."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Historical traffic file not found: {path}"
        )

    data = pd.read_csv(path)

    if "timestamp" not in data.columns:
        raise ValueError(
            "Historical traffic data must contain a timestamp column."
        )

    return data


def calculate_historical_growth(
    historical_data: pd.DataFrame,
    junction: str,
) -> float:
    """
    Estimate the recent traffic growth rate for a junction.

    We compare the average of the latest observations with the
    average of the earlier observations.

    This is a transparent baseline that can later be replaced
    with a trained ML forecasting model.
    """

    if junction not in historical_data.columns:
        return 0.0

    values = (
        historical_data[junction]
        .dropna()
        .astype(float)
        .tolist()
    )

    if len(values) < 4:
        return 0.0

    midpoint = len(values) // 2

    earlier = values[:midpoint]
    recent = values[midpoint:]

    earlier_average = sum(earlier) / len(earlier)
    recent_average = sum(recent) / len(recent)

    if earlier_average <= 0:
        return 0.0

    growth = (
        recent_average - earlier_average
    ) / earlier_average

    # Prevent unrealistic growth from dominating
    # the short-horizon prediction.
    return max(-0.30, min(growth, 0.50))


def predict_junction_traffic(
    current_vehicles: float,
    queue: float,
    speed: float,
    capacity: float,
    demand_multiplier: float = 1.0,
    historical_growth: float = 0.0,
) -> Dict[str, int]:
    """
    Predict traffic for 1, 3 and 5 minutes.

    Inputs:
    - current traffic
    - queue pressure
    - average speed
    - road capacity
    - scenario demand multiplier
    - historical traffic growth
    """

    capacity = max(
        float(capacity),
        1.0,
    )

    # ---------------------------------------------------------
    # Current traffic pressure
    # ---------------------------------------------------------

    traffic_pressure = (
        current_vehicles / capacity
    )

    queue_pressure = (
        queue / capacity
    )

    # ---------------------------------------------------------
    # Speed pressure
    # ---------------------------------------------------------

    speed_pressure = max(
        0.0,
        min(
            1.0,
            1.0 - speed / 60.0,
        ),
    )

    # ---------------------------------------------------------
    # Base short-term growth
    # ---------------------------------------------------------

    base_growth = (
        0.02
        + 0.04 * min(
            traffic_pressure,
            1.5,
        )
        + 0.04 * min(
            queue_pressure,
            1.0,
        )
        + 0.03 * speed_pressure
    )

    # ---------------------------------------------------------
    # Historical trend contribution
    # ---------------------------------------------------------

    historical_component = (
        historical_growth * 0.35
    )

    total_growth = (
        base_growth
        + historical_component
    )

    # ---------------------------------------------------------
    # Predict 1 / 3 / 5 minutes
    # ---------------------------------------------------------

    predictions = {}

    for minutes in [1, 3, 5]:

        time_factor = minutes / 5

        predicted = (
            current_vehicles
            * demand_multiplier
            * (
                1
                + total_growth * time_factor
            )
        )

        predictions[
            f"{minutes}min"
        ] = int(
            round(
                max(
                    0,
                    predicted,
                )
            )
        )

    return predictions


def predict_network(
    traffic_state: Dict,
    demand_multiplier: float = 1.0,
    historical_data: pd.DataFrame | None = None,
) -> Dict:
    """
    Predict traffic for every junction.

    If historical_data is provided, recent historical traffic
    trends are included in the prediction.
    """

    output = {}

    for junction, state in traffic_state.items():

        historical_growth = 0.0

        if historical_data is not None:
            historical_growth = (
                calculate_historical_growth(
                    historical_data,
                    junction,
                )
            )

        output[junction] = (
            predict_junction_traffic(
                current_vehicles=state["vehicles"],
                queue=state["queue"],
                speed=state["speed"],
                capacity=state["capacity"],
                demand_multiplier=demand_multiplier,
                historical_growth=historical_growth,
            )
        )

    return output