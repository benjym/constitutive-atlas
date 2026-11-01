"""Retain strict original and unknown-profile native failures; CTest checks positives."""
import argparse
import hashlib
import json
import os
import math
import re
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def check_contract(contract, policy):
    assert contract['id'] == 'native-negative-thirteen-occ-v1'
    assert contract['models'] == policy['models'] and len(contract['models']) == 13
    expected = {(target, profile) for target in ('atlas_numerical_tests', 'atlas_recorded_tests') for profile in (None, 'unknown')}
    cases = contract['cases']
    assert len(cases) == 4 and {(c['target'], c['profile']) for c in cases} == expected
    assert all(c['returncode'] == 1 for c in cases)
    return {(c['target'], c['profile']): c for c in cases}


def check_observation(case, result):
    assert result.returncode == case['returncode']
    assert result.stdout == case['stdout']
    if 'stderr_regex' in case:
        match = re.fullmatch(case['stderr_regex'], result.stderr)
        assert match, result.stderr
        residual = float(match['residual'])
        assert math.isfinite(residual) and residual > case['residual_greater_than']
    else:
        assert result.stderr == case['stderr']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,default=ROOT/'build')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--fixture-contract',type=Path,help='Explicit current13 negative contract; omitted retains historical checker')
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing observations')
    policy=json.loads((ROOT/'catalogue/laboratory-package-policy.json').read_text())
    for model,digest in policy['models'].items():
        assert hashlib.sha256((ROOT/'models'/f'{model}.json').read_bytes()).hexdigest()==digest
    contract = json.loads(args.fixture_contract.read_text()) if args.fixture_contract else None
    cases = check_contract(contract, policy) if contract else None
    report={'status':'running','policy_id':policy['id'],'model_count':len(policy['models']),'processes':[]}
    if contract:
        report['fixture_contract_id'] = contract['id']
        report['fixture_contract_sha256'] = hashlib.sha256(args.fixture_contract.read_bytes()).hexdigest()
    save=lambda:args.output.write_text(json.dumps(report,indent=2)+'\n')
    expected={'atlas_numerical_tests':'FD test outside domain\n','atlas_recorded_tests':'nonlinear recorded replay failed: research-hp-extracted-asbs-gis-2024-v03 material update failed or trial budget exhausted; last committed knot retained\n'}
    try:
        for target,message in expected.items():
            for profile in [None,'unknown']:
                env=dict(os.environ);env.pop('ATLAS_NATIVE_FIXTURES',None)
                if profile:env['ATLAS_NATIVE_FIXTURES']=profile
                result=subprocess.run([str(args.build.resolve()/target)],env=env,capture_output=True,text=True,timeout=120)
                row={'target':target,'profile':profile,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr};report['processes'].append(row);save()
                if cases:
                    check_observation(cases[target,profile], result)
                    continue
                assert result.returncode==1,(target,profile,result.returncode)
                assert result.stderr==(message if profile is None else 'unknown native fixture profile\n')
                assert result.stdout==('Strict original default fixtures; models='+str(report['model_count'])+'\n' if profile is None else '')
        report['status']='passed';save()
    except BaseException as exc:
        report['status']='failed';report['error']=str(exc);save();raise
    print('Original native failure signatures and closed fixture selection verified for both test executables.')

if __name__=='__main__':main()
