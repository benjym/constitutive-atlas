"""Copy the validated publication browser; no constitutive build or execution."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.research import load_publications


def bundle(destination):
    graph = load_publications()  # Fail before copying a corrupt graph.
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('publications.html', 'publications.mjs', 'style.css'):
        shutil.copyfile(ROOT / 'web' / name, destination / name)
    shutil.copyfile(ROOT / 'catalogue/publications.json', destination / 'publications.json')
    shutil.copyfile(ROOT / 'catalogue/manifest.json', destination / 'catalogue.json')
    (destination / 'schemas').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'schemas/publications.schema.json', destination / 'schemas/publications.schema.json')
    return graph


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    graph = bundle(args.output)
    print(f"Copied {len(graph['publications'])} publication records to {args.output}")
