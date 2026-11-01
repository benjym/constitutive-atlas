"""Prospective source-independent Kelvin study; parent owns compiled execution."""
import argparse, copy, hashlib, json, math, subprocess
from pathlib import Path
from reference import source_stress,constant_rate,deviatoric_stress_ramp,cart,mandel
B=Path(__file__).resolve().parent
M='kelvin-voigt-comsol63-deviatoric-zero-spin-ode'; P=[20e6,12e6,2.]; Z=[0.]*6
E=[.002,.001,-.001,.0005,-.0004,.0003]; D=[.001,-.0002,.0003,.0007,-.0006,.0005]
D0=[.001,-.0005,-.0005,.0004,-.0002,.0003]
SHA='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
def csv(v):return ','.join(format(x,'.17g') for x in v)
def stress(e,d,p=P):return source_stress(e,d,*p)
def dump(path,data):
    assert not path.exists(),f'Refuse to overwrite retained file {path}'
    path.write_text(json.dumps(data,indent=2)+'\n')
def direct(name,e=E,d=D,p=P,t=1.,**options):
    controls=dict(rtol=1e-8,atol=1e-11,minimum=1e-12,maximum=1e6,budget=100000);controls.update(options)
    args=[M,csv(p),csv(e),csv(d),3.,t,*controls.values()]
    argv=['--mode','integrate-time','--model',M,'--parameters',csv(p),'--initial',csv(e),'--strain-rate',csv(d),'--start-time','3','--duration',str(t)]
    for flag,value in zip(['--rtol','--atol','--min-time-step','--max-time-step','--max-substeps'],controls.values()):argv +=[flag,str(value)]
    end=constant_rate(e,d,t)
    return dict(id=name,kind='direct',ok=True,call='atlas_integrate_time',types=['string']*4+['number']*7,args=args,argv=argv,expected=end,expected_stress=stress(end,d,p),parameters=p,rate=d,time=3+t)
def observe(name,e=E,d=D,p=P):
    return dict(id=name,kind='observe',ok=True,call='atlas_observe_time',types=['string']*4+['number'],args=[M,csv(p),csv(e),csv(d),3.],argv=['--mode','observe-time','--model',M,'--parameters',csv(p),'--initial',csv(e),'--strain-rate',csv(d),'--start-time','3'],expected_stress=stress(e,d,p))
def hold(q='strain'):return dict(quantity=q,kind='hold')
def rate(v,q='strain'):return dict(quantity=q,kind='rate',value=v)
def seg(name,t,controls,samples=4):return dict(id=name,duration=t,samples=samples,controls=controls)
def schedule(name,e=Z,d=Z,p=P,start=0.):
    return dict(schema_version='0.2',units='SI',model=M,parameters=p,initial=e,initial_strain=e,initial_strain_rate=d,start_time=start,segments=[],solver=dict(method='backward-euler-step-doubling',relative_tolerance=1e-8,absolute_scale_fraction=1e-11,maximum_substeps=100000))
def schedule_case(name,s,paths):
    a=s['solver'];wire=[]
    for g in s['segments']:
        wire +=[g['duration'],g['samples']]
        for c in g['controls']:wire +=[int(c['quantity']=='stress'),{'hold':0,'rate':1,'target':2}[c['kind']],c.get('value',0)]
    args=[M,csv(s['parameters']),csv(s['initial']),csv(s['initial_strain']),csv(s['initial_strain_rate']),csv(wire),','.join(x['id'] for x in s['segments']),s['start_time'],a['relative_tolerance'],a['absolute_scale_fraction'],1e-12,1e6,a['maximum_substeps'],1e-10,40]
    argv=['--mode','schedule','--model',M]
    for flag,value in zip(['--parameters','--initial','--initial-strain','--initial-strain-rate','--segments','--segment-ids','--start-time','--rtol','--atol','--min-time-step','--max-time-step','--max-substeps','--nonlinear-tolerance','--max-iterations'],args[1:]):argv +=[flag,str(value)]
    refs=[dict(time=s['start_time'],segment=-1,side='left',state=s['initial'],stress=stress(s['initial'],s['initial_strain_rate'],s['parameters']))]
    start=s['start_time']
    for n,(g,path) in enumerate(zip(s['segments'],paths)):
        for j in range(g['samples']+1):
            t=g['duration']*j/g['samples'];e,v=path(t)
            refs.append(dict(time=start+t,segment=n,side='right' if j==0 else 'left',state=e,stress=stress(e,v,s['parameters'])))
        start +=g['duration']
    return dict(id=name,kind='schedule',ok=True,specification=s,call='atlas_run_schedule',types=['string']*7+['number']*8,args=args,argv=argv,references=refs)
def rotate(v):
    a=.41;b=-.29;c=math.cos(a);s=math.sin(a);u=math.cos(b);w=math.sin(b)
    q=[[c,-s*u,s*w],[s,c*u,-c*w],[0,w,u]];x=cart(v)
    return mandel([[sum(q[i][k]*x[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)]for i in range(3)])
def make_cases():
    rows=[]
    for tau in [.2,2.,20.]:
        for ratio in [.01,.5,4.]:rows.append(direct(f'tensor-tau{tau}-ratio{ratio}',p=P[:2]+[tau],t=tau*ratio))
    rows +=[direct('hydro',e=[.001]*3+[0.]*3,d=[.0003]*3+[0.]*3,t=4.),direct('shear',e=Z,d=[0.]*3+[.001,-.0004,.0003],t=4.),direct('elastic-hold',d=Z,t=8.),direct('zero-hold',e=Z,d=Z,t=8.)]
    for tau in [.2,2.,20.]:
        p=P[:2]+[tau];s=schedule('creep',d=D0,p=p);s['segments']=[seg('creep',4*tau,[hold('stress')]*6,8)]
        si=stress(Z,D0,p);path=lambda t,p=p,si=si:deviatoric_stress_ramp(Z,si,Z,t,p[1],p[2])
        rows.append(schedule_case('creep-preset' if tau==2 else f'creep-tau{tau}',s,[path]))
    s=schedule('history',e=E);reverse=[-x for x in D];e1=constant_rate(E,D,1)
    s['segments']=[seg('load',1,list(map(rate,D))),seg('hold',1,[hold()]*6),seg('reverse',1,list(map(rate,reverse)))]
    rows.append(schedule_case('load-hold-reverse',s,[lambda t:(constant_rate(E,D,t),D),lambda t:(e1,Z),lambda t:(constant_rate(e1,reverse,t),reverse)]))
    er=[.0001,-.00005,-.00005,.0003,-.0002,.0001];si=[15000.,-7500.,-7500.,2000.,-5000.,3000.];A=[1200.,-600.,-600.,800.,-700.,500.]
    _,v0=deviatoric_stress_ramp(er,si,A,0,P[1],P[2]);s=schedule('ramp',er,v0);s['segments']=[seg('ramp',4,[rate(x,'stress') for x in A])]
    rows.append(schedule_case('stress-ramp',s,[lambda t:deviatoric_stress_ramp(er,si,A,t,P[1],P[2])]))
    for tag,rtol,atol in [('coarse',1e-4,1e-7),('fine',1e-8,1e-11)]:
        s=schedule(tag,d=D0);s['solver'].update(relative_tolerance=rtol,absolute_scale_fraction=atol);s['segments']=[seg('creep',4,[hold('stress')]*6)]
        rows.append(schedule_case('refine-'+tag,s,[lambda t:deviatoric_stress_ramp(Z,stress(Z,D0),Z,t,P[1],P[2])]))
    restart=direct('actual-endpoint-restart',e=constant_rate(E,D,1),d=D,t=2);restart['restart_from']='tensor-tau2.0-ratio0.5';restart['time']=6.;restart['args'][4]=4.;restart['argv'][restart['argv'].index('--start-time')+1]='4';rows.append(restart)
    direction=[.4,-.3,.2,.5,-.6,.7];h=1e-6
    rows.append(observe('partial-base'))
    for key in ['state','rate']:
        for sign in [-1,1]:
            z=[x+sign*h*v for x,v in zip(E if key=='state' else D,direction)]
            rows.append(observe(f'partial-{key}-{sign}',e=z if key=='state' else E,d=z if key=='rate' else D))
    rows.append(observe('covariance-rotated',e=rotate(E),d=rotate(D)))
    # All failures are immediately followed by a successful fresh request.
    bad=direct('late-budget-rollback',t=4.,maximum=.25,budget=2);bad.update(ok=False,late=True,expected=E,time=3.);rows.append(bad)
    s=schedule('prefix',e=E);s['solver']['maximum_substeps']=2;s['segments']=[seg('valid-prefix',1,list(map(rate,D)),1),seg('fail-budget',8,[hold('stress')]*6,1)]
    bad=schedule_case('late-budget-prefix',s,[lambda t:(constant_rate(E,D,t),D),lambda t:(e1,D)]);bad.update(ok=False,prefix=e1);rows.append(bad)
    for label,opt,index,value in [('zero-duration','--duration',5,0.),('negative-duration','--duration',5,-1.),('negative-G','--parameters',1,csv([P[0],-P[1],P[2]])),('zero-tau','--parameters',1,csv(P[:2]+[0.])),('missing-state','--initial',2,''),('short-rate','--strain-rate',3,csv(D[:5]))]:
        bad=direct(label);bad['args'][index]=value;bad['argv'][bad['argv'].index(opt)+1]=str(value);bad.update(ok=False);rows.append(bad)
    for bad in [x for x in rows if not x['ok']]:rows.insert(rows.index(bad)+1,direct('recover-'+bad['id'],e=E,d=Z,t=.2))
    return rows

def err(a,b):
    assert len(a)==len(b) and all(type(x)in(int,float) and math.isfinite(x)for x in a)
    return max(abs(x-y) for x,y in zip(a,b))
def result(row):return json.loads(row['calls'][0]['stdout'])
def assess(cases,rows):
    assert [x['id']for x in cases]==[x['id']for x in rows]
    errors={}
    for c,r in zip(cases,rows):
        assert len(r['calls'])==2 and r['calls'][0]['stdout']==r['calls'][1]['stdout'],c['id']
        d=result(r);assert d['ok']==c['ok'],(c['id'],d)
        if not c['ok']:
            if c.get('late'):assert d['state']==E and d['time']==3 and d['substeps']>0,(c['id'],d)
            if c.get('prefix'):
                assert len(d['points'])>=3 and any(x['time']==1 and x['segment']==0 for x in d['points']),d
                assert all(x['time']<=1 for x in d['points']),d
                assert err(d['points'][-1]['state'],c['prefix'])<=3e-8,d
            continue
        if c['kind']=='observe':
            se=err(d['values'],c['expected_stress']);assert se<=1e-7,(c['id'],se);errors[c['id']]={'stress':se}
        elif c['kind']=='direct':
            ee=err(d['state'],c['expected']);assert ee<=3e-8,(c['id'],ee)
            assert abs(d['time']-c['time'])<=1e-12*max(1,abs(c['time']))
            obs=json.loads(r['observation']);assert obs['ok'];se=err(obs['values'],c['expected_stress']);assert se<=1e-7,(c['id'],se)
            errors[c['id']]=dict(strain=ee,stress=se)
        else:
            refs=c['references'];assert len(d['points'])==len(refs),(c['id'],len(d['points']),len(refs));ee=se=0.
            tol=3e-6 if c['id']=='refine-coarse' else 3e-8
            for pt,ref in zip(d['points'],refs):
                assert (pt['segment'],pt['side'])==(ref['segment'],ref['side'])
                assert abs(pt['time']-ref['time'])<=1e-12*max(1,abs(ref['time']))
                ee=max(ee,err(pt['state'],ref['state']),err(pt['strain'],ref['state']));se=max(se,err(pt['observables'],ref['stress']))
            assert ee<=tol and se<=1,(c['id'],ee,se,tol);errors[c['id']]=dict(strain=ee,stress=se)
    assert errors['refine-fine']['strain']<errors['refine-coarse']['strain']
    by={x['id']:result(x) for x in rows};direction=[.4,-.3,.2,.5,-.6,.7];partials={}
    for key in ['state','rate']:
        actual=[(a-b)/2e-6 for a,b in zip(by[f'partial-{key}-1']['values'],by[f'partial-{key}--1']['values'])]
        expected=stress(direction,Z) if key=='state' else stress(Z,direction)
        relative=err(actual,expected)/max(abs(x)for x in expected);assert relative<=1e-9,(key,relative);partials[key]=relative
    covariance=err(by['covariance-rotated']['values'],rotate(by['partial-base']['values']));assert covariance<=1e-7
    return dict(passed=True,cases=len(cases),calls=len(cases)*2,negative_recovery_pairs=sum(not c['ok']for c in cases),errors=errors,directional_partial_relative_errors=partials,passive_basis_covariance_error_Pa=covariance)
def verify_freeze():
    f=json.loads((B/'freeze.json').read_text())
    for name,h in f['pins'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==h,name

def collect_native(solver,cases,out):
    rows=[]
    for source in cases:
        c=copy.deepcopy(source)
        if c.get('restart_from'):
            state=result(next(x for x in rows if x['id']==c['restart_from']))['state'];c['args'][2]=csv(state);c['argv'][c['argv'].index('--initial')+1]=csv(state)
        calls=[]
        for _ in range(2):
            r=subprocess.run([str(solver),*c['argv']],capture_output=True,text=True,timeout=240);calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        row=dict(id=c['id'],calls=calls)
        if c['ok'] and c['kind']=='direct' and result(row)['ok']:
            r=subprocess.run([str(solver),'--mode','observe-time','--model',M,'--parameters',csv(c['parameters']),'--initial',csv(result(row)['state']),'--strain-rate',csv(c['rate']),'--start-time',str(c['time'])],capture_output=True,text=True,timeout=30);row['observation']=r.stdout
        rows.append(row);out.write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','native','assess','parity']);p.add_argument('--solver',type=Path);p.add_argument('--backend',default='native');a=p.parse_args()
    if a.mode=='prepare':
        assert not(B/'freeze.json').exists(),'Already frozen'
        assert hashlib.sha256((B.parent/'source-v1/candidate.json').read_bytes()).hexdigest()==SHA
        cases=make_cases();dump(B/'cases.json',dict(cases=cases))
        names=['study.py','reference.py','PLAN.md','cases.json','collect_wasm.mjs']
        dump(B/'freeze.json',dict(identity='NUM-kelvin-voigt-comsol63-v1',model=M,model_sha256=SHA,observations_at_freeze='none; parent must separately freeze committed runtime closure and toolchain',pins={n:hashlib.sha256((B/n).read_bytes()).hexdigest()for n in names}));print('Frozen',len(cases),'cases')
    else:
        verify_freeze();cases=json.loads((B/'cases.json').read_text())['cases']
        if a.mode=='parity':
            native=json.loads((B/'native-raw.json').read_text());wasm=json.loads((B/'wasm-raw.json').read_text());maximum=0.
            for c,n,w in zip(cases,native,wasm):
                dn,dw=result(n),result(w);assert dn['ok']==dw['ok']
                if not c['ok']:continue
                pairs=[(dn['values'],dw['values'])]if c['kind']=='observe' else [(dn['state'],dw['state'])]if c['kind']=='direct' else [(p['state'],q['state'])for p,q in zip(dn['points'],dw['points'])]
                for x,y in pairs:maximum=max(maximum,err(x,y));assert err(x,y)<=1e-7 if c['kind']=='observe' else err(x,y)<=3e-8
                if c['kind']=='schedule':
                    assert len(dn['points'])==len(dw['points'])
                    for x,y in zip(dn['points'],dw['points']):assert err(x['observables'],y['observables'])<=1
                elif c['kind']=='direct':assert err(json.loads(n['observation'])['values'],json.loads(w['observation'])['values'])<=1
            report=dict(passed=True,cases=len(cases),maximum_primary_value_difference=maximum);dump(B/'parity-report.json',report)
        else:
            raw=B/(a.backend+'-raw.json')
            if a.mode=='native':
                assert not raw.exists(),'Refuse to overwrite raw observations';rows=collect_native(a.solver,cases,raw)
            else:rows=json.loads(raw.read_text())
            report=assess(cases,rows);dump(B/(a.backend+'-report.json'),report)
        print(json.dumps(report,indent=2))
if __name__=='__main__':main()
