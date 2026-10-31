"""New fine-resolution verdict; original matrix/outcome stays immutable."""
from pathlib import Path
import sys,json,math,traceback
s=Path(__file__).resolve().parent;base=s.parent/'terracotta-preparation-hold-v1';sys.path.insert(0,str(base))
from assess import assess_response
reference=json.loads((base/'reference/references.json').read_text());policy=json.loads((base/'policy.json').read_text());catalogue_hash=json.loads((base/'generated/models.json').read_text())['sha256'];expected=json.loads((s/'requests.json').read_text())['records']
report={'identity':'terracotta-preparation-hold-refinement-v2','status':'passed','parent_outcome':'failed','parent_records_per_backend':9,'backends':{},'parity':{},'compiled_execution':False};parsed={}
for role in ('native','wasm'):
 rows=json.loads((s/role/'journal.json').read_text());old=json.loads((base/role/'journal.json').read_text());assert len(old)==9
 result={'status':'passed','metrics':[],'failures':[]};records=[]
 assert len(rows)==len(expected)==3
 for row,wanted in zip(rows,expected):
  try:
   for key in ('case','relative_tolerance','request'):assert row[key]==wanted[key]
   oldfine=next(r for r in old if r['case']==row['case'] and r['relative_tolerance']==1e-8)
   q=json.loads(json.dumps(oldfine['request']));q['solver']['relative_tolerance']=2.5e-9;assert row['request']==q
   response=json.loads(row['raw']);records.append(response);case=next(c for c in reference['cases'] if c['id']==row['case'])
   metric=assess_response(row['request'],response,case,policy,catalogue_hash)
   result['metrics'].append({'case':row['case'],'relative_tolerance':row['relative_tolerance'],**metric})
   coarse=next(r for r in old if r['case']==row['case'] and r['relative_tolerance']==1e-4)
   previous=assess_response(coarse['request'],json.loads(coarse['raw']),case,policy,catalogue_hash)
   for phase,channels in metric['errors'].items():
    for name,values in channels.items():
     limits=policy['fine_bounds'][name]
     if not isinstance(limits,list):limits=[limits]*len(values)
     for i,(value,limit) in enumerate(zip(values,limits)):
      if value>limit:result['failures'].append({'case':row['case'],'phase':phase,'channel':name,'component':i,'error':value,'bound':limit})
      assert value<=previous['errors'][phase][name][i]+1e-12*metric['reference_magnitudes'][phase][name][i]
  except Exception as exc:result['failures'].append({'case':row['case'],'error':repr(exc),'traceback':traceback.format_exc()})
 if result['failures']:result['status']='failed';report['status']='failed'
 report['backends'][role]=result;parsed[role]=records
try:
 assert len(parsed['native'])==len(parsed['wasm'])==3;maximum=0.
 for x,y in zip(parsed['native'],parsed['wasm']):
  assert x['ok'] is True and y['ok'] is True and len(x['points'])==len(y['points'])==23
  for p,q in zip(x['points'],y['points']):
   for name in ('time','segment','side'):assert p[name]==q[name]
   for name in ('state','strain','strain_rate','observables'):
    assert len(p[name])==len(q[name])
    for v,w in zip(p[name],q[name]):
     if v is None or w is None:assert v==w;continue
     assert math.isfinite(v) and math.isfinite(w);error=abs(v-w)/max(1,abs(v),abs(w));maximum=max(maximum,error);assert error<=policy['parity_scaled_max']
 report['parity']={'status':'passed','maximum_scaled_difference':maximum,'new_pairs':3}
except Exception as exc:report['parity']={'status':'failed','error':repr(exc),'traceback':traceback.format_exc()};report['status']='failed'
(s/'assessment.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['status'],[(k,len(v['failures']))for k,v in report['backends'].items()],report['parity'])
