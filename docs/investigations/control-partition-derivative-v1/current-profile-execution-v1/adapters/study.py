"""Bounded same-protocol native/Wasm qualification and saved-only assessment."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,sys
from decimal import Decimal as D
import os
R=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()/'docs/ingestion/burgers-itasca900/integration-v1'
sys.path.insert(0,str(R.parents[3]))
from atlas.schedule import schedule_command,validate_schedule
from reference import reference

def csv(xs):return ','.join(format(x,'.17g') for x in xs)
class Backend:
    def __init__(self,kind,engine,folder):
        self.kind=kind;self.engine=str(Path(engine).resolve());self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.calls=[]
        self.node=subprocess.Popen(['node',str(R/'wasm_host.mjs'),self.engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(self.folder/'stderr.txt').open('w'),text=True) if kind=='wasm' else None
    def call(self,label,function,args,command):
        q=dict(label=label,function=function,args=args)
        if self.node:
            self.node.stdin.write(json.dumps(q)+'\n');self.node.stdin.flush();line=self.node.stdout.readline()
            if not line: raise RuntimeError('Wasm host stopped; see stderr.txt')
            data=json.loads(line)
        else:
            p=subprocess.run([self.engine]+command,capture_output=True,text=True,timeout=120)
            data=json.loads(p.stdout)
            q.update(returncode=p.returncode,stderr=p.stderr)
            assert p.returncode==(0 if data.get('ok',True) else 1)
        q['response']=data;self.calls.append(q)
        (self.folder/'calls.json').write_text(json.dumps(self.calls,indent=2)+'\n')
        return data
    def close(self):
        if self.node:self.node.stdin.close();assert self.node.wait(timeout=30)==0

def execute(backend):
    req=json.loads((R/'requests.json').read_text());model=json.loads((R.parents[3]/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_text());mid=model['id'];params=req['ode'][0]['parameters'];initial=req['ode'][0]['initial']
    backend.call('descriptor','atlas_describe',[],['--describe'])
    def ode(case,label=None):
        args=[mid,csv(case['parameters']),csv(case['initial']),csv(case['rate']),case['start'],case['duration'],case['rtol'],case['atol'],case['min_step'],case['max_step'],case['budget']]
        keys=['--model','--parameters','--initial','--strain-rate','--start-time','--duration','--rtol','--atol','--min-time-step','--max-time-step','--max-substeps']
        cmd=['--mode','integrate-time']+[x for pair in zip(keys,map(str,args)) for x in pair]
        return backend.call(label or case['id'],'atlas_integrate_time',args,cmd)
    def schedule(spec,label):
        cmd=schedule_command(spec,'ENGINE')[1:];settings=validate_schedule(spec);wire=[]
        for seg in spec['segments']:
            wire.extend([seg['duration'],seg['samples']])
            for ctrl in seg['controls']:wire.extend([int(ctrl['quantity']=='stress'),{'hold':0,'rate':1,'target':2}[ctrl['kind']],ctrl.get('value',0)])
        args=[mid,csv(spec['parameters']),csv(spec['initial']),csv(spec.get('initial_strain',[0]*6)),csv(spec.get('initial_strain_rate',[0]*6)),csv(wire),','.join(s['id'] for s in spec['segments']),spec['start_time'],settings['relative_tolerance'],settings['absolute_scale_fraction'],settings['minimum_step'],settings['maximum_step'],settings['maximum_substeps'],settings['nonlinear_tolerance'],settings['maximum_iterations']]
        return backend.call(label,'atlas_run_schedule',args,cmd)
    # All requests are saved before any assertion in the assessor; failure evidence survives.
    for c in req['ode']:
        ode(c)
        if c['expected_ok']:ode(c,c['id']+'-repeat')
        else:ode(req['ode'][0],c['id']+'-recovery')
    base=copy.deepcopy(req['ode'][0]);base['duration']=1
    first=ode(base,'ode-restart-first');second=copy.deepcopy(base);second['initial']=first['state'];second['start']=first['time'];ode(second,'ode-restart-second')
    for case in req['schedules']:
        schedule(case['spec'],case['id']);schedule(case['spec'],case['id']+'-repeat')
    # Restart from each backend's own complete checkpoint, not another backend's state.
    creep=copy.deepcopy(next(x['spec'] for x in req['schedules'] if x['id']=='creep'))
    creep['segments'][0]['duration']=1;creep['segments'][0]['samples']=4
    first=schedule(creep,'creep-restart-first');pt=first['points'][-1]
    second=copy.deepcopy(creep);second.update(initial=pt['state'],initial_strain=pt['strain'],initial_strain_rate=pt['strain_rate'],start_time=pt['time'])
    schedule(second,'creep-restart-second')
    # Fail an output interval after an internal accepted substep; no partial commit.
    fail=copy.deepcopy(next(x['spec'] for x in req['schedules'] if x['id']=='relaxation'));fail['solver']['maximum_substeps']=2;fail['solver']['maximum_step']=.01
    schedule(fail,'schedule-budget-rollback');schedule(req['schedules'][0]['spec'],'schedule-recovery')
    for label in req['invalids']:
        z=csv(initial);p=csv(params)
        if label=='missing-state':z=''
        if label=='bad-trace':bad=initial.copy();bad[6]=1;z=csv(bad)
        if label=='zero-viscosity':bad=params.copy();bad[-1]=0;p=csv(bad)
        if label=='untimed-rejection':
            args=[mid,p,z,csv([0]*6)];cmd=['--mode','integrate','--model',mid,'--parameters',p,'--initial',z,'--strain',csv([0]*6)]
            backend.call(label,'atlas_integrate',args,cmd)
        else:
            args=[mid,p,z,csv([0]*6),4];cmd=['--mode','evaluate-time','--model',mid,'--parameters',p,'--initial',z,'--strain-rate',csv([0]*6),'--start-time','4']
            backend.call(label,'atlas_evaluate_time',args,cmd)
        ode(req['ode'][0],label+'-recovery')
    backend.call('observe','atlas_observe_time',[mid,csv(params),csv(initial),csv([0]*6),4],['--mode','observe-time','--model',mid,'--parameters',csv(params),'--initial',csv(initial),'--strain-rate',csv([0]*6),'--start-time','4'])
    return backend.calls

def assess(calls):
    policy=json.loads((R/'acceptance.json').read_text());req=json.loads((R/'requests.json').read_text());refs=json.loads((R/'references.json').read_text());model=json.loads((R.parents[3]/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_text())
    d={x['label']:x['response'] for x in calls};assert len(d)==len(calls)
    desc=d['descriptor'];assert desc['models']==[model]
    catalogue_hash=desc.get('catalogue_hash')
    # Descriptor's content-addressed catalogue identity is generated canonically.
    expected_hash=hashlib.sha256(json.dumps([model],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    # Compiler descriptor uses its own canonical encoding; all response hashes must
    # bind the generated descriptor hash retained in models.json.
    if catalogue_hash is None:catalogue_hash=desc['sha256']
    assert catalogue_hash==expected_hash
    def check_state(actual,expected,budgets):
        ratios=[]
        for j,(x,y) in enumerate(zip(actual,expected)):
            budget=budgets[0] if j<6 else budgets[1]
            ratios.append(abs(x-float(y))/budget)
        assert len(actual)==len(expected)==12
        assert max(ratios)<=1,max(ratios)
        return max(ratios)
    max_fraction=0.;points=0
    for case in req['schedules']:
        out=d[case['id']];assert out['ok'];assert out['catalogue_hash']==catalogue_hash
        assert len(out['points'])==len(refs[case['id']])
        for pt,ref in zip(out['points'],refs[case['id']]):
            assert pt['time']==float(ref['time']) and pt['segment']==ref['segment'] and pt['side']==ref['side']
            max_fraction=max(max_fraction,check_state(pt['state'],ref['state'],[2000,2e-4] if case['id'].endswith('-coarse') else [20,2e-6]))
            assert pt['observables']==pt['state'][:6]
            assert max(abs(a-float(b)) for a,b in zip(pt['strain'],ref['strain']))<=(2e-4 if case['id'].endswith('-coarse') else 2e-6)
            assert abs(sum(pt['state'][6:9]))<=1e-12
            points+=1
        assert out==d[case['id']+'-repeat']
    for case in req['ode']:
        out=d[case['id']];assert out['ok']==case['expected_ok']
        if out['ok']:
            spec=dict(initial=case['initial'],initial_strain=[0]*6,start_time=case['start'],parameters=case['parameters'],segments=[dict(duration=case['duration'],samples=1,controls=[dict(quantity='strain',kind='rate',value=v) for v in case['rate']])])
            ref=reference(spec,100)[-1]
            max_fraction=max(max_fraction,check_state(out['state'],ref['state'],[.01,1e-9]))
            assert out['time']==case['start']+case['duration']
            assert out==d[case['id']+'-repeat']
        else:
            assert out['state']==case['initial'] and out['time']==case['start']
            if case['id']=='budget-rollback':assert out['substeps']>=2
            assert d[case['id']+'-recovery']==d['ode-relaxation']
    for label in req['invalids']:
        assert not d[label]['ok'];assert d[label+'-recovery']==d['ode-relaxation']
    assert d['observe']['values']==req['ode'][0]['initial'][:6]
    ref=refs['relaxation'][-1]['state'];check_state(d['ode-restart-second']['state'],ref,[.01,1e-9])
    check_state(d['creep-restart-second']['points'][-1]['state'],refs['creep'][-1]['state'],[20,2e-6])
    assert max(abs(a-float(b)) for a,b in zip(d['creep-restart-second']['points'][-1]['strain'],refs['creep'][-1]['strain']))<=2e-6
    failed=d['schedule-budget-rollback'];assert not failed['ok'];assert len(failed['points'])==2
    assert failed['points'][-1]['time']==4 and failed['points'][-1]['state']==req['ode'][0]['initial']
    assert d['schedule-recovery']==d['relaxation']
    fine=d['relaxation']['points'][-1]['state'];coarse=d['relaxation-coarse']['points'][-1]['state'];ref=list(map(float,refs['relaxation'][-1]['state']))
    assert max(abs(a-b) for a,b in zip(fine,ref))<max(abs(a-b) for a,b in zip(coarse,ref))
    fine=d['creep']['points'][-1]['strain'];coarse=d['creep-coarse']['points'][-1]['strain'];ref=list(map(float,refs['creep'][-1]['strain']))
    assert max(abs(a-b) for a,b in zip(fine,ref))<max(abs(a-b) for a,b in zip(coarse,ref))
    return dict(ok=True,calls=len(calls),analytical_schedule_points=points,maximum_state_budget_fraction=max_fraction,catalogue_hash=catalogue_hash,refinement='pass',restart='pass',rollback_recovery='pass')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['native','wasm','assess']);ap.add_argument('path');ap.add_argument('--output');a=ap.parse_args()
    if a.mode=='assess':calls=json.loads(Path(a.path).read_text())
    else:
        b=Backend(a.mode,a.path,a.output)
        try:calls=execute(b)
        finally:b.close()
    result=assess(calls)
    if a.output:(Path(a.output)/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
