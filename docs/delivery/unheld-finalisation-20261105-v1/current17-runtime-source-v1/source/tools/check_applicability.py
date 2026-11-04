"""Check applicability matrix identity and coverage without loading responses."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.applicability import load_matrix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matrix', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(load_matrix(args.matrix), indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('Invalid applicability matrix: ' + str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__': raise SystemExit(main())
