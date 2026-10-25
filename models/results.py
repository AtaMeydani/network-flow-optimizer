"""Extract complete path allocations from solved continuous variables."""


def routed_flows(network, all_paths, fractions, accepted, edges):
    """Extract path fractions, complete link loads and representative routes."""
    routes, primary, distribution = {}, {}, {}
    edge_flows = dict.fromkeys(edges, 0.0)
    for demand_id in accepted:
        used, shares = [], {}
        for index, candidate in enumerate(all_paths[demand_id]):
            fraction = fractions[demand_id, index].value() or 0.0
            # Keep tiny positive shares; dropping them can hide undelivered bandwidth.
            if fraction <= 0:
                continue
            path = candidate['path'] if isinstance(candidate, dict) else candidate
            amount = network.demands[demand_id].bandwidth * fraction
            used.append({
                'path': path, 'flow_fraction': fraction,
                'flow_amount': amount, 'bandwidth': amount,
            })
            shares[index] = fraction
            for edge in path:
                edge_flows[edge] += amount
        routes[demand_id] = used
        primary[demand_id] = max(used, key=lambda route: route['flow_fraction'])['path']
        distribution[demand_id] = shares
    return routes, primary, edge_flows, distribution
