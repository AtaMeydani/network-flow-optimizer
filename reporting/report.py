from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from network import NetworkGraph
from models.types import ModelType
from .summary import summary_section
from .highlights import highlights_section
from .demands import demands_section
from .links import links_section


class ReportSolution:

    def __init__(self, model_type: ModelType, network: NetworkGraph, solution):
        """Share network and solution data across the report sections."""
        self.network = network
        self.solution = solution if solution is not None else {}
        self.model_type = model_type
        self.demands = self.network.demands
        self.node_positions = self.network.node_positions

    def _get_demand_attributes(self, demand):
        """Read demand fields needed by the report sections."""
        if isinstance(demand, dict):
            source = demand.get('source', 'Unknown')
            target = demand.get('target', 'Unknown')
            bandwidth = demand.get('bandwidth', 0)
            revenue = demand.get('revenue', 0)
        else:
            source = getattr(demand, 'source', 'Unknown')
            target = getattr(demand, 'target', 'Unknown')
            bandwidth = getattr(demand, 'bandwidth', 0)
            revenue = getattr(demand, 'revenue', 0)
        return (source, target, bandwidth, revenue)

    def export_solution_report(self, filename, include_plots=True):
        """Assemble report sections and optional figures into one PDF."""
        styles = getSampleStyleSheet()
        story = []
        for section in [summary_section, highlights_section, demands_section, links_section]:
            story.extend(section(self, styles))
        if include_plots:
            from .charts import charts_section
            story.extend(charts_section(self, styles))
        SimpleDocTemplate(f'{filename}.pdf', pagesize=A4).build(story)
        print(f'PDF report saved to: {filename}.pdf')
