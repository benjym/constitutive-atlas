"""Generate a separately routed controlled-path catalogue from explicit models."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas.compiler import generate
from atlas.model import integration_kind, load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('models', nargs='+', type=Path)
    args = parser.parse_args()
    if any(integration_kind(load(p)) != 'path_ode' for p in args.models):
        parser.error('each model must declare the controlled-path ODE profile')
    generate(args.output, args.models)


if __name__ == '__main__':
    main()
