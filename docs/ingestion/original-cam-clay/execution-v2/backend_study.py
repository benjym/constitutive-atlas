"""Frozen OCC candidate corpus collector/assessor. No numerical gate tuning."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
DESIGN=BASE.parent/'control-selection-v1'
MODEL='original-cam-clay-sw-electronic-log-recovery-v1'
SETTINGS='1e-11,1e-6,60,0,1,20'
PARAMS=[1000.,1.2,.2,.04,2.5]

def csv(x):return ','.join(format(v,'.17g') for v in x)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def freeze():
    source=json.loads((DESIGN/'independent-review/candidate-review-results-36012205c441.json').read_text())
    assert source['passed'] and source['count']==407
    cases=[]
    for i,c in enumerate(source['cases']):
        # std::stod rejects decimal subnormal underflow on some libc platforms.
        # Transport rejection is permitted only for this frozen minsub request;
        # a successful response must still meet the source accuracy gate.
        small=any(0<abs(x)<sys.float_info.min for x in c['stored_de'])
        cases.append(dict(id=f'finite-{i:03}',name=c['name'],initial=c['old'],de=c['stored_de'],expected=c['expected'],allow_transport_rejection=small))
    initial=[100000.]*3+[0.]*3+[2.5+.2-.04-.2*math.log(100)]
    valid=cases[10]
    negatives=[dict(id='invalid-volume',initial=valid['initial'],de=[-1.,-1.,-1.,0.,0.,0.],parameters=PARAMS),dict(id='negative-specific-volume',initial=valid['initial'][:6]+[-1.],de=valid['de'],parameters=PARAMS),dict(id='negative-pressure',initial=[-1.,-1.,-1.,0.,0.,0.,1.7],de=valid['de'],parameters=PARAMS),dict(id='parameter-order',initial=valid['initial'],de=valid['de'],parameters=[1000.,1.2,.03,.04,2.5]),dict(id='outside-yield',initial=[200000.,-25000.,-25000.,0.,0.,0.,1.7],de=valid['de'],parameters=PARAMS)]
    paths=[]
    for n in (32,64,128,256):
        start=.002;end=.03;Lam=1-.04/.2;v0=initial[6];a=1.2*v0/(.04*Lam)
        p=100000*math.exp(-Lam+Lam*math.exp(-a*start));q=1.2*p*(-math.expm1(-a*start))
        paths.append(dict(id=f'undrained-{n}',initial=[p+2*q/3,p-q/3,p-q/3,0.,0.,0.,v0],increment=[(end-start)/n,-(end-start)/n/2,-(end-start)/n/2,0.,0.,0.],count=n,start=start,end=end))
    req=dict(identity='occ-native-wasm-log-recovery-v2',model=MODEL,model_sha256=sha(DESIGN/'candidate-v03-v3.json'),parameters=PARAMS,settings=SETTINGS,cases=cases,negatives=negatives,recovery=dict(initial=valid['initial'],de=valid['de'],expected=valid['expected']),paths=paths,policy=dict(source_relative_budget=2e-10,parity_relative_budget=2e-10,exact_repeat=True,exact_rollback=True,minimum_refinement_ratio=1.8,finest_analytic_error_budget=.003,subnormal_transport='May reject frozen minsub CSV request explicitly; never silently succeed with zero-stress hold. All others must succeed.'),evidence=dict(reference_path=str(DESIGN.relative_to(ROOT)/'independent-review/candidate-review-results-36012205c441.json'),reference_sha256=sha(DESIGN/'independent-review/candidate-review-results-36012205c441.json')))
    dump(BASE/'requests.json',req)
    print('frozen',len(cases),'finite cases,',len(negatives),'negative/recovery pairs,',sum(p['count'] for p in paths),'propagated steps')

def native(binary):
    req=json.loads((BASE/'requests.json').read_text())
    def call(z,de,params=None):
        params=req['parameters'] if params is None else params
        args=[str(binary),'--mode','integrate','--model',req['model'],'--parameters',csv(params),'--initial',csv(z),'--strain',csv(de),'--integration-settings',req['settings']]
        r=subprocess.run(args,capture_output=True,text=True)
        return dict(args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    rows=[]
    for c in req['cases']:rows.append(dict(id=c['id'],calls=[call(c['initial'],c['de']),call(c['initial'],c['de'])]))
    pairs=[]
    for c in req['negatives']:
        r=req['recovery'];pairs.append(dict(id=c['id'],bad=call(c['initial'],c['de'],c['parameters']),recovery=call(r['initial'],r['de'])))
    paths=[]
    for p in req['paths']:
        z=p['initial'];calls=[]
        for _ in range(p['count']):
            rr=call(z,p['increment']);calls.append(dict(initial=z,call=rr));o=json.loads(rr['stdout'])
            if not o.get('ok'):break
            z=o['state']
        # Exact restart from the saved midpoint state, replay final suffix.
        midway=len(calls)//2;restart=p['initial'] if not midway else json.loads(calls[midway-1]['call']['stdout'])['state'];replay=[]
        for _ in range(midway,p['count']):
            rr=call(restart,p['increment']);replay.append(rr);o=json.loads(rr['stdout'])
            if not o.get('ok'):break
            restart=o['state']
        paths.append(dict(id=p['id'],calls=calls,restart=replay))
    dump(BASE/'native-raw.json',dict(backend='native',binary_sha256=sha(binary),requests_sha256=sha(BASE/'requests.json'),cases=rows,negatives=pairs,paths=paths))


def assess(path):
    req=json.loads((BASE/'requests.json').read_text());raw=json.loads(path.read_text());assert raw['requests_sha256']==sha(BASE/'requests.json')
    worst=0.;rejects=[];physical=0
    def parsed(r):
        o=json.loads(r['stdout']);assert r['returncode']==(0 if o.get('ok') else 1)
        return o
    def compare(z,ref):
        nonlocal worst,physical
        assert len(z)==len(ref)==7 and all(math.isfinite(x) for x in z)
        error=max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(z,ref)))
        worst=max(worst,error);physical+=len(z)
        assert error<=req['policy']['source_relative_budget'],error
    assert [x['id'] for x in raw['cases']]==[x['id'] for x in req['cases']]
    for c,row in zip(req['cases'],raw['cases']):
        a,b=map(parsed,row['calls']);assert a==b
        if not a.get('ok'):
            assert c['allow_transport_rejection'] and c['id']=='finite-404' and c['de']==[0.,0.,0.,float.fromhex('0x0.0000000000001p-1022'),0.,0.],(c['name'],a)
            assert a.get('message') in ('stod','stod: out of range') and 'state' not in a,(c['name'],a)
            rejects.append(dict(id=c['id'],message=a.get('message')))
        else:
            compare(a['state'],c['expected'])
            if not any(c['de']):assert a['state']==c['initial'],(c['id'],'hold drift')
    assert len(raw['negatives'])==len(req['negatives'])
    for c,row in zip(req['negatives'],raw['negatives']):
        bad=parsed(row['bad']);assert not bad['ok'],(c['id'],bad)
        assert bad.get('state')==c['initial'],(c['id'],bad)
        good=parsed(row['recovery']);assert good['ok'];compare(good['state'],req['recovery']['expected'])
    assert [x['id'] for x in raw['paths']]==[x['id'] for x in req['paths']]
    assert [x['id'] for x in raw['negatives']]==[x['id'] for x in req['negatives']]
    errors=[]
    for p,rows in zip(req['paths'],raw['paths']):
        assert p['id']==rows['id'] and len(rows['calls'])==p['count']
        state=p['initial'];maximum=0.
        for i,row in enumerate(rows['calls']):
            assert row['initial']==state
            o=parsed(row['call']);assert o['ok'],(p['id'],i,o);state=o['state']
            assert len(state)==7 and all(math.isfinite(v) for v in state)
            t=p['start']+(p['end']-p['start'])*(i+1)/p['count'];v0=p['initial'][6];Lam=.8;a=1.2*v0/(.04*Lam)
            pressure=100000*math.exp(-Lam+Lam*math.exp(-a*t));q=1.2*pressure*(-math.expm1(-a*t))
            exact=[pressure+2*q/3,pressure-q/3,pressure-q/3,0.,0.,0.,v0]
            maximum=max(maximum,max(abs(state[j]-exact[j])/100000 for j in range(6)),abs(state[6]-v0))
        offset=len(rows['calls'])//2;assert len(rows['restart'])==p['count']-offset
        for first,again in zip(rows['calls'][offset:],rows['restart']):assert parsed(first['call'])==parsed(again)
        errors.append(maximum)
    ratios=[a/b for a,b in zip(errors,errors[1:])]
    assert min(ratios)>=req['policy']['minimum_refinement_ratio'];assert errors[-1]<=req['policy']['finest_analytic_error_budget']
    result=dict(passed=True,backend=raw['backend'],raw_sha256=sha(path),requests_sha256=sha(BASE/'requests.json'),finite_cases=len(req['cases']),physical_scalars=physical,worst_relative_source_error=worst,explicit_subnormal_transport_rejections=rejects,negative_recovery_pairs=len(req['negatives']),propagated_steps=sum(p['count'] for p in req['paths']),source_path_errors=errors,refinement_ratios=ratios,exact_repeat_restart_rollback=True)
    dump(path.with_name(path.stem+'-assessment.json'),result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['freeze','native','assess']);a.add_argument('path',nargs='?');x=a.parse_args()
    if x.mode=='freeze':freeze()
    elif x.mode=='native':native(Path(x.path))
    else:assess(Path(x.path))
