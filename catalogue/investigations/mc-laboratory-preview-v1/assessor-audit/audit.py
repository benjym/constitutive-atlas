"""Run the preserved prospective assessor on synthetic ideal/corrupted journals only."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import math

ROOT=Path(__file__).resolve().parent;FROZEN=ROOT/'frozen'
spec=importlib.util.spec_from_file_location('audited_path_assessor',FROZEN/'assess_paths.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
reqs=json.loads((FROZEN/'requests.json').read_text());ref=json.loads((FROZEN/'reference-p360.json').read_text());cat=json.loads((FROZEN/'generated/models.json').read_text());model=next(x for x in cat['models']if x['id']=='mohr-coulomb');refs={x['id']:x for x in ref['paths']}

def recalc(point,protocol):
 state=point['state'];q=state[0]-.5*(state[1]+state[2]);point.update(p=sum(state[:3])/3,q=abs(q),q_signed=q,u=100000.-.5*(state[1]+state[2])if protocol in(2,3)else 0.)

def ideal():
 rows=[{'id':'describe','raw':json.dumps(cat)}]
 for req in reqs:
  pts=[]
  for q in refs[req['id']]['points']:
   pt={'state':[float(x)for x in q['state']],'strain':[float(x)for x in q['strain']],'control':float(q['control']),'iterations':0,'substeps':0,'rejected':0,'error':0.};recalc(pt,req['protocol']);pts.append(pt)
  r={'ok':True,'model':model,'catalogue_hash':cat['sha256'],'parameters':[float(x)for x in req['parameters'].split(',')],'initial':[float(x)for x in req['initial'].split(',')],'integration_settings':dict(zip(('version','norm','residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),['incremental-settings-0.1','scaled_component_max']+[float(x)for x in req['integration_settings'].split(',')])),'points':pts}
  for k in ('protocol','target','steps','cycles'):r[k]=req[k]
  rows.append({'id':req['id'],'request':req,'raw':json.dumps(r)})
 return rows

def mutate_body(rows,index,fn):
 r=json.loads(rows[index]['raw']);fn(r);rows[index]['raw']=json.dumps(r)

def outcome(rows):
 try:return {'accepted':True,'result':mod.assess(rows,reqs,ref,cat)}
 except Exception as e:return {'accepted':False,'exception':type(e).__name__,'message':str(e)}

def save(name,rows):
 p=ROOT/'witnesses';p.mkdir(exist_ok=True);(p/(name+'.json')).write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')

def run():
 base=ideal();save('ideal',base);results={'ideal':outcome(base)}
 probes=[
 ('protocol_boolean_alias',lambda rows:mutate_body(rows,1,lambda r:r.__setitem__('protocol',False))),
 ('cycles_boolean_alias',lambda rows:mutate_body(rows,1,lambda r:r.__setitem__('cycles',False))),
 ('steps_float_alias',lambda rows:mutate_body(rows,1,lambda r:r.__setitem__('steps',float(r['steps'])))),
 ('model_parameter_order_reversed',lambda rows:mutate_body(rows,1,lambda r:r['model'].__setitem__('parameters',dict(reversed(list(r['model']['parameters'].items())))))),
 ('descriptor_parameter_order_reversed',lambda rows:rows[0].__setitem__('raw',json.dumps(dict(cat,models=[dict(m,parameters=dict(reversed(list(m['parameters'].items()))))if m['id']=='mohr-coulomb'else m for m in cat['models']])))),
 ('missing_final_point',lambda rows:mutate_body(rows,1,lambda r:r['points'].pop())),
 ('wrong_final_stress',lambda rows:mutate_body(rows,1,lambda r:r['points'][-1]['state'].__setitem__(0,r['points'][-1]['state'][0]+1000.))),
 ('boolean_physical_state',lambda rows:mutate_body(rows,1,lambda r:r['points'][1]['state'].__setitem__(0,True))),
 ('nonzero_shear',lambda rows:mutate_body(rows,1,lambda r:r['points'][1]['state'].__setitem__(3,1e-100))),
 ('wrong_control',lambda rows:mutate_body(rows,1,lambda r:r['points'][1].__setitem__('control',99.))),
 ]
 for name,fn in probes:
  rows=copy.deepcopy(base);fn(rows);save(name,rows);results[name]=outcome(rows)
 # Pair witness: both journals pass their individual source budgets but violate declared parity.
 pair=[]
 for name,sgn in [('parity_native',1),('parity_wasm',-1)]:
  rows=copy.deepcopy(base)
  def bump(r):
   p=r['points'][1];p['state'][0]+=sgn*.0005;recalc(p,reqs[0]['protocol'])
  mutate_body(rows,1,bump);save(name,rows);results[name]=outcome(rows);pair.append(rows)
 a=json.loads(pair[0][1]['raw'])['points'][1]['state'][0];b=json.loads(pair[1][1]['raw'])['points'][1]['state'][0]
 results['declared_parity_pair']={'difference':abs(a-b),'budget':1e-10*max(1,abs(a),abs(b)),'violates':abs(a-b)>1e-10*max(1,abs(a),abs(b))}
 expected={'ideal':True,'protocol_boolean_alias':True,'cycles_boolean_alias':True,'steps_float_alias':True,'model_parameter_order_reversed':True,'descriptor_parameter_order_reversed':True,'missing_final_point':False,'wrong_final_stress':False,'boolean_physical_state':False,'nonzero_shear':False,'wrong_control':False,'parity_native':True,'parity_wasm':True}
 checks={n:results[n]['accepted']==v for n,v in expected.items()};checks['individually_passing_pair_violates_policy']=results['declared_parity_pair']['violates']
 d={'identity':'mc-preview-path-assessor-audit-v1','assessor_sha256':hashlib.sha256((FROZEN/'assess_paths.py').read_bytes()).hexdigest(),'candidate_calls':0,'compiled_calls':0,'checks':checks,'audit_reproduction_status':'pass'if all(checks.values())else'fail','outcomes':results}
 (ROOT/'checks.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n');print(json.dumps({'audit_reproduction_status':d['audit_reproduction_status'],'outcomes':{n:v.get('accepted',v.get('violates'))for n,v in results.items()},'parity':results['declared_parity_pair']}))
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':run()
