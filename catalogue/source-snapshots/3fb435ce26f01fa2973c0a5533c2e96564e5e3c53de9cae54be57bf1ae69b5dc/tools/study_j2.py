"""Independent J2 reference and prospective native/Wasm qualification.

The oracle uses Cartesian 3x3 tensors and analytical radial projection; it does
not load Atlas expressions. References must be frozen before backend execution.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/ingestion/j2-linear-hardening/execution-v1'
MODEL = 'j2-linear-isotropic-hardening-be'
SETTINGS = '1e-11,1e-6,60,0,1,20'  # no subdivision: named BE update
P = [100000., 20e6, 12e6, 60000., 1.2e6]
ZERO = [0.] * 8

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p, x):
    p.write_text(json.dumps(x, indent=2, allow_nan=False) + '\n')

def csv(v):
    return ','.join(format(x, '.17g') for x in v)

def matrix(v):
    a,b,c,d,e,f=v
    return [[a,d/math.sqrt(2),f/math.sqrt(2)],
            [d/math.sqrt(2),b,e/math.sqrt(2)],
            [f/math.sqrt(2),e/math.sqrt(2),c]]

def mandel(a):
    return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],
            math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]

def oracle(z, de, p):
    _,K,G,sy,H=p
    s=matrix(z[:6]);d=matrix(de)
    tr=sum(d[i][i] for i in range(3))
    trial=[[s[i][j]+2*G*(d[i][j]-(tr/3 if i==j else 0))+
            (K*tr if i==j else 0) for j in range(3)] for i in range(3)]
    mean=sum(trial[i][i] for i in range(3))/3
    t=[[trial[i][j]-(mean if i==j else 0) for j in range(3)] for i in range(3)]
    q=math.sqrt(1.5*sum(t[i][j]**2 for i in range(3) for j in range(3)))
    gamma=max(0.,(q-sy-H*z[6])/(3*G+H))
    factor=1-3*G*gamma/q if q else 1.
    return mandel([[factor*t[i][j]+(mean if i==j else 0) for j in range(3)]
                   for i in range(3)])+[z[6]+gamma,gamma]

def tangent(z, de, p):
    # Derivative of independent closed-form projection, including history rows.
    _,K,G,sy,H=p
    x=oracle(z,de,p);g=x[7]
    mean=sum(z[:3])/3+K*sum(de[:3]);tr=sum(de[:3])
    trial=[z[i]+2*G*(de[i]-(tr/3 if i<3 else 0))+
           (K*tr if i<3 else 0) for i in range(6)]
    s=[trial[i]-(mean if i<3 else 0) for i in range(6)]
    q=math.sqrt(1.5*sum(v*v for v in s))
    columns=[]
    for j in range(6):
        dt=[2*G*((1 if i==j else 0)-(1/3 if i<3 and j<3 else 0)) for i in range(6)]
        dp=K if j<3 else 0
        dq=1.5*sum(a*b for a,b in zip(s,dt))/q if q else 0
        dg=dq/(3*G+H) if g>0 else 0
        a=1-3*G*g/q if g else 1
        da=-3*G*(dg/q-g*dq/q**2) if g else 0
        columns.append([a*dt[i]+da*s[i]+(dp if i<3 else 0) for i in range(6)]+[dg,dg])
    return [[columns[j][i] for j in range(6)] for i in range(8)]

def case(name,z,de,p=P,mode='integrate',settings=SETTINGS,ok=True):
    args=[MODEL,csv(p),csv(z),csv(de),settings]
    c=dict(id=name,mode=mode,args=args,ok=ok,
           argv=['--mode',mode,'--model',MODEL,'--parameters',args[1],
                 '--initial',args[2],'--strain',args[3],'--integration-settings',settings],
           call='atlas_'+('linearize' if mode=='linearize' else 'integrate')+'_with_settings',
           types=['string']*5,expected=oracle(z,de,p) if ok else z)
    if mode=='linearize' and ok:c['tangent']=tangent(z,de,p)
    return c

def cases():
    out=[]
    directions=[[2,-1,-1,0,0,0],[0,0,0,math.sqrt(2),0,0],
                [.7,-.2,-.5,.6,-.4,.3],[-1,2,-1,.3,.8,-.2]]
    for H in (0.,1.2e6,12e6):
        p=P[:];p[-1]=H
        for mean in (-100000.,0.,200000.):
            for i,d in enumerate(directions):
                for amplitude in (.0001,.003):
                    out.append(case(f'H{H}-p{mean}-d{i}-a{amplitude}',[mean]*3+[0]*3+[.004,0],
                                    [amplitude*v for v in d],p))
    out += [case('zero-origin',ZERO,[0]*6),case('hydrostatic',ZERO,[.002]*3+[0]*3),
            case('yield-boundary-hold',[40000,-20000,-20000,0,0,0,0,0],[0]*6),
            case('nonzero-temporary-reset',[0]*6+[.01,.03],[0]*6)]
    # Closed-reference path endpoints are explicit restart inputs, with nonzero
    # incoming temporary multipliers. Every returned history scalar is checked.
    for label,path in [('reverse',[[.001,-.0005,-.0005,0,0,0]]*5+
                                  [[-.001,.0005,.0005,0,0,0]]*10),
                       ('nonproportional',[[.002,-.001,-.001,0,0,0],
                                           [0,0,0,.003,-.001,.002],
                                           [-.002,.001,.001,0,0,0],[0]*6]*3)]:
        z=ZERO[:]
        for i,d in enumerate(path):
            c=case(f'{label}-{i}',z,d);out.append(c);z=c['expected']
    for label,d in [('elastic',[.0001,-.00005,-.00005,.00003,0,0]),
                    ('plastic',[.003,-.001,-.002,.001,-.002,.001])]:
        out.append(case('tangent-'+label,ZERO,d,mode='linearize'))
    out.append(case('budget-rollback',[0]*6+[.01,.03],[.003,-.001,-.002,.002,0,0],
                    settings='1e-11,1e-6,1,0,1,0',ok=False))
    for label,z in [('negative-alpha',[0]*6+[-.01,0]),
                    ('overstress',[1e6,-5e5,-5e5,0,0,0,0,0])]:
        out.append(case(label,z,[0]*6,ok=False))
    for label,pos,val in [('missing-state',2,''),('short-state',2,'1,2'),
                          ('negative-G',1,csv([P[0],P[1],-1,P[3],P[4]]))]:
        c=case(label,ZERO,[0]*6,ok=False);c['expected']=None;c['args'][pos]=val
        flag={1:'--parameters',2:'--initial'}[pos];c['argv'][c['argv'].index(flag)+1]=val;out.append(c)
        out.append(case('recovery-after-'+label,ZERO,[.003,-.001,-.002,.001,0,0]))
    return out

def close(a,b,tol):
    assert len(a)==len(b)
    assert all(type(x) in (int,float) and math.isfinite(x) for x in a)
    err=max((abs(x-y) for x,y in zip(a,b)),default=0)
    assert err<=tol,(err,tol)
    return err

def assess(c,data):
    assert type(data['ok']) is bool and data['ok']==c['ok'],(c['id'],data)
    if not c['ok']:
        if c['expected'] is not None:assert data['state']==c['expected'],c['id']
        return {'stress':0,'history':0,'tangent':0}
    assert data['model']==MODEL
    assert data['parameters']==list(map(float,c['args'][1].split(',')))
    assert data['initial']==list(map(float,c['args'][2].split(',')))
    assert data['strain']==list(map(float,c['args'][3].split(',')))
    assert data['diagnostics']['substeps']==1
    assert data['diagnostics']['increment_fractions']==[1]
    z=data['state'];ref=c['expected']
    result={'stress':close(z[:6],ref[:6],.002),'history':close(z[6:],ref[6:],2e-10),'tangent':0}
    p=data['parameters'];s=matrix(z[:6]);mean=sum(s[i][i] for i in range(3))/3
    q=math.sqrt(1.5*sum((s[i][j]-(mean if i==j else 0))**2 for i in range(3) for j in range(3)))
    assert q-p[3]-p[4]*z[6] <= .003
    assert z[6]>=data['initial'][6]-2e-10 and z[7]>=-2e-10
    if 'tangent' in c:
        assert data['tangent_ok'] is True
        assert len(data['state_tangent'])==8
        for i,(a,b) in enumerate(zip(data['state_tangent'],c['tangent'])):
            result['tangent']=max(result['tangent'],close(a,b,.2 if i<6 else 2e-8))
    return result

def assess_rows(cs,rows):
    assert [c['id'] for c in cs]==[r['id'] for r in rows]
    errors=[]
    for c,row in zip(cs,rows):
        assert len(row['calls'])==2
        values=[]
        for call in row['calls']:
            assert call['returncode']==(0 if c['ok'] else 1)
            data=json.loads(call['stdout']);errors.append(assess(c,data));values.append(data)
        assert values[0]==values[1],c['id']+' replay mismatch'
    return dict(passed=True,cases=len(cs),calls=len(rows)*2,
                maximum_errors={k:max(x[k] for x in errors) for k in errors[0]})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['freeze','native','assess','parity']);ap.add_argument('paths',nargs='*');a=ap.parse_args()
    if a.mode=='freeze':
        assert not (BASE/'references.json').exists(),'references already frozen'
        dump(BASE/'references.json',dict(version='j2-reference-1',cases=cases(),settings=SETTINGS,
             budgets=dict(stress_Pa=.002,history=2e-10,stress_tangent_Pa=.2,history_tangent=2e-8,
                          backend_stress_Pa=1e-5,backend_history=1e-11,backend_tangent_Pa=.01)))
    elif a.mode=='native':
        solver,dest=a.paths;cs=json.loads((BASE/'references.json').read_text())['cases'];rows=[]
        for c in cs:
            calls=[]
            for _ in range(2):
                r=subprocess.run([solver,*c['argv']],text=True,capture_output=True,timeout=30)
                calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
            rows.append(dict(id=c['id'],calls=calls));dump(Path(dest),rows)
        print(json.dumps(assess_rows(cs,rows),indent=2))
    elif a.mode=='assess':
        cs=json.loads((BASE/'references.json').read_text())['cases'];rows=json.loads(Path(a.paths[0]).read_text())
        print(json.dumps(assess_rows(cs,rows),indent=2))
    else:
        cs=json.loads((BASE/'references.json').read_text())['cases'];left,right=[json.loads(Path(p).read_text()) for p in a.paths]
        assess_rows(cs,left);assess_rows(cs,right)
        for c,l,r in zip(cs,left,right):
            x,y=[json.loads(v['calls'][0]['stdout']) for v in (l,r)]
            assert x['ok']==y['ok']
            if 'state' in x:
                close(x['state'][:6],y['state'][:6],1e-5);close(x['state'][6:],y['state'][6:],1e-11)
            if c['ok'] and 'tangent' in c:
                for i,(u,v) in enumerate(zip(x['state_tangent'],y['state_tangent'])):close(u,v,.01 if i<6 else 1e-11)
        print(json.dumps(dict(passed=True,cases=len(cs),both_backends_independently_assessed=True),indent=2))

if __name__=='__main__':main()
