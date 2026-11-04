"""Check whole-test allocation metadata without reading experiment responses."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.study_allocation import validate_allocation
from tools.strict_observation_json import loads


def check(allocation, policy):
    plan=loads(Path(allocation).read_bytes())
    content=Path(policy).read_bytes()
    return validate_allocation(plan,loads(content),policy_sha256=hashlib.sha256(content).hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('allocation',type=Path)
    parser.add_argument('--policy',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        report=check(args.allocation,args.policy)
        content=json.dumps(report,indent=2,allow_nan=False)+'\n'
        if args.output:
            with args.output.open('x') as stream:stream.write(content)
        print(content,end='')
        return 0
    except (OSError,ValueError,TypeError) as exc:
        print('Invalid study allocation: '+str(exc),file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
