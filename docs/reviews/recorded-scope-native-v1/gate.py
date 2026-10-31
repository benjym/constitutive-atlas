"""Frozen native recorded-scope plan and saved-only numerical/identity assessor."""
import copy,hashlib,json,math
from pathlib import Path

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csv(v):return ','.join(repr(float(x)) for x in v)
def flat(m):return [v for f in m['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
def path(mixed=False,zero=False,failure=False):
    rows=[dict(kind='stress' if mixed and i in [1,2] else 'strain',coefficients=[int(i==j) for j in range(6)]) for i in range(6)]
    values=[0,0] if zero else [0,1e-5,0] if failure else [0,1e-5,1e-5,0]
    return dict(initial_strain=[0]*6,controls=rows,knots=[dict(coordinate=i,targets=[a,100000,100000,0,0,0] if mixed else [a,-a/2,-a/2,0,0,0]) for i,a in enumerate(values)])

def plan(models):
    cases=[];public=[m for m in models if m['id']!='scope-synthetic-total-elastic'];assert len(public)==9
    def add(label,model,p,scope=None,restart=None,control=None,compare=None,analytic=False,failure=False,error=None,params=None):
        c=[v for row in p['controls'] for v in [int(row['kind']=='stress'),*row['coefficients']]];k=[v for knot in p['knots'] for v in [knot['coordinate'],*knot['targets']]]
        cases.append(dict(label=label,model=model['id'],initial=flat(model),controls=c,knots=k,scope=scope,restart=restart,control=control,compare=compare,analytic=analytic,failure=failure,error=error,params=params,executor='old' if label.startswith('old-') else 'new'))
    for model in public:
        name=model['id'];p=path(zero=True);add('old-public-'+name,model,p);add('new-public-'+name,model,p,compare='old-public-'+name);add('scope-public-'+name,model,p,'effective',compare='old-public-'+name)
    elastic=next(m for m in public if m['id']=='linear-elastic');total=next(m for m in models if m['id']=='scope-synthetic-total-elastic')
    for policy in [None,0,1]:add('total-strain-'+str(policy),total,path(),'total',policy,analytic=True)
    add('total-mixed',total,path(True),'total',1,analytic=True)
    add('old-reversal',elastic,path(True));add('new-reversal',elastic,path(True),compare='old-reversal');add('scope-reversal',elastic,path(True),'effective',compare='old-reversal')
    for policy in [0,1]:
        name='failed-'+str(policy);add('old-'+name,elastic,path(failure=True),restart=policy,control=1,failure=True);add('new-'+name,elastic,path(failure=True),restart=policy,control=1,failure=True,compare='old-'+name);add('scope-'+name,elastic,path(failure=True),'effective',policy,1,'old-'+name,failure=True)
    add('legacy-total',total,path(),error='legacy recorded contract requires effective stress',params='bad')
    for requested in ['effective','unknown','']:
        add('mismatch-'+(requested or 'empty'),total,path(),requested,error='recorded stress scope does not match model',params='bad')
    add('mismatch-effective-model',elastic,path(),'total',error='recorded stress scope does not match model',params='bad')
    return cases

def assess(packet):
    packet=Path(packet);cases=read(packet/'cases.json');pre=read(packet/'pre-build.json');catalogue=read(packet/'generated-models.json')
    assert sha(packet/'cases.json')==pre['generated_sha256']['cases.json']
    assert sha(packet/'generated-models.json')==pre['generated_sha256']['generated/models.json']
    assert cases==plan(catalogue['models'])
    results={};max_error=0.;policy=read(packet/'freeze.json')['total_reference']
    summary=read(packet/'observations/summary.json')
    for i,case in enumerate(cases):
        receipt=read(packet/'observations'/f'{i:03d}.json');assert receipt['case']==case
        binary='atlas_recorded_legacy_solver' if case['executor']=='old' else 'atlas_recorded_scope_solver'
        assert Path(receipt['command'][0]).name==binary and receipt['binary_sha256']==summary['binary_sha256'][binary]
        out=json.loads(receipt['stdout']);assert type(out.get('ok')) is bool and receipt['returncode']==(0 if out['ok'] else 1)
        if case['error']:
            assert out==dict(ok=False,message=case['error']);results[case['label']]=receipt;continue
        assert out['model']==case['model'] and out['catalogue_hash']==catalogue['sha256'] and out['initial']==case['initial']
        assert out['controls_wire']==case['controls'] and out['knots_wire']==case['knots'] and out['initial_strain']==[0]*6
        if case['scope'] is not None:
            assert out['api_version']=='experimental-recorded-replay-0.2'
            assert out['stress']==dict(source='state',name='sigma',measure='cauchy',scope=case['scope'],tensor_representation='mandel',sign='compression_positive')
        else:assert out['api_version']=='experimental-recorded-replay-0.1' and 'stress' not in out
        if case['restart'] is None:assert 'restart_settings' not in out and 'restart_diagnostics' not in out
        else:
            assert out['restart_settings']==dict(max_restarts=case['restart'],restart_step=1e-4,restart_levels=8)
            assert out['restart_diagnostics']==dict(searches=0,material_trials=0,accepted=0)
        assert out['ok']==(not case['failure'])
        if case['failure']:
            assert out['failed_knot']==2 and len(out['points'])==2 and out['state']==out['points'][-1]['state'] and out['strain']==out['points'][-1]['strain'] and out['material_trials']==1
        else:assert len(out['points'])==len(case['knots'])//7 and out['failed_knot']==-1
        if case['compare']:
            prior=results[case['compare']];candidate=copy.deepcopy(out)
            if case['scope'] is not None:candidate.pop('stress');candidate['api_version']='experimental-recorded-replay-0.1'
            assert candidate==json.loads(prior['stdout'])
            if case['scope'] is None:assert receipt['stdout']==prior['stdout']
        if case['analytic']:
            G=policy['E']/(2*(1+policy['nu']));K=policy['E']/(3*(1-2*policy['nu']));lam=K-2*G/3;mixed=case['controls'][7]==1
            for i,point in enumerate(out['points']):
                a=case['knots'][i*7+1];radial=-policy['nu']*a if mixed else -.5*a;strain=[a,radial,radial,0,0,0];stress=[policy['p0']+lam*(a+2*radial)+2*G*v for v in strain[:3]]+[0,0,0]
                err=max(abs(a-b) for a,b in zip(stress,point['state'][:6]));max_error=max(max_error,err)
                assert err<=policy['stress_tolerance_Pa'] and max(abs(a-b) for a,b in zip(strain,point['strain']))<=policy['strain_tolerance']
                assert point['coordinate']==case['knots'][i*7]
        results[case['label']]=receipt
    driver=read(packet/'observations/driver.json');assert driver['returncode']==0
    assert driver['binary_sha256']==summary['binary_sha256']['atlas_recorded_scope_api_driver']
    data=[json.loads(x) for x in driver['stdout'].splitlines()];assert len(data)==6
    for out in data[:2]:assert out==dict(ok=False,message='legacy recorded contract requires effective stress')
    for out in data[2:4]:assert out==dict(ok=False,message='recorded stress scope does not match model')
    for out in data[4:]:assert out['ok'] and out['api_version']=='experimental-recorded-replay-0.2' and out['stress']['scope']=='total'
    assert summary['processes']==len(cases)+1 and summary['max_stress_error_Pa']==max_error
    return dict(status='passed',processes=len(cases)+1,max_stress_error_Pa=max_error,native_calls=0,builds=0)
if __name__=='__main__':print(json.dumps(assess(Path(__file__).parent)))
