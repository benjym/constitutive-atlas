#!/usr/bin/env python3
"""Independent closed-form reference plus source-only transcription checks. No solver."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.source))
from atlas.model import load,evaluation_environment,check_solution_state
from atlas.dsl import parse,evaluate,Sym
here=Path(__file__).parent;requests=json.loads((here/'requests.json').read_text());m=load(a.source/'tests/fixtures/predictor-constraint/projection.json')
def state(z):return {'sigma':z[:6],'ep':z[6],'gamma':z[7]}
rows=[]
for c in requests['cases']:
 K,Y,cap=c['parameters'];zn=c['initial'];trial=zn[0]+K*sum(c['strain'][:3]);p=min(trial,Y);gamma=max((trial-Y)/K,0);ref=[p,p,p,0,0,0,zn[6]+gamma,gamma];admissible=zn[0]>0 and zn[0]<=Y and zn[0]<=cap and p>0 and p<=cap
 expected=c['expected']['ok'];budget=c['id']=='budget-failure'
 assert expected==(admissible and not budget)
 row={'id':c['id'],'trial_pressure':trial,'reference':ref,'algebraic_root_admissible':admissible,'expected_compiled_ok':expected}
 if expected:
  assert max(abs(x-y) for x,y in zip(ref,c['expected']['state']))<1e-14
  env=evaluation_environment(m,state(ref),state(zn),c['strain'],dict(zip(m['parameters'],c['parameters'])))
  residual={k:evaluate(parse(v),env) for k,v in m['equations'].items()};flat=[x for v in residual.values() for x in (v.v if isinstance(v,Sym) else [v])]
  assert max(map(abs,flat))<1e-12;assert check_solution_state(m,state(ref),dict(zip(m['parameters'],c['parameters'])))
  row['max_raw_residual']=max(map(abs,flat))
 if c['id']=='plastic':
  predictor=[trial]*3+[0,0,0,zn[6],0]
  env=evaluation_environment(m,state(predictor),state(zn),c['strain'],dict(zip(m['parameters'],c['parameters'])))
  assert not check_solution_state(m,state(predictor),dict(zip(m['parameters'],c['parameters'])))
  row['predictor_domain_valid_but_solution_invalid']=True
 if c['id']=='excluded-root':
  env=evaluation_environment(m,state(ref),state(zn),c['strain'],dict(zip(m['parameters'],c['parameters'])))
  assert not check_solution_state(m,state(ref),dict(zip(m['parameters'],c['parameters'])))
  row['full_root_domain_valid_but_physically_excluded']=True
 rows.append(row)
a.output.write_text(json.dumps({'status':'passed-source-only','compiled_observations':False,'cases':rows},indent=2)+'\n')
