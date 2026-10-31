"""Collect serial native requests or reassess immutable saved raw responses."""
import argparse,hashlib,json,math,subprocess
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--solver',type=Path);ap.add_argument('--replay',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();base=Path(__file__).resolve().parent
    freeze=json.loads((base/'prospective-freeze.json').read_text())
    for f,h in freeze['files'].items():assert hashlib.sha256((base/f).read_bytes()).hexdigest()==h,f
    deck=json.loads((base/'cases.json').read_text());a.output.mkdir(parents=True,exist_ok=True)
    if a.replay:raw=json.loads(a.replay.read_text())
    else:
        assert a.solver
        described=json.loads(subprocess.check_output([str(a.solver),'--describe'],text=True));embedded=next(m for m in described['models']if m['id']=='drucker-prager');assert embedded==json.loads((base/'candidate-definition.json').read_text())
        raw={'solver_sha256':hashlib.sha256(a.solver.read_bytes()).hexdigest(),'catalogue_sha256':described['sha256'],'calls':[]}
        for case in deck['cases']:
            result=subprocess.run([str(a.solver),*case['arguments']],capture_output=True,text=True,timeout=30);raw['calls'].append({'id':case['id'],'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});(a.output/'raw.json').write_text(json.dumps(raw,indent=2)+'\n')
    assert len(raw['calls'])==len(deck['cases']);rows=[];t=deck['tolerances']
    for case,call in zip(deck['cases'],raw['calls'],strict=True):
        assert case['id']==call['id'];result=json.loads(call['stdout']);actual=result.get('state',[]);ratio=None
        if case['expected_failure']:passed=call['returncode']!=0 and result.get('ok')is False and actual==case['initial']
        else:
            limits=[(t['stress_absolute_Pa']if i<6 else t['other_state_absolute'])+t['relative']*abs(v)for i,v in enumerate(case['expected'])]
            passed=len(actual)==len(case['expected'])and all(math.isfinite(v)for v in actual)
            if passed:ratio=max(abs(v-e)/l for v,e,l in zip(actual,case['expected'],limits));passed=ratio<=1 and call['returncode']==0 and result.get('ok')is True
        rows.append({'id':case['id'],'passed':passed,'max_budget_fraction':ratio,'message':result.get('message')})
    report={'kind':'dp-dilatancy-domain-native-v1','candidate_sha256':deck['candidate_sha256'],'freeze_sha256':hashlib.sha256((base/'prospective-freeze.json').read_bytes()).hexdigest(),'solver_sha256':raw['solver_sha256'],'catalogue_sha256':raw['catalogue_sha256'],'cases':rows,'count':len(rows),'passed':all(r['passed']for r in rows),'scope':'Native CLI only; recovery uses separate requests. No Wasm/website or scientific admission claim.'};(a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f"{sum(r['passed']for r in rows)}/{len(rows)} pass")
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
