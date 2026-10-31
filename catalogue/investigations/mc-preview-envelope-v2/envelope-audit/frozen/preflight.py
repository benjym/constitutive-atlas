"""Source-ideal API envelopes and independent corruptions, before saved observations."""
from pathlib import Path
import json,copy,subprocess,sys
from assess_paths import load,assess
from assess_parity import assess as parity
s=Path(__file__).resolve().parent
req=load(s/'requests.json');ref=load(s/'reference/reference-p360.json');cat=load(s/'generated/models.json');refs={p['id']:p for p in ref['paths']}
def encode(x):return json.dumps(x,separators=(',',':'))
rows=[{'id':'describe','raw':encode(cat)}]
for r in req:
 points=[]
 for b in refs[r['id']]['points']:
  st=list(map(float,b['state']));de=list(map(float,b['strain']));p=sum(st[:3])/3;q=st[0]-.5*(st[1]+st[2]);u=100000.-.5*(st[1]+st[2])if r['protocol']in(2,3)else 0.
  points.append(dict(control=float(b['control']),strain=de,state=st,p=p,q=abs(q),q_signed=q,u=u,iterations=0,substeps=0,rejected=0,error=0))
 vals=[float(v)for v in r['integration_settings'].split(',')]
 settings=dict(zip(('version','norm','residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),['incremental-settings-0.1','scaled_component_max',*vals]))
 response=dict(ok=True,message='',schema_version='0.1',catalogue_hash=cat['sha256'],model=r['model'],elapsed_ms=0.,parameters=[float(v)for v in r['parameters'].split(',')],initial=[float(v)for v in r['initial'].split(',')],integration_settings=settings,protocol=r['protocol'],target=r['target'],steps=r['steps'],cycles=r['cycles'],points=points)
 rows.append(dict(id=r['id'],request=r,raw=encode(response)))
def check(x):return assess(x,req,ref,cat)
ideal=check(rows);assert ideal['passed']is True
cases={}
def corrupted(name,mutate):
 x=copy.deepcopy(rows);v=json.loads(x[1]['raw']);mutate(v);x[1]['raw']=encode(v);cases[name]=x
corrupted('model-object',lambda x:x.update(model=next(m for m in cat['models']if m['id']=='mohr-coulomb')))
corrupted('model-wrong-id',lambda x:x.update(model='linear-elastic'))
corrupted('model-bool',lambda x:x.update(model=True))
corrupted('hash',lambda x:x.update(catalogue_hash='0'*64))
corrupted('schema',lambda x:x.update(schema_version='0.3'))
corrupted('protocol-bool',lambda x:x.update(protocol=False))
corrupted('steps-float',lambda x:x.update(steps=32.))
corrupted('cycles-bool',lambda x:x.update(cycles=False))
corrupted('parameter-value',lambda x:x['parameters'].__setitem__(1,1.))
corrupted('parameter-bool',lambda x:x['parameters'].__setitem__(2,False))
corrupted('missing-point',lambda x:x['points'].pop())
corrupted('stress',lambda x:x['points'][-1]['state'].__setitem__(0,x['points'][-1]['state'][0]+1000.))
corrupted('strain',lambda x:x['points'][-1]['strain'].__setitem__(0,1.))
corrupted('shear',lambda x:x['points'][-1]['state'].__setitem__(3,1e-100))
corrupted('control',lambda x:x['points'][-1].update(control=1.))
corrupted('diagnostic-bool',lambda x:x['points'][-1].update(iterations=False))
x=copy.deepcopy(rows);d=json.loads(x[0]['raw']);m=next(m for m in d['models']if m['id']=='mohr-coulomb');m['parameters']=dict(reversed(list(m['parameters'].items())));x[0]['raw']=encode(d);cases['descriptor-order']=x
results={}
for name,x in cases.items():
 try:check(x)
 except Exception as exc:results[name]={'rejected':True,'reason':type(exc).__name__}
 else:raise RuntimeError('false pass '+name)
assert parity(rows,rows,req)['passed']is True
plus=copy.deepcopy(rows);minus=copy.deepcopy(rows)
for rs,sign in ((plus,1),(minus,-1)):
 v=json.loads(rs[1]['raw']);v['points'][1]['state'][0]+=sign*.0005;st=v['points'][1]['state'];v['points'][1].update(p=sum(st[:3])/3,q=abs(st[0]-st[1]),q_signed=st[0]-st[1]);rs[1]['raw']=encode(v);check(rs)
try:parity(plus,minus,req)
except Exception:results['pair-parity']={'rejected':True}
else:raise RuntimeError('parity false pass')
p=subprocess.run([sys.executable,'-B','-O','-c','import assess_paths'],cwd=s,capture_output=True,text=True);assert p.returncode!=0 and 'RuntimeError'in p.stderr
results['optimized-runtime']={'rejected':True}
(s/'ideal-journal.json').write_text(json.dumps(rows,indent=2)+'\n')
result={'identity':'mc-preview-envelope-preflight-v2','passed':True,'ideal':ideal,'negative_cases':results,'new_candidate_calls':0,'saved_backend_observations_read':0}
(s/'preflight-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'passed':True,'negative_cases':len(results),'ideal_points':ideal['points']}))
