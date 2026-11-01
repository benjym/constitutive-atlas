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
DUNCAN='duncan-chang-1970-endpoint-average'
DUNCAN_HASH='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
RAMBERG='ramberg-osgood-ansys242'
RAMBERG_HASH='c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2'
# Exact prior13 mapping from preserved package policy84fe14c4..., not mutable live policy.
PRIOR_THIRTEEN={
    "barodesy-clay-2017": "0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477",
    "barodesy-sand": "3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239",
    "drucker-prager": "b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877",
    "hypoplastic-clay-2005": "247de2f1792cf220748671b4563c7dd290c5b91fcc95eda5977ac03e01fa6ff5",
    "hypoplastic-clay-2013": "6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4",
    "hypoplastic-sand-igs97": "83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86",
    "hypoplastic-sand-vw96": "1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61",
    "linear-elastic": "33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041",
    "modified-cam-clay": "e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14",
    "mohr-coulomb": "6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5",
    "research-hp-extracted-asbs-gis-2024-v03": "439b785e1da3075209c6d5ca43a991a441463a915f31f2e9c77b5c6835e20dbc",
    "tresca-associated-perfect-bk2022v1-be": "19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18",
    "original-cam-clay-sw-electronic-log-recovery-v1": "637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34"
}
GIS_FAILURE='nonlinear recorded replay failed: research-hp-extracted-asbs-gis-2024-v03 material update failed or trial budget exhausted; last committed knot retained\n'

def check_recorded_failure(message, definitions, *, root=ROOT):
    if OCC not in definitions:
        assert message==GIS_FAILURE
        return 'historical-twelve GIS first failure'
    if RAMBERG in definitions:
        assert definitions=={**PRIOR_THIRTEEN,DUNCAN:DUNCAN_HASH,RAMBERG:RAMBERG_HASH}, 'unqualified strict fifteen-model catalogue'
    elif DUNCAN in definitions:
        assert definitions=={**PRIOR_THIRTEEN,DUNCAN:DUNCAN_HASH}, 'unqualified strict fourteen-model catalogue'
    else:
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
    return ('current-fifteen Ramberg/Duncan/OCC' if RAMBERG in definitions else 'current-fourteen Duncan/OCC' if DUNCAN in definitions else 'current-thirteen OCC')+' first failure; original rollback asserted by explicit positive suite'

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
