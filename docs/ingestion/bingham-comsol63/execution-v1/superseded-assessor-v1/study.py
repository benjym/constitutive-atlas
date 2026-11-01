"""Prospective request generation, raw collection and frozen assessment."""
import argparse,copy,hashlib,json,math,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(BASE))
from oracle import P,Z,D,ZERO,dev,stress,relaxation,creep,stress_space_history,rotate,rotate_state
MODEL='bingham-comsol63-mises-perfect-zero-spin-ode'
SOLVER=dict(method='backward-euler-step-doubling',relative_tolerance=1e-9,absolute_scale_fraction=1e-12,minimum_step=1e-12,maximum_step=1e6,maximum_substeps=1000000,nonlinear_tolerance=1e-10,maximum_iterations=40,maximum_depth=40)
def csv(v):return ','.join(format(x,'.17g') for x in v)
def direct(name,z,d,t,expected,expected_stress,p=P,**options):
    s=dict(rtol=1e-9,atol=1e-12,minimum=1e-12,maximum=1e6,budget=1000000);s.update(options)
    args=[MODEL,csv(p),csv(z),csv(d),3.,t,*s.values()]
    argv=['--mode','integrate-time','--model',MODEL,'--parameters',csv(p),'--initial',csv(z),'--strain-rate',csv(d),'--start-time','3','--duration',str(t)]
    for key,value in zip(['--rtol','--atol','--min-time-step','--max-time-step','--max-substeps'],s.values()):argv +=[key,str(value)]
    return dict(id=name,kind='direct',ok=True,argv=argv,call='atlas_integrate_time',types=['string']*4+['number']*7,args=args,expected=expected,expected_stress=expected_stress,parameters=p,initial=z,rate=d,time=3+t)
def schedcase(name,z,segments,refs,**settings):
    from atlas.schedule import schedule_command
    s=dict(schema_version='0.2',units='SI',model=MODEL,parameters=P,initial=z,initial_strain=z[:6],initial_strain_rate=ZERO,start_time=0.,segments=segments,solver={**{k:v for k,v in SOLVER.items() if k!='maximum_depth'},**settings})
    argv=schedule_command(s,'SOLVER')[1:];wire=dict(zip(argv[::2],argv[1::2]));a=s['solver']
    args=[MODEL,csv(P),csv(z),csv(z[:6]),csv(ZERO),wire['--segments'],wire['--segment-ids'],0.,a['relative_tolerance'],a['absolute_scale_fraction'],a['minimum_step'],a['maximum_step'],a['maximum_substeps'],a['nonlinear_tolerance'],a['maximum_iterations']]
    return dict(id=name,kind='schedule',ok=True,specification=s,argv=argv,call='atlas_run_schedule',types=['string']*7+['number']*8,args=args,references=refs,initial=z)
def seg(name,duration,d=None,mode='strain',samples=4):
    controls=[dict(quantity=mode,kind='hold') for _ in range(6)] if d is None else [dict(quantity='strain',kind='rate',value=x) for x in d]
    return dict(id=name,duration=duration,samples=samples,controls=controls)
def refs_for(fn,duration=2,samples=4):
    return [dict(time=duration*i/samples,state=fn(duration*i/samples),stress=stress(fn(duration*i/samples))) for i in range(samples+1)]
def build():
    source=json.loads((BASE.parent/'source-v1/analytical-references.json').read_text());cases=[]
    for r in source['cases']:
        cases.append(direct('radial-'+r['id'],r['initial'],r['strain_rate'],r['duration'],r['expected'],r['expected_stress']))
    cases +=[direct('hydrostatic',[.001]*3+[0.]*10,[.001]*3+[0.]*3,2.,[.003]*3+[0.]*10,[180000.]*3+[0.]*3),direct('zero-hold',[0.]*13,ZERO,2.,[0.]*13,ZERO)]
    for i,angle in enumerate([.3,.7,1.1]):
        c,s=math.cos(angle),math.sin(angle);R=[[c,-s,0],[s,c,0],[0,0,1]]
        expected=rotate_state(relaxation(Z,2.),R)
        cases.append(direct('fixed-basis-covariance-'+str(i),rotate_state(Z,R),ZERO,2.,expected,rotate(stress(relaxation(Z,2.)),R)))
    for name,fn in [('relaxation',lambda t:relaxation(Z,t)),('creep',lambda t:creep(Z,t))]:
        cases.append(schedcase('public-'+name,Z,[seg(name,2.,mode='stress' if name=='creep' else 'strain')],refs_for(fn)))
    # Independent RK4 references integrate stress and alpha, not production eps_vp.
    histories={'public-rate':[(.5,D)]*4,'noncoaxial-history':[(.5,D),(.5,ZERO),(.5,[0,.002,-.001,-.003,.001,.002]),(.5,[-x for x in D])]}
    convergence=[]
    for name,history in histories.items():
        coarse=stress_space_history(Z,history,steps=4096);fine=stress_space_history(Z,history,steps=8192)
        se=max(abs(a-b) for x,y in zip(coarse,fine) for a,b in zip(x['state'],y['state']));pe=max(abs(a-b) for x,y in zip(coarse,fine) for a,b in zip(x['stress'],y['stress']))
        assert se<1e-9 and pe<.02,(name,se,pe);convergence.append(dict(id=name,state_grid_difference=se,stress_grid_difference_Pa=pe))
        refs=[dict(time=0.,state=Z,stress=stress(Z))]+[dict(time=.5*(i+1),**r) for i,r in enumerate(fine)]
        segments=[seg(name,2.,D)] if name=='public-rate' else [seg('stage-'+str(i),t,d,samples=1) for i,(t,d) in enumerate(history)]
        cases.append(schedcase(name,Z,segments,refs))
    # Coarse and fine use an identical exact reference and never change acceptance.
    for name,rtol,atol in [('coarse',1e-4,1e-7),('fine',1e-9,1e-12)]:
        cases.append(schedcase('refinement-'+name,Z,[seg(name,2.)],refs_for(lambda t:relaxation(Z,t)),relative_tolerance=rtol,absolute_scale_fraction=atol))
    restart=direct('actual-state-restart',relaxation(Z,2.),ZERO,1.,relaxation(Z,3.),stress(relaxation(Z,3.)));restart['restart_from']='public-relaxation';restart['args'][4]=2.;restart['argv'][restart['argv'].index('--start-time')+1]='2';restart['time']=3.;cases.append(restart)
    bad=direct('late-budget-rollback',Z,ZERO,2.,Z,stress(Z),maximum=.1,budget=2);bad.update(ok=False,late=True);cases.append(bad)
    for name,opt,arg,value in [('zero-duration','--duration',5,0.),('negative-duration','--duration',5,-1.),('zero-viscosity','--parameters',1,csv(P[:3]+[0.])),('negative-yield','--parameters',1,csv(P[:2]+[-P[2],P[3]])),('missing-state','--initial',2,''),('negative-alpha','--initial',2,csv(Z[:-1]+[-.01])),('plastic-trace','--initial',2,csv(Z[:6]+[.01,0,0,0,0,0,0]))]:
        bad=direct(name,Z,ZERO,.1,None,None);bad.update(ok=False);bad['args'][arg]=value;bad['argv'][bad['argv'].index(opt)+1]=str(value);cases.append(bad)
    # Recovery is tested in the same Wasm instance after every rejected request.
    for bad in [c for c in cases if not c['ok']]:
        cases.insert(cases.index(bad)+1,direct('recovery-'+bad['id'],Z,ZERO,.2,relaxation(Z,.2),stress(relaxation(Z,.2))))
    (BASE/'cases.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n');(BASE/'reference-convergence.json').write_text(json.dumps(dict(passed=True,rows=convergence,compiled_observations=False),indent=2)+'\n')
    return len(cases)
def compare(actual,expected,kind,coarse=False):
    assert len(actual)==len(expected)
    worst=0.
    for x,y in zip(actual,expected):
        assert type(x) in (int,float) and math.isfinite(x)
        # Fixed prospective source-derived accuracy envelope. Coarse refinement is
        # diagnostic only; its quantitative fine-improvement gate is separate.
        floor=(1000 if coarse else 3.) if kind=='stress' else (.001 if coarse else 3e-7)
        bound=max(floor,2e-5*abs(y));err=abs(x-y);assert err<=bound,(kind,err,bound,x,y);worst=max(worst,err)
    return worst
def assess(cases,rows):
    assert [c['id'] for c in cases]==[r['id'] for r in rows];errors={};count=0
    for c,row in zip(cases,rows):
        assert len(row['calls'])==2 and row['calls'][0]['stdout']==row['calls'][1]['stdout'],c['id']
        r=json.loads(row['calls'][0]['stdout']);assert r['ok']==c['ok'],(c['id'],r)
        if not c['ok']:
            if c.get('late'):assert r['state']==Z and r['time']==3. and r['substeps']>0,r
            continue
        coarse=c['id']=='refinement-coarse'
        if c['kind']=='direct':
            target=c['expected'];refstress=c['expected_stress']
            if c.get('restart_from'):
                previous=next(x for x in rows if x['id']==c['restart_from']);parent=json.loads(previous['calls'][0]['stdout'])['points'][-1]['state'];target=relaxation(parent,1.);refstress=stress(target)
            ee=compare(r['state'],target,'state',coarse);obs=json.loads(row['observation']);assert obs['ok'];pe=compare(obs['values'],refstress,'stress',coarse);count+=19
            assert r['time']==c['time'],(c['id'],r['time'],c['time']);errors[c['id']]=dict(state=ee,stress=pe)
        else:
            assert r['model']==MODEL and r['units']=='SI' and r['parameters']==P and r['initial']==c['initial']
            ee=pe=0.;times=set()
            for point in r['points']:
                ref=next((x for x in c['references'] if abs(x['time']-point['time'])<1e-12),None);assert ref,c['id']
                ee=max(ee,compare(point['state'],ref['state'],'state',coarse));pe=max(pe,compare(point['observables'],ref['stress'],'stress',coarse));count+=19;times.add(ref['time'])
                assert point['strain']==point['state'][:6]
                assert point['state'][12]>=0 and abs(sum(point['state'][6:9]))<=1e-10
            assert times=={x['time'] for x in c['references']};errors[c['id']]=dict(state=ee,stress=pe)
    assert errors['refinement-fine']['state']<errors['refinement-coarse']['state']/5
    assert errors['refinement-fine']['stress']<errors['refinement-coarse']['stress']/5
    return dict(passed=True,cases=len(cases),raw_calls=2*len(cases),numeric_comparisons=count,errors=errors)
def collect(solver,output):
    cases=json.loads((BASE/'cases.json').read_text())['cases'];rows=[]
    for src in cases:
        c=copy.deepcopy(src)
        if c.get('restart_from'):
            prev=json.loads(next(x for x in rows if x['id']==c['restart_from'])['calls'][0]['stdout']);state=prev['points'][-1]['state'];c['argv'][c['argv'].index('--initial')+1]=csv(state)
        row=dict(id=c['id'],calls=[])
        for i in range(2):
            proc=subprocess.run([str(solver.resolve()),*c['argv']],capture_output=True,text=True,timeout=120);row['calls'].append(dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
        r=json.loads(row['calls'][0]['stdout'])
        if c['ok'] and c['kind']=='direct' and r['ok']:
            proc=subprocess.run([str(solver.resolve()),'--mode','observe-time','--model',MODEL,'--parameters',csv(c['parameters']),'--initial',csv(r['state']),'--strain-rate',csv(c['rate']),'--start-time',str(c['time'])],capture_output=True,text=True,timeout=120);row['observation']=proc.stdout
        rows.append(row);output.write_text(json.dumps(rows,indent=2)+'\n')
    report=assess(cases,rows);output.with_name(output.stem+'-report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','native','assess']);ap.add_argument('--solver',type=Path);ap.add_argument('--raw',type=Path);a=ap.parse_args()
    if a.action=='prepare':print('Prepared',build(),'frozen-input cases; no compiled calls')
    elif a.action=='native':print(json.dumps(collect(a.solver,a.raw),indent=2))
    else:print(json.dumps(assess(json.loads((BASE/'cases.json').read_text())['cases'],json.loads(a.raw.read_text())),indent=2))
