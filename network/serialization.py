"""Translate JSON records into network data and back."""
from .demand import TrafficDemand


def edge_key(text):
    """Parse a directed source->target key."""
    source, target = text.split('->')
    return source.strip(), target.strip()


def network_from_dict(graph_type, data):
    """Build network data from JSON-compatible records."""
    network = graph_type(data.get('nodes', []))
    for edge in data.get('edges', []):
        network.add_edge(*edge)
    for key, capacity in data.get('capacities', {}).items():
        network.set_capacity(*edge_key(key), float(capacity))
    for key, values in data.get('capacity_expansion', {}).items():
        network.add_edge_expansion_data(
            *edge_key(key), float(values['init_capacity']),
            float(values['max_capacity']), float(values['expansion_cost']))
    for key, values in data.get('candidate_edges', {}).items():
        network.candidate_edges[edge_key(key)] = {
            name: float(values[name])
            for name in ['max_capacity', 'expansion_cost', 'installation_cost']
        }
    network.demands = [TrafficDemand.from_dict(d) for d in data.get('demands', [])]
    network.node_positions = dict(data.get('node_positions', {}))
    return network


def network_to_dict(network):
    """Serialize network data using stable node and edge keys."""
    result = {
        'nodes': sorted(network.nodes), 'edges': network.edges,
        'capacities': {'->'.join(edge): capacity for edge, capacity in network.capacities.items()},
        'demands': [d.to_dict() for d in network.demands],
    }
    for name, values in [('capacity_expansion', network.edge_expansion_data),
                         ('candidate_edges', network.candidate_edges)]:
        if values:
            result[name] = {'->'.join(edge): data for edge, data in values.items()}
    if network.node_positions:
        result['node_positions'] = network.node_positions
    return result
