"""Source-specific Maxwell qualification through ordinary time/schedule APIs.
No vendor binaries or model-specific kernel. Analytical references are frozen
before execution; see docs/ingestion/maxwell-itasca900/integration-v1/PLAN.md.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.model import load
from atlas.schedule import schedule_command

BASE=ROOT/'docs/ingestion/maxwell-itasca900/integration-v1'
MODEL='maxwell-itasca900-zero-spin-ode'
CSV=lambda a:','.join(format(v,'.17g') for v in a)
Z=[140000,80000,80000,3000,-2000,1000]
P=[20e6,12e6,24e6]
ZERO=[0]*6

def dev(z):
    p=sum(z[:3])/3
    return [v-p if i<3 else v for i,v in enumerate(z)]
def exact(z,rate,p,h):
    K,G,eta=p;tau=eta/G;d=dev(rate);s=dev(z);mean=sum(z[:3])/3+K*sum(rate[:3])*h
    decay=math.exp(-h/tau);gain=-2*eta*math.expm1(-h/tau)
    return [(mean if i<3 else 0)+decay*s[i]+gain*d[i] for i in range(6)]
def hold(q='strain'):return {'quantity':q,'kind':'hold'}
def rate(v):return {'quantity':'strain','kind':'rate','value':v}
def segment(name,duration,controls,samples=8):return dict(id=name,duration=duration,samples=samples,controls=controls)
def specification(name,z=Z,p=P):
    return {'schema_version':'0.2','units':'SI','model':MODEL,'parameters':p,'initial':z,'initial_strain':ZERO,'initial_strain_rate':ZERO,'start_time':0,'segments':[],'solver':{'method':'backward-euler-step-doubling','relative_tolerance':1e-8,'absolute_scale_fraction':1e-11,'maximum_substeps':100000}}
def direct(name,z,p,d,h,**settings):
    start=settings.pop('start',3)
    opts=dict(rtol=1e-9,atol=1e-12,minimum=1e-12,maximum=1e6,budget=100000,**settings)
    args=[MODEL,CSV(p),CSV(z),CSV(d),start,h,opts['rtol'],opts['atol'],opts['minimum'],opts['maximum'],opts['budget']]
    argv=['--mode','integrate-time','--model',MODEL,'--parameters',CSV(p),'--initial',CSV(z),'--strain-rate',CSV(d),'--start-time',str(start),'--duration',str(h),'--rtol',str(opts['rtol']),'--atol',str(opts['atol']),'--min-time-step',str(opts['minimum']),'--max-time-step',str(opts['maximum']),'--max-substeps',str(opts['budget'])]
    return dict(id=name,kind='direct',argv=argv,call='atlas_integrate_time',types=['string']*4+['number']*7,args=args,ok=True,expected=exact(z,d,p,h),time=start+h,tolerance=.05)
def schedule_case(name,s,reference,tolerance=15):
    cmd=schedule_command(s,'SOLVER');args=dict(zip(cmd[1::2],cmd[2::2]))
    wire=args['--segments'];setting=s['solver']
    abi=[MODEL,CSV(s['parameters']),CSV(s['initial']),CSV(s['initial_strain']),CSV(s['initial_strain_rate']),wire,args['--segment-ids'],s['start_time'],setting['relative_tolerance'],setting['absolute_scale_fraction'],1e-12,1e6,setting['maximum_substeps'],1e-10,40]
    times=[s['start_time']];t=s['start_time']
    for seg in s['segments']:
        times.extend(t+seg['duration']*i/seg['samples'] for i in range(1,seg['samples']+1));t+=seg['duration']
    refs=[dict(time=t,**reference(t)) for t in times]
    return dict(id=name,kind='schedule',specification=s,argv=cmd[1:],call='atlas_run_schedule',types=['string']*7+['number']*8,args=abi,ok=True,references=refs,tolerance=tolerance,strain_tolerance=2e-7,time=t)
def make_cases():
    cases=[]
    for tau in (.2,2,20):
        p=[P[0],P[1],P[1]*tau]
        for ratio in (.01,.5,4):
            d=[.001,-.0002,.0003,.0007,-.0006,.0005]
            cases.append(direct(f'tensor-tau{tau}-duration{ratio}',Z,p,d,tau*ratio))
    cases += [direct('hydrostatic',[1e5]*3+[0]*3,P,[.001]*3+[0]*3,4),direct('relaxation',Z,P,ZERO,8)]
    s=specification('relax');s['segments']=[segment('relax',8,[hold() for _ in range(6)])]
    cases.append(schedule_case('relaxation-schedule',s,lambda t:dict(state=exact(Z,ZERO,P,t),strain=ZERO)))
    s=specification('creep');s['segments']=[segment('creep',4,[hold('stress') for _ in range(6)])]
    creep=lambda t:dict(state=Z,strain=[v*t/(2*P[2]) for v in dev(Z)])
    cases.append(schedule_case('creep-schedule',s,creep))
    s=specification('creep-coarse-samples');s['segments']=[segment('creep',4,[hold('stress') for _ in range(6)],samples=1)]
    cases.append(schedule_case('creep-one-sample',s,creep))
    K,G,eta=P;loadP=1e5;A=K+4*G/3;a=2*G/A;b=K*G/(eta*A);c=4*G/(3*A)
    z=[loadP*(1-a),loadP*(1-a),loadP,0,0,0]
    s=specification('oedometer',z);s['initial_strain']=[0,0,loadP/A,0,0,0];s['segments']=[segment('creep',8,[hold(),hold(),hold('stress'),hold(),hold(),hold()])]
    def oed(t):return dict(state=[loadP*(1-a*math.exp(-b*t))]*2+[loadP,0,0,0],strain=[0,0,loadP/K*(1-c*math.exp(-b*t)),0,0,0])
    cases.append(schedule_case('oedometer',s,oed))
    d=[.001,-.0005,-.0005,.0004,-.0003,.0002]
    s=specification('load-hold-reverse');s['segments']=[segment('load',1,list(map(rate,d)),4),segment('hold',1,[hold() for _ in range(6)],4),segment('reverse',1,list(map(rate,[-v for v in d])),4)]
    z1=exact(Z,d,P,1);z2=exact(z1,ZERO,P,1)
    def history(t):
        if t<=1:return dict(state=exact(Z,d,P,t),strain=[v*t for v in d])
        if t<=2:return dict(state=exact(z1,ZERO,P,t-1),strain=d)
        return dict(state=exact(z2,[-v for v in d],P,t-2),strain=[v*(3-t) for v in d])
    cases.append(schedule_case('load-hold-reverse',s,history))
    # Two fixed refinement settings; assessor requires smaller physical error.
    for suffix,rtol,atol in [('coarse',1e-4,1e-7),('fine',1e-8,1e-11)]:
        s=specification('refinement');s['solver'].update(relative_tolerance=rtol,absolute_scale_fraction=atol);s['segments']=[segment('relax',4,[hold() for _ in range(6)],4)]
        cases.append(schedule_case('refine-'+suffix,s,lambda t:dict(state=exact(Z,ZERO,P,t),strain=ZERO),tolerance=1000 if suffix=='coarse' else 15))
    # Explicit failure cases use unchanged parent and clock, including late work.
    bad=direct('late-budget-rollback',Z,P,ZERO,4);bad.update(ok=False,expected=Z,time=3);bad['args'][-2:]=[.25,2];i=bad['argv'].index('--max-time-step');bad['argv'][i+1]='.25';bad['argv'][-1]='2';cases.append(bad)
    for name,field,value in [('zero-duration',5,0),('negative-viscosity',1,CSV([P[0],P[1],-1])),('missing-state',2,''),('short-state',2,'1,2')]:
        bad=direct(name,Z,P,ZERO,4);bad.update(ok=False,expected=None);bad['args'][field]=value
        opt={5:'--duration',1:'--parameters',2:'--initial'}[field];bad['argv'][bad['argv'].index(opt)+1]=str(value);cases.append(bad)
    s=specification('schedule-budget');s['solver']['maximum_substeps']=2;s['segments']=[segment('relax',4,[hold() for _ in range(6)],4)]
    bad=schedule_case('schedule-budget-rollback',s,lambda t:dict(state=Z,strain=ZERO));bad.update(ok=False,time=0);bad['references']=[dict(time=0,state=Z,strain=ZERO)];cases.append(bad)
    return cases

def norm_error(actual,expected,tolerance):
    assert len(actual)==len(expected)
    assert all(type(v) in (int,float) and math.isfinite(v) for v in actual)
    error=max(abs(a-b) for a,b in zip(actual,expected))
    assert error<=tolerance,(error,tolerance)
    return error

def assess(case,data):
    assert type(data['ok']) is bool and data['ok']==case['ok'],(case['id'],data)
    if not case['ok']:
        if case['id']=='late-budget-rollback':
            assert data['time']==3 and data['state']==Z and data['substeps']>0
        if case['id']=='schedule-budget-rollback':
            assert data['points'][-1]['time']==0 and data['points'][-1]['state']==Z
        return 0
    assert data['model']==MODEL
    if case['kind']=='direct':assert data['time']==case['time']
    else:assert data['points'][-1]['time']==case['time']
    assert data['parameters']==list(map(float,case['args'][1].split(',')))
    if case['kind']=='direct':
        assert data['temporal_error_norm']<=1
        assert data['initial']==list(map(float,case['args'][2].split(',')))
        return norm_error(data['state'],case['expected'],case['tolerance'])
    refs=case['references'];matched=set();error=0
    assert data['initial']==case['specification']['initial']
    for point in data['points']:
        ref=next(r for r in refs if abs(r['time']-point['time'])<1e-12)
        matched.add(ref['time'])
        assert point['temporal_error_norm']<=1 and point['nonlinear_residual_norm']<=1e-10
        assert point['observables']==point['state']
        error=max(error,norm_error(point['state'],ref['state'],case['tolerance']))
        norm_error(point['strain'],ref['strain'],case['strain_tolerance'])
    assert matched=={r['time'] for r in refs}
    return error

def execute_native(solver,cases):
    rows=[]
    for case in cases:
        calls=[]
        for repeat in range(2):
            r=subprocess.run([str(solver),*case['argv']],capture_output=True,text=True,timeout=60)
            calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        rows.append(dict(id=case['id'],calls=calls))
    return rows

def assess_rows(cases,rows):
    assert [c['id'] for c in cases]==[r['id'] for r in rows]
    errors={}
    for case,row in zip(cases,rows):
        assert len(row['calls'])==2
        parsed=[]
        for call in row['calls']:
            assert call['returncode']==(0 if case['ok'] else 1)
            data=json.loads(call['stdout']);errors[case['id']]=assess(case,data);parsed.append(data)
        assert parsed[0]==parsed[1],case['id']+' replay'
    assert errors['refine-fine']<errors['refine-coarse']
    return errors

class MaxwellReferences(unittest.TestCase):
    def test_model_identity_and_references(self):
        m=load(ROOT/'models/research/maxwell'/f'{MODEL}.json')
        self.assertEqual(m,load(ROOT/'docs/ingestion/maxwell-itasca900/candidate-v03.json'))
        self.assertEqual(m['formulation']['stress']['scope'],'total')
        for c in make_cases():
            if c['ok'] and c['kind']=='direct':self.assertTrue(all(math.isfinite(v) for v in c['expected']))
    def test_assessor_rejects_wrong_stress_nonfinite_and_missing_component(self):
        c=make_cases()[0];good={'ok':True,'model':MODEL,'time':c['time'],'state':c['expected'],'initial':Z,'parameters':list(map(float,c['args'][1].split(','))),'temporal_error_norm':0}
        assess(c,good)
        for state in ([x+100 for x in c['expected']],[math.nan]*6,c['expected'][:5]):
            bad=copy.deepcopy(good);bad['state']=state
            with self.assertRaises(AssertionError):assess(c,bad)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--solver',type=Path);ap.add_argument('--output',type=Path);ap.add_argument('--assess',type=Path);a=ap.parse_args()
    if a.freeze:
        p=BASE/'reference-cases.json'
        with p.open('x') as f:json.dump({'cases':make_cases(),'policy':{'direct_absolute_Pa':.05,'schedule_absolute_Pa':15,'strain_absolute':2e-7,'parity_stress_Pa':1e-6,'parity_strain':1e-11,'no_gate_relaxation':True}},f,indent=2);f.write('\n')
        print(p)
    elif a.solver:
        cases=json.loads((BASE/'reference-cases.json').read_text())['cases'];rows=execute_native(a.solver,cases)
        a.output.write_text(json.dumps(rows,indent=2)+'\n');errors=assess_rows(cases,rows);print(json.dumps(errors,indent=2))
    elif a.assess:
        cases=json.loads((BASE/'reference-cases.json').read_text())['cases'];print(json.dumps(assess_rows(cases,json.loads(a.assess.read_text())),indent=2))
    else:unittest.main(argv=[sys.argv[0]])
