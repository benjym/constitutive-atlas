"""Prospective SLS reference generation, serial native collection and saved assessment."""
import argparse,copy,hashlib,json,math,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
BASE=Path(__file__).resolve().parent
MODEL='sls-comsol63-deviatoric-zero-spin-ode'
P=[20e6,8e6,12e6,2.]
ZERO=[0.]*6
E=[.002,.001,-.001,.0005,-.0004,.0003]
Q=[5000.,-2000.,-3000.,1000.,-500.,250.]
Z=E+Q
D=[.001,-.0002,.0003,.0007,-.0006,.0005]
def csv(v):return ','.join(format(x,'.17g')for x in v)
def dev(v):
    mean=sum(v[:3])/3
    return [x-(mean if i<3 else 0)for i,x in enumerate(v)]
def exact(z,d,p,t):
    K,g,h,tau=p;decay=math.exp(-t/tau);gain=-2*h*tau*math.expm1(-t/tau)
    return [a+b*t for a,b in zip(z[:6],d)]+[a*decay+gain*b for a,b in zip(z[6:],dev(d))]
def stress(z,p):
    K,g,h,tau=p;mean=K*sum(z[:3]);de=dev(z[:6])
    return [(mean if i<3 else 0)+2*g*de[i]+z[6+i]for i in range(6)]
def creep(z,p,t):
    K,g,h,tau=p;s=stress(z,p);sd=dev(s);ed=dev(z[:6]);decay=math.exp(-g*t/(tau*(g+h)));mean=sum(z[:3])/3
    e=[(mean if i<3 else 0)+sd[i]/(2*g)+(ed[i]-sd[i]/(2*g))*decay for i in range(6)]
    q=[sd[i]-2*g*dev(e)[i]for i in range(6)]
    return e+q

def direct(name,z=Z,p=P,d=D,t=1.,**opts):
    settings=dict(rtol=1e-9,atol=1e-12,minimum=1e-12,maximum=1e6,budget=100000);settings.update(opts)
    args=[MODEL,csv(p),csv(z),csv(d),3.,t,*settings.values()]
    argv=['--mode','integrate-time','--model',MODEL,'--parameters',csv(p),'--initial',csv(z),'--strain-rate',csv(d),'--start-time','3','--duration',str(t)]
    for key,value in zip(['--rtol','--atol','--min-time-step','--max-time-step','--max-substeps'],settings.values()):argv +=[key,str(value)]
    end=exact(z,d,p,t)
    return dict(id=name,kind='direct',ok=True,argv=argv,call='atlas_integrate_time',types=['string']*4+['number']*7,args=args,expected=end,expected_stress=stress(end,p),parameters=p,rate=d,time=3+t)

def schedule(name,z=Z,p=P):
    return dict(schema_version='0.2',units='SI',model=MODEL,parameters=p,initial=z,initial_strain=z[:6],initial_strain_rate=ZERO,start_time=0.,segments=[],solver=dict(method='backward-euler-step-doubling',relative_tolerance=1e-8,absolute_scale_fraction=1e-11,maximum_substeps=100000))
def hold(q='strain'):return dict(quantity=q,kind='hold')
def rate(v):return dict(quantity='strain',kind='rate',value=v)
def segment(name,t,controls,samples=4):return dict(id=name,duration=t,samples=samples,controls=controls)
def schedcase(name,s,ref):
    from atlas.schedule import schedule_command
    argv=schedule_command(s,'SOLVER')[1:];wire=dict(zip(argv[::2],argv[1::2]));a=s['solver']
    args=[MODEL,csv(s['parameters']),csv(s['initial']),csv(s['initial_strain']),csv(s['initial_strain_rate']),wire['--segments'],wire['--segment-ids'],s['start_time'],a['relative_tolerance'],a['absolute_scale_fraction'],1e-12,1e6,a['maximum_substeps'],1e-10,40]
    times=[s['start_time']];t=s['start_time']
    for seg in s['segments']:
        times.extend(t+seg['duration']*i/seg['samples']for i in range(1,seg['samples']+1));t+=seg['duration']
    return dict(id=name,kind='schedule',ok=True,specification=s,argv=argv,call='atlas_run_schedule',types=['string']*7+['number']*8,args=args,references=[dict(time=t,state=ref(t),stress=stress(ref(t),s['parameters']))for t in times])

def make_cases():
    cases=[]
    for tau in [.2,2.,20.]:
        for ratio in [.01,.5,4.]:cases.append(direct(f'tensor-tau{tau}-ratio{ratio}',p=P[:3]+[tau],t=tau*ratio))
    cases +=[direct('hydro',z=[.001]*3+[0.]*9,d=[.0003]*3+[0.]*3,t=4.),direct('shear',z=[0.]*12,d=[0.]*3+[.001,-.0004,.0003],t=4.),direct('relax',d=ZERO,t=8.),direct('zero-hold',z=[0.]*12,d=ZERO,t=8.)]
    s=schedule('relax');s['segments']=[segment('relax',8.,[hold()]*6)];cases.append(schedcase('relax-schedule',s,lambda t:exact(Z,ZERO,P,t)))
    s=schedule('creep');s['segments']=[segment('creep',8.,[hold('stress')]*6)];cases.append(schedcase('creep-schedule',s,lambda t:creep(Z,P,t)))
    s=schedule('history');s['segments']=[segment('load',1.,list(map(rate,D))),segment('hold',1.,[hold()]*6),segment('reverse',1.,list(map(rate,[-v for v in D])))];z1=exact(Z,D,P,1);z2=exact(z1,ZERO,P,1)
    def history(t):
        if t<=1:return exact(Z,D,P,t)
        if t<=2:return exact(z1,ZERO,P,t-1)
        return exact(z2,[-v for v in D],P,t-2)
    cases.append(schedcase('load-hold-reverse',s,history))
    # Explicit restart is initialized with the analytical nonzero-time endpoint.
    zr=exact(Z,ZERO,P,4.);s=schedule('restart',zr);s['start_time']=4.;s['segments']=[segment('continue',4.,[hold()]*6)]
    cases.append(schedcase('analytic-endpoint-restart',s,lambda t:exact(Z,ZERO,P,t)))
    for label,rtol,atol in [('coarse',1e-4,1e-7),('fine',1e-8,1e-11)]:
        s=schedule(label);s['solver'].update(relative_tolerance=rtol,absolute_scale_fraction=atol);s['segments']=[segment('relax',4.,[hold()]*6)];cases.append(schedcase('refine-'+label,s,lambda t:exact(Z,ZERO,P,t)))
    restart=direct('actual-endpoint-restart',z=exact(Z,ZERO,P,8.),d=ZERO,t=2.);restart['args'][4]=11.;restart['argv'][restart['argv'].index('--start-time')+1]='11';restart['time']=13.;restart['restart_from']='relax';cases.append(restart)
    bad=direct('late-budget-rollback',d=ZERO,t=4.,maximum=.25,budget=2);bad.update(ok=False,expected=Z,time=3.,late=True);cases.append(bad)
    for label,opt,index,value in [('zero-duration','--duration',5,0.),('negative-duration','--duration',5,-1.),('negative-G1','--parameters',1,csv([P[0],P[1],-P[2],P[3]])),('zero-tau','--parameters',1,csv(P[:3]+[0.])),('missing-state','--initial',2,''),('nontraceless-q','--initial',2,csv(E+[5000.,-1000.,-3000.,1000.,-500.,250.]))]:
        bad=direct(label);bad.update(ok=False,expected=None);bad['args'][index]=value;bad['argv'][bad['argv'].index(opt)+1]=str(value);cases.append(bad)
    # Every negative call is immediately followed by a fresh valid request.
    for bad in [c for c in cases if not c['ok']]:
        recovery=direct('recover-'+bad['id'],d=ZERO,t=.2);cases.insert(cases.index(bad)+1,recovery)
    return cases

def error(a,b):
    assert len(a)==len(b)
    assert all(type(v)in(int,float)and math.isfinite(v)for v in a)
    return max(abs(x-y)for x,y in zip(a,b))
def checkstate(z,ref,strain_tol,stress_tol):
    ee=error(z[:6],ref[:6]);qe=error(z[6:],ref[6:]);assert ee<=strain_tol,(ee,strain_tol);assert qe<=stress_tol,(qe,stress_tol);return ee,qe

def assess(cases,rows):
    assert [c['id']for c in cases]==[r['id']for r in rows]
    errors={}
    for c,r in zip(cases,rows):
        calls=r['calls'];assert len(calls)==2 and calls[0]['stdout']==calls[1]['stdout'],c['id'];data=json.loads(calls[0]['stdout']);assert data['ok']==c['ok'],(c['id'],data)
        if not c['ok']:
            if c.get('late'):assert data['state']==Z and data['time']==3. and data['substeps']>0,data
            continue
        if c['kind']=='direct':
            ee,qe=checkstate(data['state'],c['expected'],2e-8,1.)
            assert abs(data['time']-c['time'])<=1e-12*max(1,abs(c['time']))
            obs=json.loads(r['observation']);assert obs['ok'];se=error(obs['values'][:6],c['expected_stress']);assert se<=1.,(c['id'],se)
            errors[c['id']]=dict(strain=ee,q=qe,stress=se)
        else:
            assert len(data['points'])==len(c['references']),(c['id'],len(data['points']),len(c['references']))
            ee=qe=se=0.;bound=1000. if c['id']=='refine-coarse' else 15.
            for pt,ref in zip(data['points'],c['references']):
                a,b=checkstate(pt['state'],ref['state'],2e-7,bound);ee=max(ee,a);qe=max(qe,b)
                assert abs(pt['time']-ref['time'])<=1e-12*max(1,abs(ref['time']))
                se=max(se,error(pt['stress'],ref['stress']));assert se<=bound,(c['id'],se)
                assert error(pt['strain'],ref['state'][:6])<=2e-7
            errors[c['id']]=dict(strain=ee,q=qe,stress=se)
    assert errors['refine-fine']['q']<errors['refine-coarse']['q']
    return dict(passed=True,cases=len(cases),calls=2*len(cases),negative_recovery_pairs=sum(not c['ok']for c in cases),errors=errors)

def collect_native(solver,cases,output):
    rows=[]
    for c in cases:
        calls=[]
        if c.get('restart_from'):
            previous=next(row for row in rows if row['id']==c['restart_from']);parent=json.loads(previous['calls'][0]['stdout'])['state'];c=copy.deepcopy(c);c['args'][2]=csv(parent);c['argv'][c['argv'].index('--initial')+1]=csv(parent)
        for _ in range(2):
            r=subprocess.run([str(solver),*c['argv']],capture_output=True,text=True,timeout=120);calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        row=dict(id=c['id'],calls=calls)
        if c['ok']and c['kind']=='direct':
            data=json.loads(calls[0]['stdout'])
            if data['ok']:
                obs=subprocess.run([str(solver),'--mode','observe-time','--model',MODEL,'--parameters',csv(c['parameters']),'--current',csv(data['state']),'--strain-rate',csv(c['rate']),'--start-time',str(c['time'])],capture_output=True,text=True,timeout=30);row['observation']=obs.stdout
        rows.append(row);output.write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','native','assess']);p.add_argument('--solver',type=Path);p.add_argument('--backend',default='native');a=p.parse_args()
    if a.mode=='prepare':
        assert not(BASE/'freeze.json').exists(),'Refuse to overwrite frozen study'
        cases=make_cases();(BASE/'cases.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
        # Pin complete current runtime closure and study inputs before compiled observations.
        paths=[Path(__file__),BASE/'PLAN.md',BASE/'cases.json',BASE/'collect_wasm.mjs',ROOT/'cmake/sls/CMakeLists.txt',ROOT/'models/research/sls'/ (MODEL+'.json'),ROOT/'cpp/main.cpp',*sorted((ROOT/'cpp/include').rglob('*.hpp')),*sorted((ROOT/'atlas').glob('*.py')),*sorted((ROOT/'schemas').glob('*.json'))]
        pins={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in paths}
        (BASE/'freeze.json').write_text(json.dumps(dict(task='NUM-sls-comsol63-v1',pins=pins),indent=2)+'\n');print('Frozen',len(cases),'cases and',len(pins),'source/input identities')
    else:
        cases=json.loads((BASE/'cases.json').read_text())['cases'];path=BASE/(a.backend+'-raw.json')
        if a.mode=='native':
            assert not path.exists(),'Refuse to overwrite retained observations';rows=collect_native(a.solver,cases,path)
        else:rows=json.loads(path.read_text())
        report=assess(cases,rows);(BASE/(a.backend+'-report.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
