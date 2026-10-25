import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap


def plot_utilization(context):
    """Draw link loads as percentages of available capacity."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(sorted(context.network.nodes))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Edge Utilization (Continuous Color Scale)", fontsize=14, fontweight='bold')
    nx.draw_networkx_nodes(G, context.pos, node_color=context.node_colors, node_size=800, alpha=0.9, ax=ax)
    colors = ['#00ff00', '#ffff00', '#ff8800', '#ff0000']
    cmap = LinearSegmentedColormap.from_list('utilization', colors, N=100)
    edge_utilization = context.solution['edge_utilization']
    for edge in context.edges:
        x1, y1 = context.pos[edge[0]]
        x2, y2 = context.pos[edge[1]]
        util_data = edge_utilization.get(edge, {})
        util_pct = util_data.get('utilization', 0)
        color = cmap(util_pct / 100.0) if util_pct > 0 else 'lightgray'
        width = 2 + (util_pct / 100.0) * 6 if util_pct > 0 else 1
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->',
                                    color=color,
                                    lw=width,
                                    alpha=0.9 if util_pct > 0 else 0.3))
        if util_pct > 0:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            dx = x2 - x1
            dy = y2 - y1
            length = np.sqrt(dx ** 2 + dy ** 2)
            perp_x, perp_y = (-dy / length * 0.05, dx / length * 0.05) if length > 0 else (0, 0)
            label_text = f"{util_pct:.0f}%"
            if context.has_expansion and edge in context.solution.get('capacity_expansions', {}):
                expansion = context.solution['capacity_expansions'][edge].get('expansion', 0)
                label_text += f"\n+{expansion:.0f}"
            ax.text(mid_x + perp_x, mid_y + perp_y, label_text, fontsize=9, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='gray', alpha=0.9))
    nx.draw_networkx_labels(G, context.pos, font_size=10, font_weight='bold', ax=ax)
    sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar.set_label('Utilization Percentage', fontsize=10)
    cbar.ax.tick_params(labelsize=9)
    for x in [25, 50, 75]:
        cbar.ax.axvline(x=x, color='black', linestyle='--', alpha=0.3, linewidth=0.5)
    if edge_utilization:
        utils = [data.get('utilization', 0) for data in edge_utilization.values()]
        avg_util, max_util = np.mean(utils) if utils else 0, np.max(utils) if utils else 0
        high_util_edges = sum(1 for u in utils if u >= 80)
        stats_text = (f"Utilization Stats:\n"
                      f"Max: {max_util:.1f}%\n"
                      f"Avg: {avg_util:.1f}%\n"
                      f"Utilized Edges: {sum(1 for u in utils if u > 0)}\n"
                      f"High Util (≥80%): {high_util_edges}")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
    return fig
