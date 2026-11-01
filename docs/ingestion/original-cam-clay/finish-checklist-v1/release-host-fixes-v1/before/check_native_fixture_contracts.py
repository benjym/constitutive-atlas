"""Retain strict original and unknown-profile native failures; CTest checks positives."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,default=ROOT/'build')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing observations')
    policy=json.loads((ROOT/'catalogue/laboratory-package-policy.json').read_text())
    for model,digest in policy['models'].items():
        assert hashlib.sha256((ROOT/'models'/f'{model}.json').read_bytes()).hexdigest()==digest
    report={'status':'running','policy_id':policy['id'],'model_count':len(policy['models']),'processes':[]}
    save=lambda:args.output.write_text(json.dumps(report,indent=2)+'\n')
    expected={'atlas_numerical_tests':'FD test outside domain\n','atlas_recorded_tests':'nonlinear recorded replay failed: research-hp-extracted-asbs-gis-2024-v03 material update failed or trial budget exhausted; last committed knot retained\n'}
    try:
        for target,message in expected.items():
            for profile in [None,'unknown']:
                env=dict(os.environ);env.pop('ATLAS_NATIVE_FIXTURES',None)
                if profile:env['ATLAS_NATIVE_FIXTURES']=profile
                result=subprocess.run([str(args.build.resolve()/target)],env=env,capture_output=True,text=True,timeout=120)
                row={'target':target,'profile':profile,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr};report['processes'].append(row);save()
                assert result.returncode==1,(target,profile,result.returncode)
                assert result.stderr==(message if profile is None else 'unknown native fixture profile\n')
                assert result.stdout==('Strict original default fixtures; models='+str(report['model_count'])+'\n' if profile is None else '')
        report['status']='passed';save()
    except BaseException as exc:
        report['status']='failed';report['error']=str(exc);save();raise
    print('Original native failure signatures and closed fixture selection verified for both test executables.')

if __name__=='__main__':main()
