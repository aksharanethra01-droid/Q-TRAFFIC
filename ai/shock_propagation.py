import networkx as nx
from dataclasses import dataclass
from typing import Dict

EVENT_IMPACT = {
    "ACCIDENT": 1.00, "ROAD_CLOSURE": 0.95, "SCHOOL_PEAK": 0.55,
    "TEXTILE_FESTIVAL": 0.70, "CROWD_SURGE": 0.75, "VEHICLE_OBSTRUCTION": 0.80,
    "AMBULANCE": 0.35, "NORMAL": 0.0, "RECOVERY": 0.15,
}

@dataclass
class ShockResult:
    event: str
    source_junction: str | None
    affected: Dict[str, str]
    severity_score: Dict[str, float]

def build_graph() -> nx.Graph:
    g = nx.Graph()
    g.add_edges_from([("J1", "J2"), ("J2", "J3"), ("J3", "J4")])
    return g

def _label(score: float) -> str:
    if score >= 0.90: return "CRITICAL"
    if score >= 0.65: return "HIGH"
    if score >= 0.40: return "MEDIUM"
    if score > 0.0: return "LOW"
    return "NORMAL"

def propagate_shock(event: str, source_junction: str | None = None, graph: nx.Graph | None = None) -> ShockResult:
    graph = graph or build_graph()
    impact = EVENT_IMPACT.get(event, 0.25)
    scores = {j: 0.0 for j in graph.nodes}
    if source_junction and source_junction in graph:
        for j in graph.nodes:
            d = nx.shortest_path_length(graph, source_junction, j)
            scores[j] = impact * (0.70 ** d)
    elif event != "NORMAL":
        scores = {j: impact for j in graph.nodes}
    return ShockResult(event, source_junction, {j: _label(s) for j, s in scores.items()}, scores)
