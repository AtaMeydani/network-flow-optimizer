import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def plot_splits(context):
    """Label the bandwidth carried on each selected path."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(sorted(context.network.nodes))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Flow Splits Visualization", fontsize=14, fontweight='bold')
    nx.draw_networkx_nodes(G, context.pos, node_color=context.node_colors,
                          node_size=800, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, context.pos, edge_color='lightgray', alpha=0.1, width=0.5, ax=ax, arrows=False)
    splits = context.solution.get('paths_used', {})
    if splits:
        demand_colors_splits = plt.cm.rainbow(np.linspace(0, 1, len(context.solution['accepted_demands'])))
        edge_labels = {}
        edge_demand_count = {}
        edge_demand_index = {}
        for idx, d in enumerate(context.solution['accepted_demands']):
            if d in splits:
                color = demand_colors_splits[idx]
                demand = context.network.demands[d]
                for path_idx, path_info in enumerate(splits[d]):
                    path = path_info['path']
                    flow_fraction = path_info['flow_fraction']
                    flow_amount = flow_fraction * demand.bandwidth
                    width = 1 + flow_fraction * 5
                    for edge in path:
                        if edge not in edge_demand_count:
                            edge_demand_count[edge] = 0
                            edge_demand_index[edge] = {}
                        demand_path_key = (d, path_idx)
                        if demand_path_key not in edge_demand_index[edge]:
                            edge_demand_index[edge][demand_path_key] = edge_demand_count[edge]
                            edge_demand_count[edge] += 1
                        index = edge_demand_index[edge][demand_path_key]
                        rad = 0.15 if edge_demand_count[edge] == 1 else (-0.15 if index == 0 else (1 if index % 2 == 1 else -1) * (0.2 + (index // 2) * 0.15))
                        ax.annotate('', xy=context.pos[edge[1]], xytext=context.pos[edge[0]],
                                    arrowprops=dict(arrowstyle='->', color=color, lw=width, alpha=0.7,
                                                    connectionstyle=f"arc3,rad={rad}"))
                        edge_key = edge
                        if edge_key not in edge_labels:
                            edge_labels[edge_key] = []
                        flow_pct = flow_fraction * 100
                        edge_labels[edge_key].append({
                            'text': f"D{d}: {flow_amount:.1f} ({flow_pct:.0f}%)",
                            'rad': rad,
                            'demand_id': d,
                            'color': color
                        })
        for edge, label_data_list in edge_labels.items():
            x1, y1 = context.pos[edge[0]]
            x2, y2 = context.pos[edge[1]]
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            dx = x2 - x1
            dy = y2 - y1
            length = np.sqrt(dx**2 + dy**2)
            perp_x, perp_y = (-dy / length, dx / length) if length > 0 else (0, 1)
            label_data_list.sort(key=lambda x: x['rad'])
            n_labels = len(label_data_list)
            for i, label_data in enumerate(label_data_list):
                base_offset = 0.15 if label_data['rad'] > 0 else -0.15 if label_data['rad'] < 0 else 0.1
                offset_variation = (i - n_labels / 2) * 0.03
                label_x = mid_x + perp_x * (base_offset + offset_variation)
                label_y = mid_y + perp_y * (base_offset + offset_variation)
                ax.text(label_x, label_y, label_data['text'],
                        fontsize=8, ha='center', va='center',
                        color=label_data['color'], weight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white',
                                  edgecolor=label_data['color'], linewidth=1.5, alpha=0.9))
        split_text = "Flow Splits:\n"
        for d in context.solution['accepted_demands']:
            if d in splits and len(splits[d]) > 1:
                demand = context.network.demands[d]
                split_text += f"D{d} ({demand.source}→{demand.target}): "
                split_text += ' / '.join([f"{p['flow_fraction'] * 100:.0f}%" for p in splits[d]]) + "\n"
        if split_text != "Flow Splits:\n":
            ax.text(0.02, 0.02, split_text, transform=ax.transAxes,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcyan"),
                    verticalalignment='bottom', fontsize=9)
    nx.draw_networkx_labels(G, context.pos, font_size=10, font_weight='bold', ax=ax)
    return fig
