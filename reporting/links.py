from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak


def links_section(report, styles):
    """Report purchased capacities, costs and the most utilized links."""
    story = []
    if 'capacity_expansions' in report.solution:
        story.append(Paragraph("Capacity Expansions", styles['Heading1']))
        capexs = report.solution['capacity_expansions']
        if capexs:
            ex_table = [["Edge", "Expansion (units)", "New Capacity", "Total Cost ($)"]]
            for edge, info in capexs.items():
                if isinstance(info, dict):
                    edge_str = f"{edge[0]}  ->  {edge[1]}"
                    ex_table.append([
                        edge_str,
                        f"{info.get('expansion', 0):.2f}",
                        f"{info.get('new_capacity', 0):.2f}",
                        f"${info.get('cost', 0):,.2f}"
                    ])
            t = Table(ex_table, colWidths=[2.2*inch, 1.6*inch, 1.3*inch, 1.4*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.blue)
            ]))
            story.append(Spacer(1, 0.04*inch))
            story.append(t)
        else:
            story.append(Paragraph("No capacity expansions were needed.", styles['Normal']))
        story.append(PageBreak())

    if 'edge_utilization' in report.solution:
        story.append(Paragraph("Edge Utilizations (Top 12 Edges)", styles['Heading1']))
        edgeutil = list(report.solution['edge_utilization'].items())
        edgeutil.sort(key=lambda x: x[1].get('utilization', 0), reverse=True)
        table_data = [["Edge", "Flow", "Total Capacity", "Utilization (%)"]]
        for (u, v), info in edgeutil[:12]:
            table_data.append([
                f"{u}  ->  {v}",
                f"{info.get('flow', 0):.2f}",
                f"{info.get('capacity', 0):.2f}",
                f"{info.get('utilization', 0):.1f} %"
            ])
        t = Table(table_data, colWidths=[2.2*inch, 1.1*inch, 1.3*inch, 1.3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        story.append(t)
        story.append(PageBreak())

    return story
