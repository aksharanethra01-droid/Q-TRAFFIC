import networkx as nx

def edge_cost(data, alpha=2.0, beta=1.5, gamma=1.0):
    distance=float(data.get("distance",1))
    congestion=float(data.get("congestion",0))
    queue=float(data.get("queue",0))
    speed=max(float(data.get("speed",1)),1)
    return distance + alpha*congestion + beta*queue + gamma*(distance/speed)

def candidate_routes(graph,start,destination,k=3):
    g=graph.copy()
    if g.is_multigraph():
        for u,v,key,data in list(g.edges(keys=True,data=True)):
            if data.get("closed",False): g.remove_edge(u,v,key=key)
    else:
        g.remove_edges_from([(u,v) for u,v,d in g.edges(data=True) if d.get("closed",False)])
    try:
        paths=nx.shortest_simple_paths(g,start,destination,weight=lambda u,v,d: edge_cost(d))
    except (nx.NetworkXNoPath,nx.NodeNotFound):
        return []
    result=[]
    for path in paths:
        cost=sum(edge_cost(g.get_edge_data(u,v)) for u,v in zip(path[:-1],path[1:]))
        result.append({"route":path,"cost":round(cost,3)})
        if len(result)>=k: break
    return result

def select_best_route(routes):
    return min(routes,key=lambda x:x["cost"]) if routes else None
