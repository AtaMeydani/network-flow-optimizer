"""Shared graph layout and colors for report figures."""
import networkx as nx
from network import NetworkGraph
from models.types import ModelType


class PlotContext:

    def __init__(self, network: NetworkGraph, solution: dict, model_type: ModelType):
        """Prepare consistent positions and colors for every network figure."""
        self.network = network
        self.solution = solution
        self.model_type = model_type
        self.has_expansion = bool(solution.get('capacity_expansions'))
        self.edges = network.edges + list(solution.get('installed_edges', []))
        graph = nx.DiGraph()
        graph.add_nodes_from(sorted(network.nodes))
        graph.add_edges_from(self.edges)
        if hasattr(network, 'node_positions') and network.node_positions:
            self.pos = nx.spring_layout(graph, seed=42)
            self.pos.update(network.node_positions)
        elif len(network.nodes) <= 8:
            self.pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
        else:
            self.pos = nx.kamada_kawai_layout(graph)
        self.pos = {node: (x * 1.5, y * 1.5) for node, (x, y) in self.pos.items()}
        self.demand_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'olive', 'cyan', 'magenta']
        self.node_colors = []
        for node in sorted(self.network.nodes):
            if any((d.source == node for d in self.network.demands)):
                self.node_colors.append('lightgreen')
            elif any((d.target == node for d in self.network.demands)):
                self.node_colors.append('lightcoral')
            else:
                self.node_colors.append('lightblue')
