"""Run only the prospectively prepared recorded scope cases; retain each process."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.recorded import CONTROL_DEFAULTS
from gate import read,sha,csv,assess

def exercise(stage):
    d=Path(stage).resolve();pre=read(d/'pre-build.json')
    for p,h in pre['source_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in pre['generated_sha256'].items():assert sha(d/p)==h,p
    observations=d/'observations';observations.mkdir(exist_ok=False);cases=read(d/'cases.json')
    binaries={name:d/'build'/name for name in ['atlas_recorded_scope_solver','atlas_recorded_legacy_solver','atlas_recorded_scope_api_driver']};pins={n:sha(p) for n,p in binaries.items()}
    def capture(name,args,filename,case=None):
        binary=binaries[name];assert sha(binary)==pins[name]
        command=[str(binary),*args];r=subprocess.run(command,capture_output=True,text=True,timeout=30)
        record=dict(command=command,binary_sha256=pins[name],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
        if case is not None:record['case']=case
        (observations/filename).write_text(json.dumps(record,indent=2)+'\n');return json.loads(r.stdout) if case is not None else None
    max_error=0.;policy=read(Path(__file__).with_name('freeze.json'))['total_reference'];G=policy['E']/(2*(1+policy['nu']));K=policy['E']/(3*(1-2*policy['nu']));lam=K-2*G/3
    for i,case in enumerate(cases):
        name='atlas_recorded_legacy_solver' if case['executor']=='old' else 'atlas_recorded_scope_solver'
        args=['--mode','recorded','--model',case['model'],'--initial','bad' if case['error'] else csv(case['initial']),'--initial-strain','0,0,0,0,0,0','--recorded-controls-file',str(d/f'controls-{i}.csv'),'--recorded-knots-file',str(d/f'knots-{i}.csv')]
        if case['params'] is not None:args+=['--parameters',case['params']]
        if case['scope'] is not None:args+=['--recorded-stress-scope',case['scope']]
        if case['restart'] is not None:args+=['--recorded-restarts',csv([case['restart'],1e-4,8])]
        if case['control'] is not None:
            control=CONTROL_DEFAULTS|dict(max_material_trials=case['control']);args+=['--recorded-settings',csv(control.values())]
        out=capture(name,args,f'{i:03d}.json',case)
        if case['analytic']:
            for j,point in enumerate(out.get('points',[])):
                a=case['knots'][j*7+1];radial=-policy['nu']*a if case['controls'][7]==1 else -.5*a
                expected=[policy['p0']+lam*(a+2*radial)+2*G*v for v in [a,radial,radial]]+[0,0,0]
                max_error=max(max_error,max(abs(a-b) for a,b in zip(expected,point['state'][:6])))
    capture('atlas_recorded_scope_api_driver',[],'driver.json')
    for n,p in binaries.items():assert sha(p)==pins[n]
    summary=dict(processes=len(cases)+1,max_stress_error_Pa=max_error,binary_sha256=pins)
    (observations/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Same frozen assessor can run without processes from the retained packet.
    (d/'generated-models.json').write_bytes((d/'generated/models.json').read_bytes())
    (d/'freeze.json').write_bytes(Path(__file__).with_name('freeze.json').read_bytes())
    print(json.dumps(assess(d)))
if __name__=='__main__':exercise(sys.argv[1])
