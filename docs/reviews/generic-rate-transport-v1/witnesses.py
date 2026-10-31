"""Read-only preliminary transport audit witnesses; no compiled execution.
Uses a synthetic model and monkeypatched loader, not an admitted model fixture.
"""
import argparse
import contextlib
import io
import runpy
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

PRELIMINARY_SHA='783002f9a5ac2440b497cda4fb20bc3a95cb6064c25a7733bf25ece0b38050c1'

def run(source, repo):
    sys.path.insert(0,str(repo))
    spec=importlib.util.spec_from_file_location('review_preliminary_rate_observations',source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    out=[]
    with tempfile.TemporaryDirectory(prefix='atlas-rate-transport-witness-') as tmp:
        root=Path(tmp);(root/'tools').mkdir();(root/'tools/research_rate_observations.py').write_bytes(source.read_bytes())
        model={'id':'transport-fixture','integration':'rate','state':[{'shape':'scalar'}]}
        protocol={'version':'research-instantaneous-rate-protocol-0.1','files':{},'model_file':'fixture.json','model_definition':model,'cases':[{'id':'control','args':['transport-fixture','1','2','3'],'expectation':{'ok':True,'values':[1.],'absolute_budgets':[0.],'parity_budgets':[0.]}}]}
        def write(path,value):path.write_text(json.dumps(value,allow_nan=False)+'\n')
        pp=root/'protocol.json';bp=root/'build.json';op=root/'observation.json';rp=root/'raw.json'
        build={'backend':'native','protocol_sha256':None,'artifacts':{'native':{'path':'/private/tmp/not-executed-driver','sha256':'a'*64}},'all_commands_succeeded':True}
        response={'ok':True,'model':model['id'],'catalogue_hash':m.digest([model]),'parameters':[1.],'state':[2.],'increment':[3.],'values':[1.],'message':''}
        descriptor={'models':[model],'sha256':m.digest([model])}
        write(root/'fixture.json',model)
        protocol['files']={'fixture.json':m.sha(root/'fixture.json')}
        def freeze():
            write(pp,protocol);build['protocol_sha256']=m.sha(pp);write(bp,build)
            raw={'argv':[build['artifacts']['native']['path'],'--stream'],'stdin':m.stream_text(protocol),'stdout':json.dumps(descriptor)+'\n'+json.dumps(response)+'\n','stderr':'','returncode':0}
            write(rp,raw)
            obs={'version':'research-instantaneous-rate-observation-0.1','backend':'native','protocol_sha256':m.sha(pp),'build_receipt_sha256':m.sha(bp),'build_receipt':build,'collector_sha256':m.sha(source),'completed':True,'transport_sha256':m.sha(rp)}
            write(op,obs);return raw,obs
        with patch.object(m,'ROOT',root),patch.object(m,'load',return_value=model),patch.object(m,'validate',create=True,return_value=None):
            raw,obs=freeze();assessed=m.audit(pp,bp,op,rp);assert assessed['outcome']=='passed'
            # Mutate raw bytes only after read() has parsed the held earlier bytes.
            original_read=m.Snapshot.read if hasattr(m,'Snapshot') else m.read
            def changing_read(*args):
                path=args[-1]
                value=original_read(*args)
                if Path(path)==rp:
                    corrupted=dict(raw);corrupted['stdout']=raw['stdout'].replace('"values": [1.0]','"values": [999.0]')
                    write(rp,corrupted)
                return value
            try:
                target=m.Snapshot if hasattr(m,'Snapshot') else m
                with patch.object(target,'read',new=changing_read):r=m.audit(pp,bp,op,rp)
                vulnerable=r['outcome']=='passed' and r['transport_sha256']!=obs['transport_sha256']
            except (ValueError,AssertionError):vulnerable=False
            out.append({'id':'raw-read-hash-race','vulnerable':vulnerable,'contract':'Reject input mutation or retain and hash the exact bytes parsed; do not bind passing values to another raw document.'})
            freeze()
            # No response-vector length/status check in parity itself: zip truncates.
            n={'backend':'native','protocol_sha256':m.sha(pp),'outcome':'passed','cases':[{'id':'control','response':{'values':[]}}]}
            w={'backend':'wasm','protocol_sha256':m.sha(pp),'outcome':'passed','cases':[{'id':'control','response':{'values':[99.]}}]}
            try:
                r=m.parity(pp,n,w);vulnerable=r['passed'] is True and r['both_independent_assessments_passed'] is True
            except (ValueError,AssertionError):vulnerable=False
            out.append({'id':'truncated-parity-vectors','vulnerable':vulnerable,'contract':'Require complete typed response vectors and audited assessment provenance before parity.'})
            protocol['cases'][0]['expectation']['values']=[-1e308]
            protocol['cases'][0]['expectation']['absolute_budgets']=[1.]
            response['values']=[1e308]
            freeze()
            try:
                r=m.audit(pp,bp,op,rp)
                try:json.dumps(r,allow_nan=False);vulnerable=False
                except ValueError:vulnerable=True
            except (ValueError,AssertionError):vulnerable=False
            out.append({'id':'finite-subtraction-overflow','vulnerable':vulnerable,'contract':'Report or reject an unrepresentable difference without constructing nonfinite JSON assessment values.'})
            # Execute only Python CLI body, with loader and ROOT patched; no collector mode.
            protocol['cases'][0]['expectation']['values']=[1.]
            protocol['cases'][0]['expectation']['absolute_budgets']=[0.]
            response['values']=[2.]
            freeze();cli_output=root/'cli-assessment.json'
            import atlas.model as model_module
            exitcode=0
            with patch.object(model_module,'ROOT',root),patch.object(model_module,'load',return_value=model),patch.object(model_module,'validate',return_value=None),patch.object(sys,'argv',[str(source),'--protocol',str(pp),'--build-receipt',str(bp),'--observation',str(op),'--transport',str(rp),'--output',str(cli_output)]),contextlib.redirect_stdout(io.StringIO()):
                try:runpy.run_path(str(source),run_name='__main__')
                except SystemExit as exc:exitcode=exc.code
            vulnerable=exitcode in (0,None) and json.loads(cli_output.read_text())['outcome']=='failed'
            out.append({'id':'numerical-failure-exit-status','vulnerable':vulnerable,'contract':'CLI writes the failed assessment and exits nonzero.'})
            # A changed protocol can contain empty pins and unchecked relative/model roles.
            protocol['model_file']=str((root/'fixture.json').resolve())
            protocol['files']={}
            freeze()
            try:m.checked_protocol(pp);vulnerable=True
            except (ValueError,AssertionError):vulnerable=False
            out.append({'id':'protocol-path-and-empty-pins','vulnerable':vulnerable,'contract':'Require model_file repo-relative and pinned; require minimum generic tool/definition provenance roles.'})
    return {'input_sha256':m.sha(source),'scope':'Synthetic pure Python; mocked model loader; no external executable launched. Witnesses characterize the pinned preliminary implementation, not a scientific source study.','witness_groups':len(out),'witnesses':out}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--repo',type=Path,required=True,help='Repository providing atlas.model; synthetic loader is mocked.')
    parser.add_argument('--require-fixed',action='store_true')
    args=parser.parse_args()
    result=run(args.source.resolve(),args.repo.resolve())
    print(json.dumps(result,indent=2,allow_nan=False))
    if args.require_fixed:
        assert not any(x['vulnerable'] for x in result['witnesses']), 'unresolved preliminary failure modes'
