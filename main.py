"""Command-line entry point for generating all example solutions."""
import argparse
from pathlib import Path
from workflow import PROJECT_DIR, example_jobs, solve


def main():
    """Parse command options and generate all example solutions."""
    parser = argparse.ArgumentParser(description='Read network data, solve models and save results.')
    parser.add_argument('--output-dir', type=Path, default=PROJECT_DIR / 'results')
    parser.add_argument('--no-pdf', action='store_true', help='Save raw JSON only')
    parser.add_argument('--no-plots', action='store_true', help='Omit plots from PDF reports')
    args = parser.parse_args()
    for path, solver, model in example_jobs():
        solve(solver, path, model, args.output_dir, pdf=not args.no_pdf, plots=not args.no_plots)


if __name__ == '__main__':
    main()
