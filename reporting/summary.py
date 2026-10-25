from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak


def summary_section(report, styles):
    """Build the numerical objective, cost and admission summary."""
    story = []
    title = report.model_type.value.replace('_', ' ').title()
    story.append(Paragraph(f"{title} Network Optimization Report", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Model Type: <b>{report.model_type.value}</b>", styles['Normal']))
    story.append(Spacer(1, 0.14 * inch))
    n_nodes = len(report.network.nodes)
    n_edges = len(report.network.edges)
    total_init_capacity = report.network.get_total_capacity()
    total_expanded = sum(
        info.get('expansion', 0)
        for info in report.solution.get('capacity_expansions', {}).values()
        if isinstance(info, dict))
    total_demands = len(report.demands)
    accepted = set(report.solution.get('accepted_demands', []))
    total_revenue = sum(report._get_demand_attributes(report.demands[d])[3] for d in accepted if d < total_demands)
    expansion_cost = report.solution.get('total_expansion_cost', 0)
    installation_cost = report.solution.get('total_installation_cost', 0)
    total_cost = expansion_cost + installation_cost
    net_profit = report.solution.get('objective', total_revenue - total_cost)
    acceptance_rate = len(accepted) / total_demands * 100 if total_demands else 0
    objective = report.solution.get('objective', total_revenue)
    summary_data = [
        ['Metric', 'Value'],
        ['Status', report.solution.get('status', 'Unknown')],
        ['Objective Value', f"${objective:,.2f}"],
        ['Total Revenue', f"${total_revenue:,.2f}"],
        ['Total Expansion Cost', f"${expansion_cost:,.2f}"],
        ['Total Installation Cost', f"${installation_cost:,.2f}"],
        ['Total Cost', f"${total_cost:,.2f}"],
        ['Net Profit', f"${net_profit:,.2f}"],
        ['Accepted Demands', f"{len(accepted)} / {total_demands}"],
        ['Rejected Demands', f"{total_demands - len(accepted)} / {total_demands}"],
        ['Acceptance Rate', f"{acceptance_rate:.1f}%"],
        ['Nodes', n_nodes], ['Edges', n_edges],
        ['Total Initial Capacity', f"{total_init_capacity:.2f}"],
        ['Total Expansion', f"{total_expanded:.2f}"],
        ['Capacity Increase (%)', f"{(total_expanded / total_init_capacity * 100 if total_init_capacity else 0):.1f}%"]
    ]
    summary_table = Table(summary_data, colWidths=[2.3*inch, 2.0*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.black)
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    return story
