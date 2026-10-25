from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak


def demands_section(report, styles):
    """List admitted routes and rejected requests in the report."""
    story = []
    accepted = set(report.solution.get('accepted_demands', []))
    story.append(Paragraph("Accepted Demands & Flow Paths", styles['Heading1']))
    if accepted:
        for idx, d_idx in enumerate(sorted(accepted)):
            if d_idx < len(report.demands):
                if idx:
                    story.append(Spacer(1, 0.14*inch))
                demand = report.demands[d_idx]
                source, target, bandwidth, revenue = report._get_demand_attributes(demand)
                dn_head = f"<b>Demand {d_idx}: {source} -&gt; {target}</b>"
                demand_info = (
                    f"<b>Bandwidth:</b> {bandwidth} units &nbsp; &nbsp; "
                    f"<b>Revenue:</b> ${revenue}<br/>"
                    f"<b>Revenue/BW:</b> ${revenue / bandwidth:.2f}/unit" if bandwidth else ""
                )
                story.append(Paragraph(dn_head, styles['Heading3']))
                story.append(Paragraph(demand_info, styles['Normal']))
                if d_idx in report.solution.get('paths_used', {}):
                    allocs = report.solution['paths_used'][d_idx]
                    alloc_table = [['Path', 'Fraction', 'Bandwidth']]
                    for alloc in allocs:
                        path_str = " -> ".join([alloc["path"][0][0]] + [e[1] for e in alloc["path"]])
                        alloc_table.append([
                            path_str,
                            f"{alloc['flow_fraction']:.2%}",
                            f"{alloc['flow_amount']:.2f}"
                        ])
                    t = Table(alloc_table, colWidths=[3.5*inch, 1.1*inch, 1.1*inch])
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
                    ]))
                    story.append(t)
    else:
        story.append(Paragraph("No demands were accepted.", styles['Normal']))
    story.append(PageBreak())

    rejected = report.solution.get('rejected_demands', None)
    if not rejected:
        rejected = [i for i in range(len(report.demands)) if i not in accepted]
    lost_revenue = 0
    story.append(Paragraph("Rejected Demands", styles['Heading1']))
    if rejected:
        rej_table = [["Idx", "Source", "Target", "Bandwidth", "Revenue ($)"]]
        for d_idx in rejected:
            if d_idx < len(report.demands):
                demand = report.demands[d_idx]
                source, target, bandwidth, revenue = report._get_demand_attributes(demand)
                rej_table.append([d_idx, source, target, bandwidth, revenue])
                lost_revenue += revenue
        t = Table(rej_table, colWidths=[0.7*inch, 1.5*inch, 1.5*inch, 1.1*inch, 1.3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Paragraph(f"<b>Total Lost Revenue:</b> ${lost_revenue:,.2f}", styles['Normal']))
    else:
        story.append(Paragraph("No demands were rejected.", styles['Normal']))
    story.append(PageBreak())

    return story
