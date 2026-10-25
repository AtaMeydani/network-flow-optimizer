import networkx as nx
import matplotlib.pyplot as plt


def plot_routes(context):
    """Draw every edge used by admitted requests."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(sorted(context.network.nodes))

    for edge in context.edges:
        capacity = context.network.get_capacity(edge[0], edge[1]) or 0
        G.add_edge(edge[0], edge[1], capacity=capacity, edge_type='base')

    fig, ax = plt.subplots(figsize=(8, 6))
    title = "Accepted Demand Paths"
    if context.has_expansion:
        title += " with Expansions"
    ax.set_title(title, fontsize=14, fontweight='bold')

    nx.draw_networkx_nodes(G, context.pos, node_color=context.node_colors,
                          node_size=800, alpha=0.9, ax=ax)

    base_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 'base']
    if context.has_expansion:
        expanded_edges = list(context.solution['capacity_expansions'].keys()) if 'capacity_expansions' in context.solution else []
        normal_edges = [e for e in base_edges if e not in expanded_edges]
        nx.draw_networkx_edges(G, context.pos, edgelist=normal_edges, edge_color='gray', alpha=0.2, width=1, ax=ax)
        nx.draw_networkx_edges(G, context.pos, edgelist=expanded_edges, edge_color='red', alpha=0.3, width=3, style='dashed', ax=ax)
    else:
        nx.draw_networkx_edges(G, context.pos, edgelist=base_edges, edge_color='gray', alpha=0.2, width=1, ax=ax)

    for idx, d in enumerate(context.solution['accepted_demands']):
        if 'paths' in context.solution and d in context.solution['paths']:
            routes = context.solution.get('paths_used', {}).get(d, [])
            path = (list(dict.fromkeys(e for route in routes for e in route['path']))
                    if routes else context.solution['paths'][d])
            color = context.demand_colors[idx % len(context.demand_colors)]
            for edge in path:
                G.add_edge(edge[0], edge[1], demand_id=d, color=color, edge_type='demand')

    demand_edge_count = {}
    for u, v, key, data in G.edges(keys=True, data=True):
        if data.get('edge_type') == 'demand':
            edge_key = (u, v)
            demand_edge_count[edge_key] = demand_edge_count.get(edge_key, 0) + 1
            rad = 0.2 * demand_edge_count[edge_key]
            ax.annotate('', xy=context.pos[v], xytext=context.pos[u],
                        arrowprops=dict(arrowstyle='->',
                                        color=data['color'],
                                        lw=2.5, alpha=0.8,
                                        connectionstyle=f"arc3,rad={rad}"))
    nx.draw_networkx_labels(G, context.pos, font_size=10, font_weight='bold', ax=ax)

    legend_elements = []
    for idx, d in enumerate(context.solution['accepted_demands']):
        demand = context.network.demands[d]
        color = context.demand_colors[idx % len(context.demand_colors)]
        split_info = ''
        if 'paths_used' in context.solution and d in context.solution['paths_used']:
            split_info = f" ({len(context.solution['paths_used'][d])} paths)"
        legend_elements.append(
            plt.Line2D([0], [0], color=color, lw=3,
                       label=f"D{d}: {demand.source}→{demand.target} (BW:{demand.bandwidth}, Rev:${demand.revenue:,}){split_info}")
        )
    if context.has_expansion:
        legend_elements.append(plt.Line2D([0], [0], color='red', lw=3, linestyle='--', label='Expanded edges'))
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), fontsize=8)

    stats_text = f"Total Revenue: ${context.solution.get('total_revenue', 0):,}\n"\
                 f"Accepted: {len(context.solution['accepted_demands'])}\n"\
                 f"Rejected: {len(context.solution.get('rejected_demands', []))}"
    if context.has_expansion:
        stats_text += f"\nExpansion Cost: ${context.solution.get('total_expansion_cost', 0):,}"
        stats_text += f"\nInstallation Cost: ${context.solution.get('total_installation_cost', 0):,}"
        stats_text += f"\nNet Profit: ${context.solution.get('net_profit', context.solution.get('objective', 0)):,}"
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen"),
           verticalalignment='bottom', fontsize=10)
    return fig
