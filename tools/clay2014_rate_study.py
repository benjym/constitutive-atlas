"""Source-bound instantaneous research rates; no integration or admission."""
import argparse, copy, hashlib, json, math, subprocess
from pathlib import Path
from atlas.model import ROOT, load
from tools import reference_clay2014_cartesian as oracle
MODEL_PATH=ROOT/'models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json'
PACKET=ROOT/'catalogue/investigations/clay2014-rates-v1'
REFERENCE=PACKET/'reference.json'
VERSION='clay2014-instantaneous-rates-v1'
PARITY_POLICY=dict(stress_scaled_bound=5e-13,stress_absolute_floor_Pa=2e-11,void_scaled_bound=2e-14,void_absolute_floor=2e-16)

def require(ok,message):
    if not ok: raise ValueError(message)
def finite(x):
    try:return type(x) in (int,float) and math.isfinite(x)
    except OverflowError:return False
def vector(x,n):return type(x)is list and len(x)==n and all(finite(v)for v in x)
def same(a,b):
    if finite(a) and finite(b):return a==b
    if type(a)is not type(b):return False
    if type(a)is dict:return set(a)==set(b)and all(same(a[k],b[k])for k in a)
    if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text(),parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON')))
def csv(values):return ','.join(format(x,'.17g')for x in values)
def checked_reference():
    ref=read(REFERENCE);require(digest(ref)==digest(oracle.build_reference()),'frozen independent reference differs from fresh replay')
    model=load(MODEL_PATH);require(ref['parameter_order']==list(model['parameters']),'parameter order mismatch')
    require(len(model['state'])==2 and model['state'][0]['shape']=='sym' and model['state'][1]['name']=='e','seven-state layout')
    ids=[c['id']for c in ref['cases']+ref['invalid_cases']];require(len(ids)==len(set(ids)),'duplicate reference ID')
    for c in ref['cases']:
        require(vector(c['state'],7)and vector(c['increment'],6)and vector(c['expected'],7),'reference vectors')
        require(set(c['parameters'])==set(ref['parameter_order']),'explicit parameters')
        stress=max(1.,math.hypot(*c['state'][:6]))*math.hypot(*c['increment']);void=max(1.,(1+c['state'][6])*math.hypot(*c['increment']))
        require(c['stress_scale']==stress and c['void_scale']==void,'reference physical scales')
    return ref,model

def requests(ref,model):
    def request(case,role):return dict(id=case['id'],role=role,model=model['id'],parameters=[case['parameters'][k]for k in ref['parameter_order']],state=case['state'],increment=case['increment'])
    out=[request(c,'valid')for c in ref['cases']]
    for c in ref['invalid_cases']:
        out.extend([request(c,'invalid'),request(ref['cases'][0],'recovery')])
    return out

def identity(ref,model,backend):
    paths=['tools/clay2014_rate_study.py','tools/test_clay2014_rates_wasm.mjs','tools/reference_clay2014_cartesian.py','tests/research_rate_driver.cpp','atlas/compiler.py','atlas/dsl.py','atlas/model.py','atlas/structure.py','atlas/scalar_math.py','atlas/symmetric_expm.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp',str(MODEL_PATH.relative_to(ROOT)),str(REFERENCE.relative_to(ROOT))]
    return dict(version=VERSION,backend=backend,model_definition=model,catalogue_hash=digest([model]),reference_sha256=digest(ref),source_sha256=oracle.SOURCE_SHA256,policy=ref['policy'],parity_policy=PARITY_POLICY,artifact_scope='Collector before/after artifact stability; portable archival assessment does not reopen artifacts.',source_pins={p:sha(ROOT/p)for p in paths},claims=dict(public_admission=False,experimental_validation=False,integration=False,AD=False,source_repair=False))

def response(a,r,model,ok):
    require(type(a)is dict and a.get('ok')is ok,'response status')
    require(a.get('model')==r['model'] and a.get('catalogue_hash')==digest([model]),'model/catalogue receipt')
    for key,n in [('parameters',len(model['parameters'])),('state',7),('increment',6)]:
        require(vector(a.get(key),n)and a[key]==r[key],'response echo '+key)
    require(type(a.get('message'))is str and (a['message']==''if ok else bool(a['message'])),'response message')
    require(vector(a.get('values'),7)if ok else a.get('values')is None,'response values')

def verify(report):
    ref,model=checked_reference();backend=report.get('backend');require(backend in ('native','wasm'),'backend')
    for k,v in identity(ref,model,backend).items():require(same(report.get(k),v),'report identity '+k)
    d=report.get('descriptor');require(type(d)is dict and same(d.get('models'),[model])and d.get('sha256')==digest([model]),'descriptor')
    wanted=requests(ref,model);calls=report.get('calls');require(type(calls)is list and len(calls)==len(wanted),'complete calls')
    policy=ref['policy'];targets={c['id']:c for c in ref['cases']};maximum_stress=maximum_void=0.;recovery=None
    for c,r in zip(calls,wanted):
        require(same(c.get('request'),r),'request corpus/order');a=c.get('response');valid=r['role']!='invalid';response(a,r,model,valid)
        if not valid:continue
        target=targets[r['id']];got=a['values'];want=target['expected']
        stress=math.hypot(*(x-y for x,y in zip(got[:6],want[:6])));void=abs(got[6]-want[6])
        stress_limit=policy['stress_scaled_bound']*target['stress_scale']+policy['stress_absolute_floor_Pa'];void_limit=policy['void_scaled_bound']*target['void_scale']+policy['void_absolute_floor']
        require(stress<=stress_limit and void<=void_limit,'independent rate error budget: '+r['id'])
        if not any(r['increment']):require(all(x==0 for x in got),'zero loading must have exact seven zero rates')
        maximum_stress=max(maximum_stress,stress/stress_limit);maximum_void=max(maximum_void,void/void_limit)
        if r['role']=='valid'and r['id']==ref['cases'][0]['id']:recovery=copy.deepcopy(a)
        if r['role']=='recovery':require(same(a,recovery),'persistent recovery differs from original control')
    require(report.get('persistent_instance')is True,'persistent instance assertion')
    for k in ('transport_sha256',*(['native_sha256']if backend=='native'else ['native_report_sha256','wasm_loader_sha256','wasm_binary_sha256'])):
        value=report.get(k);require(type(value)is str and len(value)==64 and all(x in '0123456789abcdef'for x in value),'artifact receipt '+k)
    return dict(valid_cases=len(ref['cases']),invalid_recovery_pairs=len(ref['invalid_cases']),call_count=len(calls),maximum_stress_budget_fraction=maximum_stress,maximum_void_budget_fraction=maximum_void)

def stream_request(r):return '\t'.join([r['model'],csv(r['parameters']),csv(r['state']),csv(r['increment'])])
def verify_transport(report,path):
    require(sha(path)==report.get('transport_sha256'),'transport file binding');raw=read(path);calls=report['calls'];expected=[report['descriptor']]+[c['response']for c in calls]
    if report['backend']=='native':
        require(type(raw.get('args'))is list and len(raw['args'])==2 and raw['args'][1]=='--stream','native stream argv')
        require(type(raw.get('returncode'))is int and raw['returncode']==0 and type(raw.get('stderr'))is str,'native status/stderr')
        require(raw.get('stdin')=='--describe\n'+''.join(stream_request(c['request'])+'\n'for c in calls),'native stdin binding')
        require(type(raw.get('stdout'))is str,'opaque native stdout');lines=raw['stdout'].splitlines();require(len(lines)==len(expected),'native raw row count')
        for line,want in zip(lines,expected):require(digest(json.loads(line))==digest(want),'native raw response binding')
    else:
        require(type(raw)is list and len(raw)==len(expected),'Wasm raw row count')
        for i,(row,want)in enumerate(zip(raw,expected)):
            require(row.get('name')==('atlas_describe'if i==0 else 'atlas_research_rate'),'C ABI function')
            require(row.get('types')==([]if i==0 else ['string']*4),'C ABI types')
            args=row.get('args');require(type(args)is list and len(args)==(0 if i==0 else 4),'C ABI arguments')
            if i:
                r=calls[i-1]['request'];require(args[0]==r['model'],'C ABI model')
                for value,key in zip(args[1:],('parameters','state','increment')):
                    require(type(value)is str,'C ABI CSV');parsed=[float(x)for x in value.split(',')];require(all(finite(x)for x in parsed)and parsed==r[key],'C ABI CSV/request')
            require(type(row.get('raw'))is str and digest(json.loads(row['raw']))==digest(want),'Wasm raw response binding')
    return len(expected)

def run(binary,output):
    ref,model=checked_reference();base=identity(ref,model,'native');binary_sha=sha(binary);req=requests(ref,model);text='--describe\n'+''.join(stream_request(r)+'\n'for r in req);transport=output.with_suffix('.transport.json')
    try:p=subprocess.run([str(binary),'--stream'],input=text,text=True,capture_output=True,timeout=60)
    except subprocess.TimeoutExpired as e:
        def decoded(v):return v.decode(errors='replace')if isinstance(v,bytes)else v
        transport.write_text(json.dumps(dict(args=[str(binary),'--stream'],stdin=text,stdout=decoded(e.stdout),stderr=decoded(e.stderr),returncode=None,exception='TimeoutExpired'))+'\n');raise
    transport.write_text(json.dumps(dict(args=[str(binary),'--stream'],stdin=text,stdout=p.stdout,stderr=p.stderr,returncode=p.returncode),allow_nan=False)+'\n')
    require(sha(binary)==binary_sha,'native artifact changed during collection');require(p.returncode==0,'native stream status');rows=[json.loads(line)for line in p.stdout.splitlines()];require(len(rows)==1+len(req),'native response count')
    report=base|dict(native_sha256=binary_sha,descriptor=rows[0],calls=[dict(request=r,response=a)for r,a in zip(req,rows[1:])],persistent_instance=True,transport_sha256=sha(transport))
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');report['assessment']=verify(report);verify_transport(report,transport);output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');return report

def compare(wasm,native,native_path,wasm_transport,native_transport):
    verify(wasm);verify(native);require(same(read(native_path),native),'native parsed report/file mismatch');require(wasm['backend']=='wasm'and native['backend']=='native','parity backends');require(wasm['native_report_sha256']==sha(native_path),'native report file binding')
    verify_transport(wasm,wasm_transport);verify_transport(native,native_transport);maximum=0.
    ref,_=checked_reference();targets={c['id']:c for c in ref['cases']};bound=ref['policy']['stress_scaled_bound']
    for a,b in zip(wasm['calls'],native['calls']):
        require(same(a['request'],b['request']),'backend request mismatch')
        if a['request']['role']=='invalid':continue
        c=targets[a['request']['id']];x=a['response']['values'];y=b['response']['values'];stress=math.hypot(*(u-v for u,v in zip(x[:6],y[:6])));void=abs(x[6]-y[6])
        sl=PARITY_POLICY['stress_scaled_bound']*c['stress_scale']+PARITY_POLICY['stress_absolute_floor_Pa'];vl=PARITY_POLICY['void_scaled_bound']*c['void_scale']+PARITY_POLICY['void_absolute_floor']
        require(stress<=sl and void<=vl,'native/Wasm parity budget');maximum=max(maximum,stress/sl,void/vl)
    return maximum

def verify_artifacts(report,path):
    path=Path(path)
    if report['backend']=='native':require(sha(path)==report['native_sha256'],'native artifact receipt mismatch')
    else:
        require(sha(path)==report['wasm_loader_sha256'],'Wasm loader receipt mismatch')
        require(sha(path.with_suffix('.wasm'))==report['wasm_binary_sha256'],'Wasm binary receipt mismatch')
    return True

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifact',type=Path);p.add_argument('--native',type=Path);p.add_argument('--report',type=Path);p.add_argument('--transport',type=Path);p.add_argument('--native-report',type=Path);p.add_argument('--native-transport',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(bool(a.native)!=bool(a.report),'one native/report required')
    report=run(a.native,a.output)if a.native else read(a.report);raw=a.output.with_suffix('.transport.json')if a.native else a.transport;require(raw is not None,'explicit transport required')
    result=verify(report);
    if a.artifact:verify_artifacts(report,a.artifact)
    result['transport_rows']=verify_transport(report,raw)
    if report['backend']=='wasm':
        require(a.native_report is not None and a.native_transport is not None,'Wasm assessment requires native report and transport');result['maximum_parity_budget_fraction']=compare(report,read(a.native_report),a.native_report,raw,a.native_transport)
    report['assessment']=result;a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
