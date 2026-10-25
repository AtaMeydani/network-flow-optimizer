"""Candidate paths shared by the two splittable formulations."""
from itertools import islice
import networkx as nx


def candidate_paths(network, k_paths=3, include_candidates=False):
    """Return up to k shortest simple paths for each request."""
    if not isinstance(k_paths, int) or isinstance(k_paths, bool) or k_paths < 1:
        raise ValueError('k_paths must be a positive integer')
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(network.nodes))
    graph.add_edges_from(network.edges)
    if include_candidates:
        graph.add_edges_from(network.candidate_edges)
    paths = {}
    for index, demand in enumerate(network.demands):
        try:
            selected = islice(nx.shortest_simple_paths(graph, demand.source, demand.target), k_paths)
            paths[index] = [list(zip(path[:-1], path[1:])) for path in selected]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            paths[index] = []
    return paths
