"""Build a paper-side source/phase map without loading cyclic response rows."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.cyclic_inventory import build_inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'paper/study/ottawa_cyclic_inventory.json')
    args = parser.parse_args()
    report_path = ROOT/'paper/results/public-feasibility/report.json'
    registry_path = ROOT/'data/public_sources.json'
    report = read_json(report_path)
    for name, expected in report['inputs'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('shared manifests changed; rerun audit_public_feasibility.py first')
    inputs = {**report['inputs'], str(report_path.relative_to(ROOT)): digest(report_path),
              'paper/analysis/cyclic_inventory.py': digest(ROOT/'paper/analysis/cyclic_inventory.py'),
              'paper/scripts/inventory_ottawa_cyclic.py': digest(__file__)}
    value = build_inventory(report, read_json(registry_path))
    if any(digest(ROOT/name) != expected for name, expected in inputs.items()):
        raise ValueError('cyclic inventory inputs changed during generation')
    value['inputs_sha256'] = inputs
    write_json(args.output, value)
    print(value['counts'])


if __name__ == '__main__':
    main()
