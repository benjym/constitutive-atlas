"""Serial standard-API runner, retaining raw process output per frozen request."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import time
from assess import HERE, ROOT, FREEZE, context, load, sha, require


def verify_execution_freeze():
    freeze=load(HERE/'execution-freeze.json')
    for name,expected in freeze['files'].items():
        require(sha(ROOT/name)==expected,'execution pin: '+name)
    return freeze


def invoke(backend,artifact,request,work):
    args=request['args'];work.mkdir()
    request_file=work/'request.json';request_file.write_text(json.dumps(request))
    if backend=='native':
        command=[str(artifact),'--mode','recorded' if request['function']=='atlas_replay_recorded_scope' else 'integrate','--model',args[0],'--parameters',args[1],'--initial',args[2]]
        if request['function']=='atlas_replay_recorded_scope':
            (work/'controls.csv').write_text(args[4]);(work/'knots.csv').write_text(args[5])
            command+=['--initial-strain',args[3],'--recorded-controls-file',str(work/'controls.csv'),'--recorded-knots-file',str(work/'knots.csv'),'--integration-settings',args[6],'--recorded-settings',args[7],'--recorded-stress-scope',args[8]]
        else:
            command+=['--strain',args[3]]
            if len(args)==5:command+=['--integration-settings',args[4]]
    else:
        command=['/opt/homebrew/bin/node',str(HERE/'wasm-call.mjs'),str(artifact),str(request_file)]
    start=time.monotonic(); receipt={'request':request,'argv':command,'backend':backend,'timeout_seconds':300}
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=300)
        receipt.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        try:receipt['response']=json.loads(result.stdout)
        except (ValueError,TypeError) as exc:receipt['exception']='JSON: '+str(exc)
    except subprocess.TimeoutExpired as exc:
        decode=lambda x:x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
        receipt.update(returncode=None,stdout=decode(exc.stdout),stderr=decode(exc.stderr),exception='timeout')
    except OSError as exc:receipt.update(returncode=None,stdout='',stderr='',exception=str(exc))
    receipt['elapsed_seconds']=time.monotonic()-start
    return receipt


def run(backend,build_receipt,destination):
    verify_execution_freeze();ctx=context();build=load(build_receipt)
    require(build['backend']==backend and build['returncode']==0,'qualified build receipt')
    for name,expected in build['artifacts'].items():require(sha(Path(name))==expected,'build artifact: '+name)
    artifact=Path(build['executable']);require(str(artifact) in build['artifacts'],'missing executable pin')
    destination.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(build_receipt, destination/'build-receipt.json')
    index={'backend':backend,'build_receipt':'build-receipt.json','build_receipt_sha256':sha(build_receipt),'records':[],'status':'running'}
    selected=None
    def call(request):
        i=len(index['records']);receipt=invoke(backend,artifact,request,destination/f'wire-{i:03}')
        path=destination/f'{i:03}.json.gz';path.write_bytes(gzip.compress((json.dumps(receipt,allow_nan=False)+'\n').encode(),mtime=0))
        index['records'].append({'id':request['id'],'file':path.name,'sha256':sha(path)})
        (destination/'index.json').write_text(json.dumps(index,indent=2)+'\n')
        response=receipt.get('response',{})
        print(json.dumps({'backend':backend,'id':request['id'],'ok':response.get('ok'),'elapsed_seconds':receipt['elapsed_seconds'],'points':len(response.get('points',[]))}),flush=True)
        return response
    for request in ctx['requests']:
        response=call(request)
        if request['id']=='compression-e0.735-p100000/N1024':selected=response
    for probe in ctx['probes']['probes']:
        call(probe)
        call(dict(ctx['probes']['recover_after_each'],id='recovery/'+probe['id']))
    if selected and selected.get('ok') is True and len(selected.get('points',[]))==1026:
        # No reference history is used: one actual candidate parent, never mutated.
        parent=list(selected['points'][513]['state']);base=ctx['probes']['recover_after_each']['args']
        parent_csv=','.join(repr(float(x)) for x in parent)
        for trial in ctx['probes']['dependent_transactions']['trials']:
            args=[base[0],base[1],parent_csv,trial['strain']]
            if 'settings' in trial:args.append(trial['settings'])
            call({'id':'transaction/'+trial['id'],'function':'atlas_integrate_with_settings' if len(args)==5 else 'atlas_integrate','types':['string']*len(args),'args':args})
        # Round-trip the complete incoming engine layout, including temporary gamma.
        restored=[float(x) for x in parent_csv.split(',')];require(restored==parent,'restart serialization')
        call({'id':'transaction/restart-A','function':'atlas_integrate','types':['string']*4,'args':[base[0],base[1],','.join(repr(x) for x in restored),'1e-5,-5e-6,-5e-6,0,0,0']})
    else:index['transactions_not_attempted']='actual candidate parent unavailable; no reference substitution'
    index['status']='completed';(destination/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    return index


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('backend',choices=['native','wasm']);p.add_argument('build_receipt',type=Path);p.add_argument('destination',type=Path);a=p.parse_args()
    run(a.backend,a.build_receipt.resolve(),a.destination.resolve())
