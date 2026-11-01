"""Supplementary prospective recovery/restart/CLI gates; same fixed budgets.
Run after main raw observations exist; retains exact restart requests and calls.
"""
import argparse,copy,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('maxwell_checks',ROOT/'tests/test_maxwell.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE=Path(__file__).resolve().parent

def cases_for(raw):
    cases=json.loads((BASE/'reference-cases.json').read_text())['cases'];rows=json.loads(raw.read_text());out=[]
    good=next(c for c in cases if c['id']=='tensor-tau2-duration0.5')
    for bad in [c for c in cases if not c['ok']]:
        out.append(copy.deepcopy(bad));recovery=copy.deepcopy(good);recovery['id']='recovery-after-'+bad['id'];out.append(recovery)
    for ident,kind in [('creep-schedule','creep'),('relaxation-schedule','relax')]:
        row=next(r for r in rows if r['id']==ident);end=json.loads(row['calls'][0]['stdout'])['points'][-1]
        assert all(type(v) in (int,float) for v in end['strain_rate'])
        s=m.specification('restart');s.update(start_time=end['time'],initial=end['state'],initial_strain=end['strain'],initial_strain_rate=end['strain_rate'])
        s['segments']=[m.segment('continue',2,[m.hold('stress' if kind=='creep' else 'strain') for _ in range(6)],4)]
        if kind=='creep':ref=lambda t:dict(state=m.Z,strain=[v*t/(2*m.P[2]) for v in m.dev(m.Z)])
        else:ref=lambda t:dict(state=m.exact(m.Z,m.ZERO,m.P,t),strain=m.ZERO)
        out.append(m.schedule_case('restart-'+kind,s,ref))
    return out

def assess(cases,rows):
    assert [c['id'] for c in cases]==[r['id'] for r in rows]
    errors={}
    for c,r in zip(cases,rows):
        assert len(r['calls'])==2
        assert r['calls'][0]['stdout']==r['calls'][1]['stdout']
        for call in r['calls']:
            assert call['returncode']==(0 if c['ok'] else 1)
            errors[c['id']]=m.assess(c,json.loads(call['stdout']))
    return errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backend',choices=['native','wasm'],required=True);p.add_argument('--solver',type=Path);p.add_argument('--module',type=Path);a=p.parse_args()
    cases=cases_for(BASE/(a.backend+'-raw.json'));casepath=BASE/(a.backend+'-transaction-cases.json');casepath.write_text(json.dumps({'cases':cases},indent=2)+'\n');out=BASE/(a.backend+'-transactions-raw.json')
    if a.backend=='native':
        rows=m.execute_native(a.solver,cases);out.write_text(json.dumps(rows,indent=2)+'\n')
    else:
        subprocess.run(['node',str(ROOT/'tools/test_maxwell_wasm.mjs'),str(a.module),str(casepath),str(out)],check=True);rows=json.loads(out.read_text())
    report={'passed':True,'errors_Pa':assess(cases,rows),'recovery_pairs':6,'actual_endpoint_restarts':2}
    if a.backend=='native':
        replaydir=Path('/private/tmp/atlas-maxwell-execution-v1/cli');replaydir.mkdir(exist_ok=True)
        paths=[ROOT/'examples/maxwell/creep.json',replaydir/'first.json',replaydir/'replay.json']
        for source,target in zip(paths,paths[1:]):
            r=subprocess.run([sys.executable,'-m','atlas.cli','run',str(source),'--solver',str(a.solver),'--output',str(target)],cwd=ROOT,capture_output=True,text=True,timeout=60);assert r.returncode==0,(r.stdout,r.stderr)
        first=json.loads(paths[1].read_text());second=json.loads(paths[2].read_text());assert first==second
        (BASE/'cli-creep-result.json').write_text(json.dumps(first,indent=2)+'\n')
        report['CLI_replay_exact']=True
        r=subprocess.run([str(a.solver),'--model',m.MODEL,'--mode','integrate','--initial',m.CSV(m.Z),'--parameters',m.CSV(m.P),'--strain','0,0,0,0,0,0'],capture_output=True,text=True)
        report['untimed_rejection_raw']=r.stdout;assert r.returncode==1 and json.loads(r.stdout)['ok'] is False
    (BASE/(a.backend+'-transactions.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
