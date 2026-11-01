"""Prospective path-only gate. Not browser, rollback or scientific admission."""
import json,math,sys,hashlib,struct
from pathlib import Path
if not __debug__:
 raise RuntimeError('assessor requires assertions enabled; optimized Python is unsupported')
HERE=Path(__file__).resolve().parent
from assess_binding import exact,verify

from strict_observation_json import loads

def load(p):return loads(Path(p).read_bytes())
def finite(x):
 if isinstance(x,bool)or not isinstance(x,(float,int))or not math.isfinite(x):raise ValueError('finite number required')
 return float(x)
def vector(x,n):
 assert isinstance(x,list)and len(x)==n
 return [finite(v)for v in x]
def close(a,b,budget):
 assert abs(finite(a)-finite(b))<=budget,(a,b,budget)
def norm(x):return math.hypot(*x)
def assess(rows,requests,reference,catalogue):
 assert [r['id']for r in rows]==['describe']+[r['id']for r in requests]
 descriptor=loads(rows[0]['raw'])
 assert exact(descriptor,catalogue),'descriptor differs from frozen generated catalogue'
 assert [list(m['parameters'])for m in descriptor['models']]==[list(m['parameters'])for m in catalogue['models']],'descriptor parameter order'
 assert all(type(m['schema_version'])is str for m in descriptor['models'])
 refs={p['id']:p for p in reference['paths']};worst_stress=worst_strain=worst_control=0.;points=0
 for row,req in zip(rows[1:],requests):
  echoed=row['request'];assert set(echoed)==set(req) and isinstance(row['raw'],str)
  for key in req:
   if key=='target':assert struct.pack('>d',finite(echoed[key]))==struct.pack('>d',finite(req[key]))
   else:assert exact(echoed[key],req[key])
  r=loads(row['raw'])
  assert r['ok']is True and type(r['model'])is str and r['model']==req['model'] and r['catalogue_hash']==catalogue['sha256']
  assert any(m['id']==r['model']for m in catalogue['models']),'model ID absent from frozen descriptor'
  assert r['schema_version']=='0.1'
  assert type(r['message'])is str and r['message']==''
  assert finite(r['elapsed_ms'])>=0
  assert vector(r['parameters'],len(req['parameters'].split(',')))==[float(x)for x in req['parameters'].split(',')]
  assert vector(r['initial'],6)==[float(x)for x in req['initial'].split(',')]
  assert r['integration_settings']==dict(zip(('version','norm','residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),['incremental-settings-0.1','scaled_component_max']+[float(x)for x in req['integration_settings'].split(',')]))
  for k in ['residual_tolerance','rate_tolerance']:finite(r['integration_settings'][k])
  for k in ['max_iterations','max_depth','max_substeps','max_backtracks']:assert type(r['integration_settings'][k])is int
  for k in ('protocol','steps'):assert type(r[k])is int and r[k]==req[k]
  assert 'cycles'not in r and 'target'not in r
  assert r['api_version']=='experimental-laboratory-scope-0.1'
  assert r['stress']==dict(source='state',name='sigma',measure='cauchy',scope='effective',tensor_representation='mandel',sign='compression_positive')
  assert r['pore_pressure']==(dict(quantity='change',availability='reconstructed',assumption='fixed_radial_total_stress_incompressible_fluid_and_grains') if req['protocol'] in (2,3) else dict(quantity='change',availability='unavailable',reason='not_reconstructed_for_protocol'))
  assert r['loading']['version']==req['loading_version']=='laboratory-controls-0.1'
  assert r['loading']['encoding']=='ieee754-binary64-hex'
  expected_bits=req['controls_bits_csv'].split(',')
  assert len(expected_bits)==req['steps']+1
  assert r['loading']['controls_bits']==expected_bits
  assert [struct.pack('>d',finite(x)).hex() for x in vector(r['loading']['controls'],len(expected_bits))]==expected_bits
  assert [struct.pack('>d',finite(x['control'])).hex()for x in r['points']]==expected_bits
  actual=r['points'];expected=refs[req['id']]['points'];assert len(actual)==len(expected)==req['steps']+1
  for i,(a,b)in enumerate(zip(actual,expected)):
   state=vector(a['state'],6);strain=vector(a['strain'],6);bs=[float(x)for x in b['state']];be=[float(x)for x in b['strain']]
   assert state[3:]==[0.,0.,0.] and strain[3:]==[0.,0.,0.]
   stressbudget=2e-8*max(100000.,norm(bs));strainbudget=2e-9*(1+norm(be));controlbudget=1e-12*max(1,abs(req['target']))
   es=norm([x-y for x,y in zip(state,bs)])/stressbudget;ee=norm([x-y for x,y in zip(strain,be)])/strainbudget;ec=abs(finite(a['control'])-float(b['control']))/controlbudget
   assert es<=1,('stress',req['id'],i,es)
   assert ee<=1,('strain',req['id'],i,ee)
   assert ec<=1,('control',req['id'],i,ec)
   worst_stress=max(worst_stress,es);worst_strain=max(worst_strain,ee);worst_control=max(worst_control,ec)
   p=sum(state[:3])/3;q=state[0]-.5*(state[1]+state[2]);u=100000.-.5*(state[1]+state[2])if req['protocol']in(2,3)else 0.
   for k,v in [('p',p),('q',abs(q)),('q_signed',q)]+([('u',u)] if req['protocol'] in (2,3) else []):close(a[k],v,1e-10*max(1,abs(v),norm(state)))
   if req['protocol'] not in (2,3):assert a['u'] is None
   for k,ref in [('p','mean_stress'),('q_signed','q')]+([('u','pore_pressure')] if req['protocol'] in (2,3) else []):close(a[k],float(b[ref]),2*stressbudget)
   for k in ('iterations','substeps','rejected'):assert type(a[k])is int and a[k]>=0
   assert finite(a['error'])>=0
   if i==0 or req['id']=='zero-hold':assert state==r['initial']and strain==[0.]*6
   points+=1
 return {'passed':True,'requests':len(requests),'points':points,'maximum_stress_budget_fraction':worst_stress,'maximum_strain_budget_fraction':worst_strain,'maximum_control_budget_fraction':worst_control,'scope':'finite paths only; browser/default export, rejection recovery and scientific admission separate'}
if __name__=='__main__':
 verify()
 result=assess(load(sys.argv[1]),load(HERE/'requests.json'),load(HERE/'reference/reference-p360.json'),load(HERE/'generated/models.json'))
 print(json.dumps(result,indent=2,sort_keys=True))
