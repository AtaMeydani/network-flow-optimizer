from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak


def highlights_section(report, styles):
    """Summarize link utilization, expansion and rejected revenue."""
    story = []
    accepted = set(report.solution.get('accepted_demands', []))
    story.append(Paragraph("Insights & Highlights", styles['Title']))
    edge_utils = report.solution.get('edge_utilization', {})
    max_util_edge = max(edge_utils.items(), key=lambda x: x[1].get('utilization', 0), default=(None, {'utilization':0}))
    high_util_edges = [(e, info) for e, info in edge_utils.items() if info.get('utilization', 0) >= 90]
    expanded_edges = report.solution.get('capacity_expansions', {})
    highlight_data = [
        ["Key Insight", "Detail"],
        ["Most Congested Edge",
         (f"{max_util_edge[0][0]} -> {max_util_edge[0][1]} ({max_util_edge[1]['utilization']:.1f}%)" if max_util_edge[0] else "None")],
        ["Number of Highly Utilized Edges (≥90%)", len(high_util_edges)],
        ["Most Capacity Expansion",
         f"{max(expanded_edges.items(), key=lambda x: x[1].get('expansion', 0))[0] if expanded_edges else 'None'}"],
        ["Total Lost Revenue", f"${sum(report._get_demand_attributes(report.demands[d])[3] for d in range(len(report.demands)) if d not in accepted):,.2f}"],
        ["Number of Expanded Edges", len(expanded_edges)]
    ]
    highlights_table = Table(highlight_data, colWidths=[2.6*inch, 2.9*inch])
    highlights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(highlights_table)
    if high_util_edges:
        story.append(Spacer(1, 0.13*inch))
        story.append(Paragraph(
            '<b>WARNING:</b> Congestion risk in the following edges (utilization ≥90%):',
            styles['Normal']))
        for edge, info in high_util_edges:
            story.append(Paragraph(
                f"- Edge {edge[0]} -> {edge[1]}: {info.get('utilization', 0):.1f}% used", styles['Normal']))
    story.append(PageBreak())

    return story
