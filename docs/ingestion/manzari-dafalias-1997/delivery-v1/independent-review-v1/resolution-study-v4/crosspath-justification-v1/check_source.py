import hashlib,importlib.util,json,math
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parents[2];S=P/'resolution-justification-v1';ROOT=P.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('all six packet hashes',all(h(S/k)==v for k,v in json.loads((S/'manifest.json').read_text()).items()))
inputs=json.loads((S/'inputs.json').read_text());print(inputs.keys())
plan=json.loads((P/'resolution-study-v4/requests.json').read_text());r=json.loads((S/'results.json').read_text());paths=[c for c in plan['cases'] if c['group'] in ['axis','interior']]
check('28 exact requested case identities',set(r['cases'])=={c['id'] for c in paths} and len(paths)==28)
for c in paths:
 check(c['id']+'/exact checkpoint coverage',[v['coordinate'] for v in r['cases'][c['id']]['checkpoints']]==[cp.get('axial_strain',cp.get('t')) for cp in c['checkpoints']])
check('28 all complete source gates',r['passed'] and r['completed_cases']==28 and not r['failures'] and not r['source_gate_failures'] and all(c['source_gates_passed'] for c in r['cases'].values()))
check('200 checkpoints86refinements',sum(len(c['checkpoints']) for c in r['cases'].values())==200 and len(r['refinement'])==86 and all(x['passed'] for x in r['refinement']))
check('root and domain margins',max(c['max_local_residual'] for c in r['cases'].values())<=1e-11 and min(c['min_hardening_margin'] for c in r['cases'].values())>0)
# Reproduce independent source Python with only its output path redirected into reviewer scope.
spec=importlib.util.spec_from_file_location('independent_source_be',S/'source_be.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.P=D;module.main()
check('source results exactly reproduced',json.loads((D/'results.json').read_text())==r)
# Independently recalculate every group error from retained tensors/references.
for c in paths:
 axis=c['group']=='axis'
 for row,cp in zip(r['cases'][c['id']]['checkpoints'],c['checkpoints']):
  e={'stress':max(abs(a-b)/(100+.01*max(1000,abs(b))) for a,b in zip(row['sigma_Pa'],cp['sigma_Pa'])),'alpha':max(abs(a-b)/.002 for a,b in zip(row['alpha'],cp['alpha'])),'e':abs(row['e']-cp['e'])/.0002,'radial':abs(row['radial_strain']-cp['radial_strain'])/.0002 if axis else 0}
  e.update(worst=max(e.values()),passed=max(e.values())<=1);check(c['id']+'/sourceerror/'+str(row['coordinate']),e==row['source_error'])
for f in r['refinement']:
 coarse=r['cases'][f['case'].rsplit('-',1)[0]+'-2048'];cr=next(v for v in coarse['checkpoints'] if v['coordinate']==f['coordinate']);fine=next(v for v in r['cases'][f['case']]['checkpoints'] if v['coordinate']==f['coordinate']);co=cr['source_error']['worst'];fi=fine['source_error']['worst'];check(f['case']+'/refinement/'+str(f['coordinate']),f['coarse']==co and f['fine']==fi and f['passed']==(fi<co or max(fi,co)<1e-5))
(D/'checks.json').write_text(json.dumps({'reviewer_compiled_calls':0,'decision':'crosspath justification accepted for exact frozen study; no compiled pass inferred','checks':checks},indent=2)+'\n')
