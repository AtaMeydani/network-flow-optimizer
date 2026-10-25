import networkx as nx
import matplotlib.pyplot as plt


def plot_expansion(context):
    """Show purchased capacities and separate variable and fixed costs."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(sorted(context.network.nodes))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Capacity Expansion Details", fontsize=14, fontweight='bold')
    nx.draw_networkx_nodes(G, context.pos, node_color=context.node_colors,
                          node_size=800, alpha=0.9, ax=ax)
    expanded_edges = context.solution.get('capacity_expansions', {})
    edge_labels = {}
    for edge, exp_info in expanded_edges.items():
        base_capacity = context.network.get_capacity(edge[0], edge[1]) or 0
        exp_amount = exp_info.get('expansion', 0)
        cost = exp_info.get('cost', exp_info.get('expansion_cost', 0))
        nx.draw_networkx_edges(G, context.pos, edgelist=[edge],
                               edge_color='red', width=3, style='dashed', alpha=0.8, ax=ax)
        x1, y1 = context.pos[edge[0]]
        x2, y2 = context.pos[edge[1]]
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y, f"+{exp_amount}\n(${cost:,})", fontsize=8, ha='center',
                va='center', bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='red', alpha=0.8))
        edge_labels[edge] = f"Base: {base_capacity}, Added: {exp_amount}, Cost: ${cost:,}"
    nx.draw_networkx_edges(G, context.pos, edgelist=[e for e in context.edges if e not in expanded_edges],
                           edge_color='gray', width=1, alpha=0.2, ax=ax)
    nx.draw_networkx_labels(G, context.pos, font_size=10, font_weight='bold', ax=ax)

    exp_text = 'Capacity Expansions:\n'
    for edge, lbl in edge_labels.items():
        exp_text += f"{edge}: {lbl}\n"
    exp_text += f"Capacity Cost: ${context.solution.get('total_expansion_cost', 0):,}\n"
    exp_text += f"Installation Cost: ${context.solution.get('total_installation_cost', 0):,}\n"
    exp_text += f"Total Cost: ${context.solution.get('total_cost', 0):,}"
    ax.text(0.02, 0.02, exp_text, transform=ax.transAxes, verticalalignment='bottom',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="mistyrose"),
            fontsize=9)
    return fig
