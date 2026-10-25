"""Build the figures included in a solution report."""
from models.types import ModelType
from .context import PlotContext
from .routes import plot_routes
from .utilization import plot_utilization
from .splits import plot_splits
from .expansion import plot_expansion


def build_figures(network, solution, model):
    """Build the route, utilization and design figures required by a model."""
    context = PlotContext(network, solution, model)
    figures = [('Accepted Demand Paths', plot_routes(context)),
               ('Edge Utilization', plot_utilization(context))]
    if model in [ModelType.LINK_PATH, ModelType.CAPACITY_EXPANSION]:
        figures.append(('Flow Splits', plot_splits(context)))
    if model == ModelType.CAPACITY_EXPANSION:
        figures.append(('Capacity Expansion Details', plot_expansion(context)))
    return figures
