"""Audit both opaque rate evidence bundles, then assess cross-backend parity.

No constitutive equations. Arbitrary assessment JSON is never an input.
"""
import argparse
import json
from pathlib import Path
from tools import research_rate_observations_v3 as rates


def assess(protocol_path,native_paths,wasm_paths):
    """Each bundle is (build receipt, observation receipt, raw journal)."""
    rates.require(len(native_paths)==len(wasm_paths)==3,'three explicit evidence paths per backend')
    snapshot=rates.Snapshot()
    protocol,_,_=rates.checked_protocol(protocol_path,snapshot)
    for name in ('tools/research_rate_observations_v3.py','tools/collect_research_rates_wasm_v3.mjs',
                 'tools/research_rate_parity_v3.py'):
        snapshot.sha(rates.ROOT/name)
    bundles=[]
    for expected,paths in (('native',native_paths),('wasm',wasm_paths)):
        build_path,observation_path,raw_path=map(Path,paths)
        for path in (build_path,observation_path,raw_path):snapshot.blob(path)
        rates.build_receipt(build_path,protocol_path,expected,snapshot=snapshot)
        assessment=rates.audit(protocol_path,build_path,observation_path,raw_path)
        rates.require(assessment['backend']==expected,'explicit backend bundle role')
        for key,path in (('protocol_sha256',protocol_path),('build_receipt_sha256',build_path),
                         ('observation_sha256',observation_path),('transport_sha256',raw_path)):
            rates.require(assessment[key]==snapshot.sha(path),'held evidence identity: '+key)
        bundles.append(assessment)
    comparison=rates.parity(protocol_path,*bundles)
    snapshot.check()
    passed=comparison['passed'] and comparison['both_backend_assessments_passed']
    return {'version':'research-instantaneous-rate-evidence-comparison-0.3',
            'outcome':'passed' if passed else 'failed','protocol_sha256':snapshot.sha(protocol_path),
            'wrapper_sha256':snapshot.sha(__file__),'native':bundles[0],'wasm':bundles[1],
            'parity':comparison,
            'claims':{'integration':False,'material_AD':False,'scientific_admission':False,'experimental_validation':False}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,required=True)
    for backend in ('native','wasm'):
        for kind in ('build','observation','transport'):parser.add_argument('--'+backend+'-'+kind,type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();rates.require(not args.output.exists(),'fresh comparison output required')
    result=assess(args.protocol,tuple(getattr(args,'native_'+k) for k in ('build','observation','transport')),
                  tuple(getattr(args,'wasm_'+k) for k in ('build','observation','transport')))
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(result['outcome']);return 0 if result['outcome']=='passed' else 1

if __name__=='__main__':raise SystemExit(main())
