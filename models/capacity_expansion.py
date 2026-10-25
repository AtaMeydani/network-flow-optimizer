import pulp
from network import NetworkGraph
from .paths import candidate_paths
from .results import routed_flows


def solve_capacity_expansion_model(network: NetworkGraph, k_paths: int = 3,
                                   verbose: bool = True, solver_msg: bool = False) -> dict:
    """Maximize net profit with optional link installation and capacity purchases."""
    network.validate()
    if not isinstance(k_paths, int) or isinstance(k_paths, bool) or k_paths < 1:
        raise ValueError("k_paths must be a positive integer")
    edges = network.edges + list(network.candidate_edges)
    demands = network.demands
    all_paths = {d: [{'path': path} for path in paths]
                 for d, paths in candidate_paths(network, k_paths, include_candidates=True).items()}
    prob = pulp.LpProblem("Capacity_Expansion_Network_Flow", pulp.LpMaximize)
    x = {d: pulp.LpVariable(f"x_{d}", cat="Binary") for d in range(len(demands))}
    fractions = {(d, p): pulp.LpVariable(f"lambda_{d}_{p}", 0, 1)
                 for d in x for p in range(len(all_paths[d]))}
    expansion = {}
    installed = {e: pulp.LpVariable(f"install_{i}", cat="Binary")
                 for i, e in enumerate(network.candidate_edges)}
    initial, unit_cost = {}, {}
    for i, e in enumerate(edges):
        data = network.candidate_edges.get(e) or network.edge_expansion_data.get(e)
        initial[e] = 0 if e in network.candidate_edges else network.get_capacity(*e)
        max_capacity = data['max_capacity'] if data else initial[e]
        unit_cost[e] = data['expansion_cost'] if data else 0
        expansion[e] = pulp.LpVariable(f"expansion_{i}", 0, max_capacity - initial[e])
        if e in installed:
            # New capacity is unavailable until its one-time installation fee is paid.
            prob += expansion[e] <= max_capacity * installed[e]
    revenue = pulp.lpSum(demands[d].revenue * x[d] for d in x)
    variable_cost = pulp.lpSum(unit_cost[e] * expansion[e] for e in edges)
    installation_cost = pulp.lpSum(network.candidate_edges[e]['installation_cost'] * installed[e]
                                   for e in installed)
    prob += revenue - variable_cost - installation_cost
    # Routing remains all-or-nothing even though admitted traffic can use several paths.
    for d in x:
        prob += pulp.lpSum(fractions[d, p] for p in range(len(all_paths[d]))) == x[d]
    for e in edges:
        prob += pulp.lpSum(demands[d].bandwidth * fractions[d, p]
                           for d, p in fractions if e in all_paths[d][p]['path']) <= initial[e] + expansion[e]
    prob.solve(pulp.PULP_CBC_CMD(msg=solver_msg))
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        return {"status": status, "message": "No optimal solution found"}

    accepted = [d for d in x if x[d].value() > 0.5]
    install_values = {e: installed[e].value() or 0.0 for e in installed}
    solution = {'status': status, 'objective': pulp.value(prob.objective) or 0.0,
                'net_profit': pulp.value(prob.objective) or 0.0,
                'total_revenue': sum(demands[d].revenue for d in accepted),
                'total_expansion_cost': sum(unit_cost[e] * (expansion[e].value() or 0) for e in edges),
                'total_installation_cost': sum(network.candidate_edges[e]['installation_cost'] * install_values[e]
                                                for e in installed),
                'accepted_demands': accepted,
                'rejected_demands': [d for d in x if d not in accepted],
                'paths': {}, 'paths_used': {}, 'capacity_expansions': {},
                'installed_edges': [e for e in installed if install_values[e] > 0.5],
                'edge_utilization': {}, 'all_paths': all_paths}
    solution['total_cost'] = solution['total_expansion_cost'] + solution['total_installation_cost']
    routes, primary, edge_flows, _ = routed_flows(network, all_paths, fractions, accepted, edges)
    solution['paths_used'] = routes
    solution['paths'] = primary
    for e in edges:
        added = expansion[e].value() or 0.0
        fixed_cost = (network.candidate_edges[e]['installation_cost'] * install_values[e]
                      if e in installed else 0)
        if added > 0 or fixed_cost > 0:
            solution['capacity_expansions'][e] = {
                'expansion': added, 'init_capacity': initial[e],
                'new_capacity': initial[e] + added, 'expansion_cost': unit_cost[e] * added,
                'installation_cost': fixed_cost, 'cost': unit_cost[e] * added + fixed_cost}
        capacity = initial[e] + added
        solution['edge_utilization'][e] = {
            'flow': edge_flows[e], 'capacity': capacity, 'init_capacity': initial[e],
            'expansion': added, 'utilization': 100 * edge_flows[e] / capacity if capacity else 0}
    if verbose:
        print(f"Capacity expansion: {status}, revenue={solution['total_revenue']:.2f}, "
              f"cost={solution['total_cost']:.2f}, profit={solution['net_profit']:.2f}")
    return solution
