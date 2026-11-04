#!/usr/bin/env python3
"""Prospective scalar-source oracle and frozen native/Wasm qualification requests."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ID = 'ramberg-osgood-ansys242'
PACKET = ROOT/'docs/ingestion'/ID
MODEL = ROOT/'models'/f'{ID}.json'
SETTINGS = [2e-10,1e-6,45,14,20000,11]

def stress_oracle(e, p):
    """Source scalar inverse with elastic upper bracket and 160 bisections."""
    E,nu,s0,a,n = (p[k] for k in ('E','nu','sigma0','alpha','n'))
    v=sum(e[:3]); dev=[e[i]-(v/3 if i<3 else 0) for i in range(6)]
    r=math.sqrt(2/3*sum(x*x for x in dev))
    if r==0: return [E*v/(3*(1-2*nu)) if i<3 else 0 for i in range(6)]
    lo,hi=0.0,3*E*r/(2*(1+nu))
    for _ in range(160):
        q=(lo+hi)/2
        if 2*(1+nu)/3*q+a*(q/s0)**(n-1)*q < E*r: lo=q
        else: hi=q
    q=(lo+hi)/2
    return [2*q/(3*r)*dev[i]+(E*v/(3*(1-2*nu)) if i<3 else 0) for i in range(6)]

def strain_from_stress(sigma,p):
    # Used only to prepare source-consistent nonzero parents.
    m=sum(sigma[:3])/3; s=[sigma[i]-(m if i<3 else 0) for i in range(6)]
    q=math.sqrt(1.5*sum(x*x for x in s))
    f=(1+p['nu']+1.5*p['alpha']*(q/p['sigma0'])**(p['n']-1))/p['E']
    return [f*s[i]+((1-2*p['nu'])*m/p['E'] if i<3 else 0) for i in range(6)]

def rotate(a):
    # Passive fixed Cartesian re-expression by orthogonal 45-degree z rotation.
    t=math.sqrt(0.5);Q=[[t,-t,0],[t,t,0],[0,0,1]];rt=math.sqrt(2)
    A=[[a[0],a[3]/rt,a[5]/rt],[a[3]/rt,a[1],a[4]/rt],[a[5]/rt,a[4]/rt,a[2]]]
    B=[[sum(Q[i][k]*A[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return [B[0][0],B[1][1],B[2][2],rt*B[0][1],rt*B[1][2],rt*B[0][2]]

def make_requests():
    model=json.loads(MODEL.read_text());p={k:v['default'] for k,v in model['parameters'].items()};cases=[]
    def add(name,params,endpoints,initial=None,**extra):
        z=initial or [0.0]*12;last=z[6:];increments=[]
        for e in endpoints: increments.append([e[i]-last[i] for i in range(6)]);last=e
        cases.append(dict(id=name,parameters=params,initial=z,increments=increments,expected_states=[stress_oracle(e,params)+e for e in endpoints],settings=SETTINGS,expect_ok=True,**extra))
    sets=[('default',p),('n1.5',dict(p,n=1.5)),('n2.5',dict(p,n=2.5)),('n8',dict(p,n=8)),('nu-negative',dict(p,nu=-.2)),('nu-near-incompressible',dict(p,nu=.45)),('vendor',dict(E=390900e6,nu=.3,sigma0=50e6,alpha=.5,n=5))]
    for tag,q in sets:
        h=q['sigma0']/q['E'];mixed=[1.4*h,-.5*h,.2*h,.3*h,-.4*h,.6*h]
        add(tag+'-zero',q,[[0.0]*6])
        add(tag+'-hydro',q,[[h,h,h,0,0,0],[-h,-h,-h,0,0,0]])
        uni=strain_from_stress([q['sigma0'],0,0,0,0,0],q)
        add(tag+'-uniaxial',q,[uni,[0.0]*6,[-v for v in uni],[0.0]*6])
        for i in (3,4,5):
            a=[0.0]*6;a[i]=h;add(tag+f'-shear{i}',q,[a,[-v for v in a]])
        add(tag+'-mixed-hold-reverse',q,[mixed,mixed,[0.0]*6,[-v for v in mixed],[0.0]*6])
        add(tag+'-rotated',q,[rotate(mixed)])
        zsigma=[q['sigma0'],q['sigma0'],q['sigma0'],0,0,0];ze=strain_from_stress(zsigma,q)
        add(tag+'-nonzero-parent',q,[mixed],initial=zsigma+ze)
        add(tag+'-refinement16',q,[[v*j/16 for v in mixed] for j in range(1,17)])
    mixed=[.004,-.002,.001,.0008,-.0003,.0004]
    add('unit-scale-base',p,[mixed]);add('unit-scale-1000',dict(p,E=p['E']*1000,sigma0=p['sigma0']*1000),[mixed])
    for name,q in [('alpha0',dict(p,alpha=0)),('n1',dict(p,n=1)),('nu-half',dict(p,nu=.5)),('negative-E',dict(p,E=-1))]:
        cases.append(dict(id='reject-'+name,parameters=q,initial=[0.0]*12,increments=[[.001,0,0,0,0,0]],settings=SETTINGS,expect_ok=False,require_rollback=False))
    for name,z in [('inconsistent',[p['sigma0']]*3+[0]*9),('omitted',[])]:
        cases.append(dict(id='reject-'+name,parameters=p,initial=z,increments=[[0.0]*6],settings=SETTINGS,expect_ok=False,require_rollback=name=='inconsistent'))
    cases.append(dict(id='reject-budget',parameters=p,initial=[0.0]*12,increments=[[.02,-.01,-.01,.005,0,0]],settings=[2e-10,1e-6,1,0,1,0],expect_ok=False,require_rollback=True))
    cases.append(dict(id='reject-nonfinite-loading',parameters=p,initial=[0.0]*12,increments=[[0.0]*6],strain_csv_override='nan,0,0,0,0,0',settings=SETTINGS,expect_ok=False,require_rollback=False))
    add('recovery-after-rejections',p,[[.001,0,0,0,0,0]])
    for name,e in [('origin',[0.0]*6),('mixed',mixed)]:
        add('tangent-'+name,p,[e],mode='linearize',tangent_kind=name)
    return dict(identity='ramberg-osgood-requests-v1',model_id=ID,model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256((PACKET/'PLAN.md').read_bytes()).hexdigest(),parameter_order=list(p),cases=cases)

def csv(a): return ','.join(format(v,'.17g') for v in a)

def execute_native(requests,solver):
    out=[]
    for c in requests['cases']:
        state=c['initial'];responses=[]
        for d in c['increments']:
            args=[str(solver),'--model',ID,'--mode',c.get('mode','integrate'),'--parameters',csv([c['parameters'][k] for k in requests['parameter_order']]),'--initial',csv(state),'--strain',c.get('strain_csv_override',csv(d)),'--integration-settings',csv(c['settings'])]
            proc=subprocess.run(args,text=True,capture_output=True,check=False)
            try:r=json.loads(proc.stdout)
            except ValueError:r={'ok':False,'message':'non-JSON response','stdout':proc.stdout,'stderr':proc.stderr,'exit_code':proc.returncode}
            responses.append(r)
            if r.get('ok'):state=r['state']
        out.append({'id':c['id'],'responses':responses})
    return dict(identity='ramberg-osgood-responses-v1',model_sha256=requests['model_sha256'],cases=out)

def check_responses(requests,responses):
    checks=[];byid={c['id']:c for c in responses['cases']}
    def check(name,ok,**details):checks.append(dict(name=name,passed=bool(ok),**details))
    check('response-model-identity',responses['model_sha256']==requests['model_sha256'])
    for c in requests['cases']:
        rs=byid.get(c['id'],{}).get('responses',[]);check(c['id']+'-count',len(rs)==len(c['increments']))
        parent=c['initial']
        for j,r in enumerate(rs):
            key=f"{c['id']}:{j}";check(key+'-status',r.get('ok')==c['expect_ok'],message=r.get('message'))
            if not c['expect_ok']:
                if c.get('require_rollback'):check(key+'-rollback',r.get('state')==parent)
                continue
            if not r.get('ok'):continue
            expected=c['expected_states'][j];state=r.get('state',[])
            finite=len(state)==12 and all(math.isfinite(x) for x in state);check(key+'-finite-layout',finite)
            if not finite:continue
            se=max(abs(a-b) for a,b in zip(state[:6],expected[:6]));ee=max(abs(a-b) for a,b in zip(state[6:],expected[6:]));p=c['parameters']
            check(key+'-stress-oracle',se<=2e-5*p['sigma0'],error_Pa=se,tolerance_Pa=2e-5*p['sigma0'])
            check(key+'-strain',ee<=2e-8*p['sigma0']/p['E'],error=ee)
            parent=state
            if c.get('mode')=='linearize':
                T=r.get('state_tangent');check(key+'-tangent-available',r.get('tangent_ok') and isinstance(T,list) and len(T)==12)
                if not isinstance(T,list) or len(T)!=12:continue
                e=expected[6:];h=1e-8*p['sigma0']/p['E'];errs=[]
                for k in range(6):
                    if c['tangent_kind']=='origin':
                        G=p['E']/(2*(1+p['nu']));lam=p['E']*p['nu']/((1+p['nu'])*(1-2*p['nu']));col=[(lam+(2*G if i==k else 0)) if i<3 and k<3 else (2*G if i==k else 0) for i in range(6)]
                    else:
                        ep=e.copy();em=e.copy();ep[k]+=h;em[k]-=h;sp=stress_oracle(ep,p);sm=stress_oracle(em,p);col=[(a-b)/(2*h) for a,b in zip(sp,sm)]
                    for i in range(6):errs.append(abs(T[i][k]-col[i])/max(1,p['E'],abs(col[i])))
                tolerance=1e-8 if c['tangent_kind']=='origin' else 2e-5
                check(key+'-independent-tangent',max(errs)<=tolerance,error=max(errs),tolerance=tolerance)
    # Compare paths directly as well as against the independent oracle.
    for tag in ['default','n1.5','n2.5','n8','nu-negative','nu-near-incompressible','vendor']:
        a=byid[tag+'-mixed-hold-reverse']['responses'][0];b=byid[tag+'-refinement16']['responses'][-1]
        if a.get('ok') and b.get('ok'):
            p=next(c['parameters'] for c in requests['cases'] if c['id']==tag+'-zero')
            err=max(abs(x-y) for x,y in zip(a['state'][:6],b['state'][:6]));check(tag+'-refinement',err<=4e-5*p['sigma0'],error_Pa=err)
        else:check(tag+'-refinement',False)
    for tag in ['default','n1.5','n2.5','n8','nu-negative','nu-near-incompressible','vendor']:
        a=byid[tag+'-mixed-hold-reverse']['responses'][0];b=byid[tag+'-rotated']['responses'][0]
        if a.get('ok') and b.get('ok'):
            expected=rotate(a['state'][:6]);scale=max(1,max(abs(x) for x in expected));error=max(abs(x-y) for x,y in zip(expected,b['state'][:6]));check(tag+'-fixed-basis-covariance',error<=2e-5*scale,error_Pa=error)
        else:check(tag+'-fixed-basis-covariance',False)
    a=byid['unit-scale-base']['responses'][0];b=byid['unit-scale-1000']['responses'][0]
    if a.get('ok') and b.get('ok'):
        error=max(abs(x-y/1000) for x,y in zip(a['state'][:6],b['state'][:6]));check('positive-unit-scaling',error<=2e-5*100000,error_Pa=error)
    else:check('positive-unit-scaling',False)
    return dict(identity='ramberg-osgood-qualification-v1',model_sha256=requests['model_sha256'],policy_sha256=requests['policy_sha256'],passed=all(c['passed'] for c in checks),checks=checks)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--solver');ap.add_argument('--responses');ap.add_argument('--requests',default=str(PACKET/'execution-v1/requests.json'));ap.add_argument('--output',default=str(PACKET/'execution-v1/results.json'));ap.add_argument('--save-responses');args=ap.parse_args()
    request_path=Path(args.requests)
    if args.prepare:
        request_path.parent.mkdir(parents=True,exist_ok=True);requests=make_requests();request_path.write_text(json.dumps(requests,indent=2,allow_nan=False)+'\n');print(f"Frozen {len(requests['cases'])} cases at {request_path}");return
    requests=json.loads(request_path.read_text());assert requests['model_sha256']==hashlib.sha256(MODEL.read_bytes()).hexdigest(),'model changed since request freeze'
    if args.solver:responses=execute_native(requests,args.solver)
    elif args.responses:responses=json.loads(Path(args.responses).read_text())
    else:ap.error('--prepare, --solver or --responses required')
    if args.save_responses:Path(args.save_responses).write_text(json.dumps(responses,indent=2)+'\n')
    result=check_responses(requests,responses);Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(result['checks']),'failed':[c for c in result['checks'] if not c['passed']]}));raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__':main()
