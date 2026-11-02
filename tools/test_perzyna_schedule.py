"""CI execution of the frozen Perzyna BE-schedule qualification."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'docs/ingestion/perzyna-comsol63/execution-v2'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BASE))
spec = importlib.util.spec_from_file_location('perzyna_schedule_study', BASE/'study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps(study.collect(args.solver, args.output), indent=2))

if __name__ == '__main__':
    main()
