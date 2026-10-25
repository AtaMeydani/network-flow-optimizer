"""Network data and the small mutation API used by the solvers."""
import json
from pathlib import Path

from .demand import TrafficDemand
from .serialization import network_from_dict, network_to_dict
from .validation import validate_network


class NetworkGraph:
    def __init__(self, nodes=None, edges=None):
        """Initialize graph, demand, capacity and layout data."""
        self.nodes = set(nodes or [])
        self.edges = [tuple(edge) for edge in edges or []]
        self.capacities = {}
        self.demands = []
        self.edge_expansion_data = {}
        self.candidate_edges = {}
        self.node_positions = {}

    def add_node(self, node):
        """Add a node to the network."""
        self.nodes.add(node)

    def add_edge(self, source, target, capacity=None):
        """Add a directed edge and its optional capacity."""
        self.nodes.update([source, target])
        edge = (source, target)
        if edge not in self.edges:
            self.edges.append(edge)
        if capacity is not None:
            self.set_capacity(source, target, capacity)

    def add_demand(self, source, target, bandwidth, revenue):
        """Append a complete traffic request."""
        self.demands.append(TrafficDemand(source, target, bandwidth, revenue))

    def add_edge_expansion_data(self, source, target, init_capacity, max_capacity, expansion_cost):
        """Attach expansion bounds without changing an existing initial capacity."""
        existing = self.get_capacity(source, target)
        if existing is not None and existing != init_capacity:
            raise ValueError(f'Initial capacity mismatch: {(source, target)}')
        self.edge_expansion_data[source, target] = {
            'init_capacity': init_capacity, 'max_capacity': max_capacity,
            'expansion_cost': expansion_cost,
        }
        self.set_capacity(source, target, init_capacity)

    def set_capacity(self, source, target, capacity):
        """Set the capacity of a directed edge."""
        self.capacities[source, target] = capacity

    def get_capacity(self, source, target):
        """Return an edge capacity, or None when it is unspecified."""
        return self.capacities.get((source, target))

    def get_total_capacity(self):
        """Sum the existing link capacities."""
        return sum(self.capacities.values())

    def validate(self):
        """Check that network data defines a valid optimization input."""
        validate_network(self)

    def to_dict(self):
        """Return a JSON-compatible representation."""
        return network_to_dict(self)

    def to_json(self, indent=2):
        """Encode the network as JSON text."""
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_json_file(self, filepath, indent=2):
        """Write network data to a UTF-8 JSON file."""
        Path(filepath).write_text(self.to_json(indent), encoding='utf-8')

    @classmethod
    def from_json(cls, data):
        """Load network data from JSON text or a dictionary."""
        return network_from_dict(cls, json.loads(data) if isinstance(data, str) else data)

    @classmethod
    def from_json_file(cls, filepath):
        """Read a network configuration from a UTF-8 JSON file."""
        return cls.from_json(Path(filepath).read_text(encoding='utf-8'))
