"""Read network data, solve the selected model and save its result."""
import json
from pathlib import Path
from network import NetworkGraph
from models.node_link import solve_node_link_model
from models.link_path import solve_link_path_model
from models.capacity_expansion import solve_capacity_expansion_model
from models.types import ModelType

PROJECT_DIR = Path(__file__).resolve().parent


def example_jobs():
    """Choose the applicable solvers for each example configuration."""
    for path in sorted((PROJECT_DIR / 'data').glob('net_*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('capacity_expansion') or data.get('candidate_edges'):
            yield path, solve_capacity_expansion_model, ModelType.CAPACITY_EXPANSION
        else:
            yield path, solve_node_link_model, ModelType.NODE_LINK
            yield path, solve_link_path_model, ModelType.LINK_PATH


def json_ready(value):
    """Encode edge tuple keys as source->target in portable raw JSON."""
    if isinstance(value, dict):
        return {('->'.join(k) if isinstance(k, tuple) else str(k)): json_ready(v)
                for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


def solve(solver, network_config_path, model, output_dir=None, pdf=True, plots=True):
    """Read a configuration, solve it and save JSON and optional PDF output."""
    config_path = Path(network_config_path)
    if not config_path.is_absolute():
        config_path = PROJECT_DIR / config_path
    output_dir = Path(output_dir) if output_dir is not None else PROJECT_DIR / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    network = NetworkGraph.from_json_file(config_path)
    solution = solver(network=network)
    if solution['status'] != 'Optimal':
        raise RuntimeError(f"{config_path.name}: {solution['status']}")
    filename = output_dir / f'{config_path.stem}_{model.value}'
    filename.with_suffix('.json').write_text(
        json.dumps(json_ready(solution), indent=2, allow_nan=False), encoding='utf-8')
    if pdf:
        from reporting.report import ReportSolution
        ReportSolution(model, network, solution).export_solution_report(str(filename), include_plots=plots)
    print(f"{config_path.stem} / {model.value}: objective={solution['objective']:.2f}, "
          f"accepted={len(solution['accepted_demands'])}/{len(network.demands)}")
    return solution

