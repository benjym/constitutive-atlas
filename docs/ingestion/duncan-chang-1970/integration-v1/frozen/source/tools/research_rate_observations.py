"""Generic frozen-corpus instantaneous-rate transport and numerical assessment.

No constitutive equations or model-ID branches. Source studies supply explicit
expected values and budgets; collection retains raw evidence before assessment.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from atlas.model import ROOT, load, validate, reject_duplicate_keys


def require(ok,message):
    if not ok: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(),parse_constant=lambda _:require(False,'nonfinite JSON'))


def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()


def finite(value):
    if type(value) not in (int,float): return False
    try: return math.isfinite(value)
    except OverflowError: return False


class Snapshot:
    """Hash and parse the same held bytes; reject inputs changed during audit."""
    def __init__(self): self.blobs={}
    def blob(self,path):
        path=Path(path).resolve()
        if path not in self.blobs: self.blobs[path]=path.read_bytes()
        return self.blobs[path]
    def sha(self,path): return hashlib.sha256(self.blob(path)).hexdigest()
    def read(self,path):
        return json.loads(self.blob(path),object_pairs_hook=reject_duplicate_keys,
                          parse_constant=lambda _:require(False,'nonfinite JSON'))
    def check(self):
        for path,blob in self.blobs.items():
            require(path.read_bytes()==blob,'input changed during audit: '+str(path))


def error_measure(a,b):
    """None denotes a difference exceeding finite binary64 range, always a failure."""
    error=abs(a-b)
    return error if math.isfinite(error) else None


def vector(value,size): return type(value)is list and len(value)==size and all(finite(v) for v in value)


def same(a,b):
    if type(a)is bool or type(b)is bool: return type(a)is type(b) and a==b
    if finite(a) and finite(b): return a==b
    if type(a)is not type(b): return False
    if type(a)is dict: return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if type(a)is list: return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b


def checked_protocol(path,snapshot=None):
    snapshot=snapshot or Snapshot();read=snapshot.read;sha=snapshot.sha
    protocol=read(path)
    require(protocol.get('version')=='research-instantaneous-rate-protocol-0.1','protocol version')
    for name,pin in protocol['files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'relative source pin')
        require(sha(ROOT/name)==pin,'frozen source changed: '+name)
    require(protocol['model_file'] in protocol['files'],'model source pin required')
    model=read(ROOT/protocol['model_file']);validate(model)
    require(model['integration']=='rate','instantaneous rate model required')
    require(same(model,protocol['model_definition']),'frozen definition identity')
    size=sum(6 if s['shape']=='sym' else 1 for s in model['state'])
    seen=set()
    for case in protocol['cases']:
        require(type(case['id'])is str and case['id'] not in seen,'unique corpus ID');seen.add(case['id'])
        args=case['args'];require(type(args)is list and len(args)==4 and all(type(x)is str and '\n' not in x and '\t' not in x and '\r' not in x for x in args),'four literal CSV arguments')
        require(args[0]==model['id'],'single model corpus')
        expect=case['expectation'];require(type(expect['ok'])is bool,'Boolean expected status')
        if expect.get('parser_error'):
            require(expect['parser_error']is True and expect['ok']is False,'parser rejection contract')
        else:
            for text in args[1:]: require(all(finite(float(x)) for x in text.split(',')),'finite numeric corpus CSV')
            if expect['ok']:
                require(vector(expect['values'],size) and vector(expect['absolute_budgets'],size)
                        and vector(expect['parity_budgets'],size),'complete expected rates/budgets')
                require(min(expect['absolute_budgets'])>=0 and min(expect['parity_budgets'])>=0,'nonnegative frozen budgets')
        if 'recovery_of' in case:
            require(case['recovery_of'] in seen and case['recovery_of']!=case['id'],'prior recovery control')
    require(len(protocol['cases'])>0,'nonempty corpus')
    snapshot.check()
    return protocol,model,size


def stream_text(protocol):
    return '--describe\n'+''.join('\t'.join(c['args'])+'\n' for c in protocol['cases'])


def build_receipt(path,protocol_path,backend,reopen=False,snapshot=None):
    snapshot=snapshot or Snapshot();read=snapshot.read;sha=snapshot.sha
    receipt=read(path)
    require(receipt['backend']==backend and receipt['protocol_sha256']==sha(protocol_path),'pre-execution build binding')
    require(type(receipt['artifacts'])is dict and set(receipt['artifacts'])==({'native'} if backend=='native' else {'loader','wasm'}),'build artifact roles')
    require(receipt['all_commands_succeeded']is True,'successful narrow build receipt')
    for entry in receipt['artifacts'].values():
        require(type(entry['path'])is str and type(entry['sha256'])is str and len(entry['sha256'])==64,'artifact identity')
        if reopen:require(sha(entry['path'])==entry['sha256'],'artifact bytes changed')
    snapshot.check()
    return receipt


def collect_native(protocol_path,build_path,output):
    snapshot=Snapshot();sha=snapshot.sha
    protocol,_,_=checked_protocol(protocol_path,snapshot)
    build=build_receipt(build_path,protocol_path,'native',True,snapshot)
    output=Path(output);raw=output.with_suffix('.transport.json')
    require(not output.exists() and not raw.exists(),'fresh observation/raw paths required')
    output.parent.mkdir(parents=True,exist_ok=True)
    argv=[build['artifacts']['native']['path'],'--stream'];text=stream_text(protocol)
    receipt={'version':'research-instantaneous-rate-observation-0.1','backend':'native',
             'protocol_sha256':sha(protocol_path),'build_receipt_sha256':sha(build_path),
             'build_receipt':build,'collector_sha256':sha(__file__),'completed':False}
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        p=subprocess.run(argv,input=text,text=True,capture_output=True,timeout=60)
        raw_doc={'argv':argv,'stdin':text,'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode}
    except subprocess.TimeoutExpired as exc:
        decode=lambda value:value.decode(errors='replace') if isinstance(value,bytes) else value
        raw_doc={'argv':argv,'stdin':text,'stdout':decode(exc.stdout),'stderr':decode(exc.stderr),'returncode':None,'exception':'TimeoutExpired'}
        raw.write_text(json.dumps(raw_doc,allow_nan=False)+'\n')
        receipt['transport_sha256']=sha(raw);output.write_text(json.dumps(receipt,indent=2)+'\n');raise
    raw.write_text(json.dumps(raw_doc,allow_nan=False)+'\n')
    receipt['transport_sha256']=sha(raw);receipt['completed']=p.returncode==0
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    snapshot.check()
    require(p.returncode==0,'nonzero process outcome retained')
    return receipt


def audit(protocol_path,build_path,observation_path,raw_path):
    snapshot=Snapshot();read=snapshot.read;sha=snapshot.sha
    protocol,model,size=checked_protocol(protocol_path,snapshot)
    observation=read(observation_path);backend=observation.get('backend')
    require(backend in ('native','wasm'),'observation backend')
    build=build_receipt(build_path,protocol_path,backend,snapshot=snapshot)
    require(observation.get('version')=='research-instantaneous-rate-observation-0.1'
            and observation.get('protocol_sha256')==sha(protocol_path),'observation/protocol identity')
    require(observation.get('completed')is True,'complete transport required')
    require(observation.get('build_receipt_sha256')==sha(build_path) and same(observation.get('build_receipt'),build),'build receipt identity')
    collector='tools/research_rate_observations.py' if backend=='native' else 'tools/collect_research_rates_wasm.mjs'
    require(observation.get('collector_sha256')==sha(ROOT/collector),'collector source identity')
    require(observation.get('transport_sha256')==sha(raw_path),'opaque raw companion hash')
    raw=read(raw_path)
    if backend=='native':
        require(raw.get('argv')==[build['artifacts']['native']['path'],'--stream'] and raw.get('stdin')==stream_text(protocol),'native command/control binding')
        require(type(raw.get('returncode'))is int and raw['returncode']==0 and type(raw.get('stderr'))is str,'native termination receipt')
        require(type(raw.get('stdout'))is str,'native raw stdout')
        lines=raw['stdout'].splitlines()
    else:
        require(type(raw)is list and len(raw)==1+len(protocol['cases']),'complete Wasm journal')
        lines=[]
        for i,row in enumerate(raw):
            require(row.get('name')==('atlas_describe' if i==0 else 'atlas_research_rate'),'CABI function')
            require(row.get('types')==([] if i==0 else ['string']*4),'CABI types')
            require(row.get('args')==([] if i==0 else protocol['cases'][i-1]['args']),'literal CABI controls')
            require(type(row.get('raw'))is str,'opaque CABI response');lines.append(row['raw'])
    require(len(lines)==1+len(protocol['cases']),'complete response count')
    parsed=[json.loads(line,parse_constant=lambda _:require(False,'nonfinite response')) for line in lines]
    descriptor=parsed[0]
    require(type(descriptor)is dict and same(descriptor.get('models'),[model]) and descriptor.get('sha256')==digest([model]),'compiled descriptor identity')
    failures=[];results=[];controls={}
    for case,response in zip(protocol['cases'],parsed[1:]):
        expect=case['expectation']
        require(type(response)is dict and response.get('ok')is expect['ok'],'rate success/rejection: '+case['id'])
        require(type(response.get('message'))is str and (response['message']=='' if expect['ok'] else bool(response['message'])),'response message')
        if expect.get('parser_error'):
            require(set(response)=={'ok','message'},'parser rejection shape')
        else:
            require(set(response)=={'ok','model','catalogue_hash','parameters','state','increment','values','message'},'echoed response shape')
            require(response['model']==model['id'] and response['catalogue_hash']==digest([model]),'response model identity')
            for text,key in zip(case['args'][1:],('parameters','state','increment')):
                require(type(response[key])is list and all(finite(x) for x in response[key])
                        and same(response[key],[float(x) for x in text.split(',')]),'finite numeric echo '+key)
            require(vector(response['values'],size) if expect['ok'] else response['values'] is None,'rate output shape')
        errors=None
        if expect['ok']:
            errors=[error_measure(a,b) for a,b in zip(response['values'],expect['values'])]
            for index,(error,budget) in enumerate(zip(errors,expect['absolute_budgets'])):
                if error is None or error>budget:failures.append({'case':case['id'],'component':index,'error':error,'error_overflow':error is None,'budget':budget})
        if 'recovery_of' in case:
            require(case['args']==controls[case['recovery_of']]['args'] and same(response,controls[case['recovery_of']]['response']),'persistent known-state recovery')
        controls[case['id']]={'args':case['args'],'response':response}
        results.append({'id':case['id'],'errors':errors,'response':response})
    snapshot.check()
    return {'version':'research-instantaneous-rate-assessment-0.1','backend':backend,
            'outcome':'passed' if not failures else 'failed','failures':failures,'cases':results,
            'protocol_sha256':sha(protocol_path),'observation_sha256':sha(observation_path),
            'transport_sha256':sha(raw_path),'build_receipt_sha256':sha(build_path),
            'claims':{'integration':False,'material_AD':False,'scientific_admission':False,'experimental_validation':False}}


def parity(protocol_path,native,wasm):
    # This compares pre-audited assessments; callers retain their bound raw evidence.
    protocol,model,size=checked_protocol(protocol_path)
    require(native['backend']=='native' and wasm['backend']=='wasm','parity backends')
    require(native['protocol_sha256']==wasm['protocol_sha256']==sha(protocol_path),'parity protocol')
    require(len(native['cases'])==len(wasm['cases'])==len(protocol['cases']),'complete parity corpus')
    for assessment in (native,wasm):
        require(assessment.get('version')=='research-instantaneous-rate-assessment-0.1' and assessment.get('outcome') in ('passed','failed'),'parity assessment contract')
    failures=[];maximum=0.;unbounded=False
    for case,n,w in zip(protocol['cases'],native['cases'],wasm['cases']):
        require(n['id']==w['id']==case['id'],'parity request alignment')
        for item in (n,w):
            response=item['response']
            require(type(response)is dict and response.get('ok') is case['expectation']['ok'],'parity response status')
            if case['expectation']['ok']:
                require(vector(response.get('values'),size),'parity output shape')
                require(response.get('model')==model['id'] and response.get('catalogue_hash')==digest([model]),'parity model identity')
        if not case['expectation']['ok']:continue
        for i,(a,b,budget) in enumerate(zip(n['response']['values'],w['response']['values'],case['expectation']['parity_budgets'])):
            error=error_measure(a,b)
            if error is None or error>budget:
                failures.append({'case':case['id'],'component':i,'error':error,'error_overflow':error is None,'budget':budget})
            if error is None or (budget==0 and error!=0):unbounded=True
            elif budget:
                ratio=error/budget
                if math.isfinite(ratio):maximum=max(maximum,ratio)
                else:unbounded=True
    return {'passed':not failures,'failures':failures,'maximum_parity_budget_fraction':None if unbounded else maximum,
            'parity_budget_fraction_unbounded':unbounded,
            'both_independent_assessments_passed':native['outcome']==wasm['outcome']=='passed'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',type=Path,required=True);p.add_argument('--build-receipt',type=Path,required=True)
    p.add_argument('--collect-native',action='store_true');p.add_argument('--observation',type=Path)
    p.add_argument('--transport',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();require(not a.output.exists(),'fresh output required')
    if a.collect_native:
        require(a.observation is None and a.transport is None,'no replay inputs during collection')
        collect_native(a.protocol,a.build_receipt,a.output)
    else:
        require(a.observation is not None and a.transport is not None,'explicit observation/raw companion required')
        result=audit(a.protocol,a.build_receipt,a.observation,a.transport)
        a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(result['outcome'])
        raise SystemExit(0 if result['outcome']=='passed' else 1)
