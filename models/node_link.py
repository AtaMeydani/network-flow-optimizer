import pulp
from network import NetworkGraph


def solve_node_link_model(network: NetworkGraph):
    """Maximize admission revenue with one unsplittable simple path per demand."""
    network.validate()
    nodes = sorted(network.nodes)
    edges = network.edges
    demands = network.demands
    prob = pulp.LpProblem("Node_Link_Unsplittable", pulp.LpMaximize)
    x = {d: pulp.LpVariable(f"x_{d}", cat="Binary") for d in range(len(demands))}
    y = {(d, e): pulp.LpVariable(f"y_{d}_{i}", cat="Binary")
         for d in x for i, e in enumerate(edges)}
    order = {(d, v): pulp.LpVariable(f"order_{d}_{i}", 0, len(nodes) - 1)
             for d in x for i, v in enumerate(nodes)}
    prob += pulp.lpSum(demands[d].revenue * x[d] for d in x)
    for d, demand in enumerate(demands):
        for v in nodes:
            outgoing = pulp.lpSum(y[d, e] for e in edges if e[0] == v)
            incoming = pulp.lpSum(y[d, e] for e in edges if e[1] == v)
            balance = (1 if v == demand.source else -1 if v == demand.target else 0)
            prob += outgoing - incoming == balance * x[d]
            prob += outgoing <= x[d]
            prob += incoming <= x[d]
        # Strictly increasing node order excludes disconnected routing cycles.
        for u, v in edges:
            prob += order[d, v] >= order[d, u] + 1 - len(nodes) * (1 - y[d, (u, v)])
    for e in edges:
        prob += pulp.lpSum(demands[d].bandwidth * y[d, e] for d in x) <= network.get_capacity(*e)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        return {"status": status, "message": "No optimal solution found"}

    accepted = [d for d in x if x[d].value() > 0.5]
    flows = {d: {e: demands[d].bandwidth * (y[d, e].value() or 0)
                 for e in edges} for d in x}
    paths = {}
    for d in accepted:
        successors = {u: v for u, v in edges if y[d, (u, v)].value() > 0.5}
        path = []
        node = demands[d].source
        while node != demands[d].target:
            target = successors[node]
            path.append((node, target))
            node = target
        paths[d] = path
    revenue = sum(demands[d].revenue for d in accepted)
    utilization = {}
    for e in edges:
        flow = sum(flows[d][e] for d in x)
        capacity = network.get_capacity(*e)
        utilization[e] = {"flow": flow, "capacity": capacity,
                          "utilization": 100 * flow / capacity if capacity else 0}
    return {"status": status, "objective": revenue, "total_revenue": revenue,
            "accepted_demands": accepted,
            "rejected_demands": [d for d in x if d not in accepted],
            "paths": paths, "demand_edge_flows": flows,
            "paths_used": {d: [{"path": paths[d], "flow_fraction": 1.0,
                                "flow_amount": demands[d].bandwidth,
                                "bandwidth": demands[d].bandwidth}] for d in accepted},
            "edge_utilization": utilization}
