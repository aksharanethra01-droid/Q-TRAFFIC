from typing import Dict, Optional
from .config import NETWORK

def propagate_shock(traffic_state: Dict, event: Optional[Dict] = None) -> Dict[str, float]:
    """Normalized prototype shock map: origin 1.00, direct 0.65, second-level 0.30."""
    shock = {junction: 0.0 for junction in traffic_state}
    for junction, state in traffic_state.items():
        capacity = max(float(state["capacity"]), 1.0)
        shock[junction] = min(float(state["queue"]) / capacity, 1.0)
    if not event or event.get("type") == "NORMAL":
        return {k: round(min(v, 1.0), 2) for k, v in shock.items()}
    affected = event.get("junction")
    if affected not in traffic_state:
        raise ValueError(f"Unknown event junction: {affected}")
    local_shock = 1.0
    shock[affected] = local_shock
    for neighbor in NETWORK.get(affected, []):
        if neighbor in shock:
            shock[neighbor] = max(shock[neighbor], local_shock * 0.65)
            for second_neighbor in NETWORK.get(neighbor, []):
                if second_neighbor != affected and second_neighbor in shock:
                    shock[second_neighbor] = max(shock[second_neighbor], local_shock * 0.30)
    return {k: round(min(v, 1.0), 2) for k, v in shock.items()}

def build_shock_visualization(shock_map: Dict[str, float], event: Optional[Dict] = None) -> Dict:
    source = event.get("junction") if event else None
    ranked = sorted(shock_map.items(), key=lambda item: item[1], reverse=True)
    return {
        "source": source,
        "propagation": [j for j, v in ranked if v > 0],
        "intensity": shock_map,
    }
