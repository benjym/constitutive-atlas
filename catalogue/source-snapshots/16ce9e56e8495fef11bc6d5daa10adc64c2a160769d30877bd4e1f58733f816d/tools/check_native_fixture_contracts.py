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


OCC='original-cam-clay-sw-electronic-log-recovery-v1'
OCC_HASH='637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34'
GIS_FAILURE='nonlinear recorded replay failed: research-hp-extracted-asbs-gis-2024-v03 material update failed or trial budget exhausted; last committed knot retained\n'

def check_recorded_failure(message, definitions, *, root=ROOT):
    if OCC not in definitions:
        assert message==GIS_FAILURE
        return 'historical-twelve GIS first failure'
    assert len(definitions)==13 and definitions[OCC]==OCC_HASH, 'unqualified strict catalogue'
    match=re.fullmatch(r'failed knot 1 residual ([^ ]+) trials 1 de0 ([^ ]+) de1 0\ndrained replay failed: '+re.escape(OCC)+r' singular mixed-control system; last committed knot retained\n',message)
    assert match, 'strict OCC failure signature changed'
    residual,axial=map(float,match.groups())
    assert axial==1e-4 and math.isfinite(residual)
    # Independent cone endpoint: BE volume, source normal-compression packing;
    # initial transverse stress is100kPa and fixed control scale100kPa.
    model=json.loads((root/'models'/f'{OCC}.json').read_text())
    params={k:v['default'] for k,v in model['parameters'].items()}
    volume=model['state'][1]['initial']/(1+axial)
    pressure=params['pref']*math.exp((params['Gamma']+params['lambda_c']-params['kappa']-volume)/params['lambda_c'])
    expected=abs(pressure-100000)/100000
    assert abs(residual-expected)<=2e-10*max(1,abs(expected)), 'strict OCC cone residual changed'
    return 'current-thirteen OCC first failure; original rollback asserted by positive v4 suite'

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
    expected={'atlas_numerical_tests':'FD test outside domain\n','atlas_recorded_tests':GIS_FAILURE}
    try:
        for target,message in expected.items():
            for profile in [None,'unknown']:
                env=dict(os.environ);env.pop('ATLAS_NATIVE_FIXTURES',None)
                if profile:env['ATLAS_NATIVE_FIXTURES']=profile
                result=subprocess.run([str(args.build.resolve()/target)],env=env,capture_output=True,text=True,timeout=120)
                row={'target':target,'profile':profile,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr};report['processes'].append(row);save()
                assert result.returncode==1,(target,profile,result.returncode)
                if target=='atlas_recorded_tests' and profile is None:
                    row['strict_context']=check_recorded_failure(result.stderr,policy['models']);save()
                else:
                    assert result.stderr==(message if profile is None else 'unknown native fixture profile\n')
                assert result.stdout==('Strict original default fixtures; models='+str(report['model_count'])+'\n' if profile is None else '')
        report['status']='passed';save()
    except BaseException as exc:
        report['status']='failed';report['error']=str(exc);save();raise
    print('Original native failure signatures and closed fixture selection verified for both test executables.')

if __name__=='__main__':main()
