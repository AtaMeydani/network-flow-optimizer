"""Revenue maximization with traffic split across candidate paths."""
import pulp
from network import NetworkGraph
from .paths import candidate_paths
from .results import routed_flows


def solve_link_path_model(network: NetworkGraph, k_paths: int = 3):
    """Maximize admitted revenue by splitting traffic across candidate paths."""
    network.validate()
    edges = network.edges
    demands = network.demands
    all_paths = candidate_paths(network, k_paths)
    model = pulp.LpProblem('Link_Path_Flow', pulp.LpMaximize)
    accepted_vars = {
        d: pulp.LpVariable(f'x_{d}', cat='Binary') for d in range(len(demands))
    }
    fractions = {
        (d, p): pulp.LpVariable(f'lambda_{d}_{p}', lowBound=0, upBound=1)
        for d in accepted_vars for p in range(len(all_paths[d]))
    }
    model += pulp.lpSum(accepted_vars[d] * demands[d].revenue for d in accepted_vars)
    # An admitted request must send all of its bandwidth, including when no path exists.
    for d in accepted_vars:
        model += pulp.lpSum(fractions[d, p] for p in range(len(all_paths[d]))) == accepted_vars[d]
    for edge in edges:
        # Every candidate path contributes its share to each edge it traverses.
        flow = pulp.lpSum(
            fractions[d, p] * demands[d].bandwidth
            for d, p in fractions if edge in all_paths[d][p]
        )
        model += flow <= network.get_capacity(*edge)
    for d, p in fractions:
        model += fractions[d, p] <= accepted_vars[d]
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[model.status]
    if status != 'Optimal':
        return {'status': status, 'message': 'No optimal solution found'}

    accepted = [d for d in accepted_vars if accepted_vars[d].value() > 0.5]
    routes, primary, flows, distribution = routed_flows(
        network, all_paths, fractions, accepted, edges)
    utilization = {}
    for edge in edges:
        capacity = network.get_capacity(*edge)
        utilization[edge] = {
            'flow': flows[edge], 'capacity': capacity,
            'utilization': 100 * flows[edge] / capacity if capacity else 0,
        }
    return {
        'status': status, 'objective': pulp.value(model.objective) or 0.0,
        'total_revenue': pulp.value(model.objective) or 0.0,
        'accepted_demands': accepted,
        'rejected_demands': [d for d in accepted_vars if d not in accepted],
        'all_paths': all_paths, 'paths_used': routes, 'paths': primary,
        'flow_distribution': distribution, 'edge_utilization': utilization,
    }
