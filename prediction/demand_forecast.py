from typing import Dict


def demand_multiplier(
    scenario_multiplier: float = 1.0,
    is_peak_hour: bool = False,
    event_type: str = "NORMAL",
    event_severity: str = "LOW",
) -> float:
    """
    Calculate the final traffic-demand multiplier.

    scenario_multiplier:
        Multiplier provided by the selected location/scenario.

    is_peak_hour:
        Adds additional demand during peak periods.

    event_type:
        Represents a known event such as a festival, school peak,
        road closure, or accident.

    event_severity:
        Represents the severity of the event.
    """

    multiplier = float(scenario_multiplier)

    # Peak-hour effect
    if is_peak_hour:
        multiplier += 0.20

    event_type = event_type.upper()

    # Known demand-increasing events
    if event_type in {
        "FESTIVAL",
        "PUBLIC_EVENT",
        "COLLEGE_EVENT",
    }:
        multiplier += 0.20

    elif event_type == "ROAD_CLOSURE":
        multiplier += 0.10

    elif event_type == "ACCIDENT":
        multiplier += 0.05

    # Severe events can create additional traffic pressure
    if event_severity.upper() == "HIGH":
        multiplier += 0.10

    return round(multiplier, 2)


def forecast_demand(
    traffic_state: Dict,
    multiplier: float = 1.0,
    is_peak_hour: bool = False,
    event_type: str = "NORMAL",
    event_severity: str = "LOW",
    scenario_multiplier: float = 1.0,
) -> Dict[str, int]:
    """
    Forecast vehicle demand for each junction.

    The function supports both:
    - direct multiplier usage
    - scenario/peak/event-based demand calculation

    This keeps the module compatible with the existing tests while
    allowing the new location/scenario architecture to use it.
    """

    # If additional context is supplied, calculate the multiplier.
    context_multiplier = demand_multiplier(
        scenario_multiplier=scenario_multiplier,
        is_peak_hour=is_peak_hour,
        event_type=event_type,
        event_severity=event_severity,
    )

    # If caller explicitly supplied a non-default multiplier,
    # use it as the base multiplier.
    if multiplier != 1.0:
        final_multiplier = multiplier

    else:
        final_multiplier = context_multiplier

    return {
        junction: int(
            round(
                state["vehicles"] * final_multiplier
            )
        )
        for junction, state in traffic_state.items()
    }