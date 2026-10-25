import math


def validate_network(network):
    """Reject invalid model inputs before sending them to the optimizer."""

    def nonnegative(value, label):
        """Reject negative, missing or nonfinite numeric inputs."""
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{label} must be a finite nonnegative number')
    if len(network.edges) != len(set(network.edges)):
        raise ValueError('Duplicate edges are not supported')
    if set(network.capacities) - set(network.edges):
        raise ValueError('Capacity records must refer to existing edges')
    for edge in network.edges:
        if edge[0] not in network.nodes or edge[1] not in network.nodes or edge[0] == edge[1]:
            raise ValueError(f'Invalid edge: {edge}')
        nonnegative(network.get_capacity(*edge), f'Capacity of {edge}')
    for demand in network.demands:
        if demand.source not in network.nodes or demand.target not in network.nodes:
            raise ValueError('Demand endpoints must be network nodes')
        if demand.source == demand.target:
            raise ValueError('Demand source and target must differ')
        nonnegative(demand.bandwidth, 'Demand bandwidth')
        if demand.bandwidth == 0:
            raise ValueError('Demand bandwidth must be positive')
        nonnegative(demand.revenue, 'Demand revenue')
    for edge, data in network.edge_expansion_data.items():
        if edge not in network.edges:
            raise ValueError(f'Expansion data for nonexistent edge: {edge}')
        for key in ['init_capacity', 'max_capacity', 'expansion_cost']:
            nonnegative(data.get(key), f'{key} of {edge}')
        if data['max_capacity'] < data['init_capacity']:
            raise ValueError(f'Maximum capacity below initial capacity: {edge}')
        if data['init_capacity'] != network.get_capacity(*edge):
            raise ValueError(f'Initial capacity mismatch: {edge}')
    for edge, data in network.candidate_edges.items():
        if edge in network.edges or edge[0] == edge[1] or (not set(edge) <= network.nodes):
            raise ValueError(f'Invalid candidate edge: {edge}')
        for key in ['max_capacity', 'expansion_cost', 'installation_cost']:
            nonnegative(data.get(key), f'{key} of candidate {edge}')
