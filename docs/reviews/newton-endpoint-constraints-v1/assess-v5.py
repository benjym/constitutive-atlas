"""Unchanged endpoint/residual budgets and exact transactional gates."""
from pathlib import Path
import json,sys,math
B=Path(__file__).resolve().parent

def assess(rows):
    cases=json.loads((B/'requests-v5.json').read_text());assert len(rows)==len(cases)
    result=[]
    for c,r in zip(cases,rows):
        assert c['id']==r['id'];checks={k:r[k] is True for k in ['input_unchanged','replay','recovery']};checks['rounding_bound']=0<=r['rounding']<=max(1,r['substeps']+r['rejected']);checks['status']=r['ok'] is c['expect_success'];checks['restart_bound']=0<=r['restarts']<=max(1,r['substeps']+r['rejected'])
        if 'expect_rounding' in c:checks['rounding_count']=r['rounding']==c['expect_rounding']
        if 'expect_restarts' in c:checks['restart_count']=r['restarts']==c['expect_restarts']
        if c['expect_success']:
            checks['endpoint']=len(r['state'])==len(c['target']) and all(math.isfinite(x) and abs(x-y)/1e5<=2e-8 for x,y in zip(r['state'],c['target']))
            checks['admissible']=r['endpoint_admissible'] is True
            checks['residual']=r['residual_ok'] is True and len(r['residual'])==len(c['target']) and all(math.isfinite(x) and abs(x)/1e5<=min(2e-10,c.get('settings',{}).get('residual_tolerance',2e-10)) for x in r['residual'])
        else:checks['rollback']=r['rollback'] is True and r['state']==c['initial']
        result.append(dict(id=c['id'],pass_=all(checks.values()),checks=checks))
    return dict(identity='newton-endpoint-regression-v5',pass_=all(x['pass_'] for x in result),cases=result)
if __name__=='__main__':
    result=assess([json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines()]);print(json.dumps(result,indent=2));sys.exit(0 if result['pass_'] else 1)
