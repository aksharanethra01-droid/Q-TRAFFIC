"""
Generic TraCI -> Q-TRAFFIC traffic observation adapter.

This module is intentionally independent of Nila's SUMO network.
When the final SUMO network is available, only the junction IDs
and lane/edge mapping need to be configured.
"""

from typing import Dict, List, Optional


def collect_junction_observation(
    traci_connection,
    junction_id: str,
    incoming_lanes: List[str],
    capacity: float = 0,
    signal: str = "UNKNOWN",
) -> Dict:
    """
    Collect traffic information for one junction from TraCI.

    Parameters
    ----------
    traci_connection:
        Active TraCI connection/module.

    junction_id:
        SUMO traffic-light/junction identifier.

    incoming_lanes:
        Incoming lane IDs belonging to the junction.

    capacity:
        Approximate junction capacity.

    signal:
        Current signal state.

    Returns
    -------
    Dict
        SUMO-style observation compatible with sumo_adapter.py.
    """

    vehicle_ids = set()
    total_speed = 0.0
    speed_samples = 0

    queue_length = 0

    for lane_id in incoming_lanes:

        # Vehicles currently present on the lane
        lane_vehicle_ids = traci_connection.lane.getLastStepVehicleIDs(
            lane_id
        )

        vehicle_ids.update(lane_vehicle_ids)

        # Mean speed on this lane
        lane_speed = traci_connection.lane.getLastStepMeanSpeed(
            lane_id
        )

        if lane_speed >= 0:
            total_speed += lane_speed
            speed_samples += 1

        # SUMO waiting time is used as a queue proxy.
        waiting_time = traci_connection.lane.getWaitingTime(
            lane_id
        )

        if waiting_time > 0:
            queue_length += len(lane_vehicle_ids)

    mean_speed = (
        total_speed / speed_samples
        if speed_samples > 0
        else 0.0
    )

    return {
        junction_id: {
            "vehicle_count": len(vehicle_ids),
            "queue_length": queue_length,
            "mean_speed": round(mean_speed, 2),
            "capacity": capacity,
            "signal": signal,
        }
    }


def collect_network_observation(
    traci_connection,
    junction_config: Dict[str, Dict],
) -> Dict:
    """
    Collect observations for multiple junctions.

    Example configuration:

        {
            "J1": {
                "incoming_lanes": ["lane1", "lane2"],
                "capacity": 60,
                "signal": "NS_GREEN"
            }
        }
    """

    observations = {}

    for junction_id, config in junction_config.items():

        observation = collect_junction_observation(
            traci_connection=traci_connection,
            junction_id=junction_id,
            incoming_lanes=config.get("incoming_lanes", []),
            capacity=config.get("capacity", 0),
            signal=config.get("signal", "UNKNOWN"),
        )

        observations.update(observation)

    return observations


def get_traffic_light_state(
    traci_connection,
    traffic_light_id: str,
) -> str:
    """
    Get the current SUMO traffic-light state.

    Returns the raw TraCI signal-state string.
    """

    return traci_connection.trafficlight.getRedYellowGreenState(
        traffic_light_id
    )


def build_junction_config(
    junctions: Dict[str, Dict],
) -> Dict[str, Dict]:
    """
    Validate and normalize junction configuration.

    This lets us keep the final SUMO mapping in one place.
    """

    normalized = {}

    for junction_id, config in junctions.items():

        normalized[junction_id] = {
            "incoming_lanes": list(
                config.get("incoming_lanes", [])
            ),
            "capacity": float(
                config.get("capacity", 0)
            ),
            "signal": config.get(
                "signal",
                "UNKNOWN"
            ),
        }

    return normalized