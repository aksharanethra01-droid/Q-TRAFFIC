import networkx as nx

def build_road_graph():
    g = nx.DiGraph()
    g.add_edge("J1", "J2", travel_time=30)
    g.add_edge("J2", "J3", travel_time=30)
    g.add_edge("J3", "J4", travel_time=30)
    return g

def find_emergency_route(source="J1", target="J4"):
    return nx.shortest_path(build_road_graph(), source, target, weight="travel_time")

def calculate_arrival_time(route=None):
    route = route or find_emergency_route()
    g = build_road_graph()
    return sum(g[u][v]["travel_time"] for u, v in zip(route, route[1:]))

def next_junction(current="J1", route=None):
    route = route or find_emergency_route()
    if current not in route:
        return None
    i = route.index(current)
    return route[i+1] if i + 1 < len(route) else None
