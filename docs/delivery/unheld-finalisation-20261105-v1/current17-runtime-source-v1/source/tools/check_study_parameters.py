"""Check parameter accounting after whole-test allocation; never run a model."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.study_parameters import validate_parameter_policy
from tools.check_study_allocation import check as check_allocation
from tools.strict_observation_json import loads


def check(policy,allocation,reservations,models):
    allocation_report=check_allocation(allocation,reservations)
    policy=loads(Path(policy).read_bytes());definitions={};digests={}
    for record in policy['models']:
        mid=record['id']
        if not isinstance(mid,str) or re.fullmatch(r'[a-z][a-z0-9-]*',mid) is None:
            raise ValueError('invalid model ID')
        content=(Path(models)/(mid+'.json')).read_bytes()
        definitions[mid]=loads(content);digests[mid]=hashlib.sha256(content).hexdigest()
    result=validate_parameter_policy(policy,definitions,
        allocation_sha256=hashlib.sha256(Path(allocation).read_bytes()).hexdigest(),definition_sha256=digests)
    result['allocation_id']=allocation_report['id']
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('policy',type=Path)
    parser.add_argument('--allocation',type=Path,required=True)
    parser.add_argument('--reservations',type=Path,required=True)
    parser.add_argument('--models',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        report=check(args.policy,args.allocation,args.reservations,args.models)
        content=json.dumps(report,indent=2,allow_nan=False)+'\n'
        if args.output:
            with args.output.open('x') as stream:stream.write(content)
        print(content,end='');return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print('Invalid study parameters: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
