"""Assess retained observations without compiled execution; retain all gate failures."""
from pathlib import Path
import json,traceback,math
from assess import assess,assess_response
s=Path(__file__).resolve().parent
reference=json.loads((s/'reference/references.json').read_text());model=json.loads((s/'frozen/models/research/terracotta-2024-fig1.json').read_text());policy=json.loads((s/'policy.json').read_text());catalogue_hash=json.loads((s/'generated/models.json').read_text())['sha256']
report={'identity':'terracotta-preparation-hold-v1','status':'passed','backends':{},'parity':{},'compiled_execution':False}
parsed={}
for role in ('native','wasm'):
 rows=json.loads((s/role/'journal.json').read_text());records=[];result={'status':'passed','metrics':[],'failures':[]}
 for row in rows:
  try:
   response=json.loads(row['raw']);record={k:row[k] for k in ('case','relative_tolerance','request')};record['response']=response;records.append(record)
   case=next(c for c in reference['cases'] if c['id']==row['case'])
   metrics=assess_response(record['request'],response,case,policy,catalogue_hash)
   result['metrics'].append({'case':row['case'],'relative_tolerance':row['relative_tolerance'],**metrics})
  except Exception as exc:result['failures'].append({'case':row.get('case'),'relative_tolerance':row.get('relative_tolerance'),'error':repr(exc),'traceback':traceback.format_exc()})
 try:assess(records,reference,model,policy,catalogue_hash)
 except Exception as exc:result['failures'].append({'scope':'complete-matrix-and-fine-policy','error':repr(exc),'traceback':traceback.format_exc()})
 # Diagnostic list of every fine component budget exceedance supplements, never replaces, the frozen assessor.
 for row in result['metrics']:
  if row['relative_tolerance']!=1e-8:continue
  for phase,channels in row['errors'].items():
   for name,values in channels.items():
    limits=policy['fine_bounds'][name]
    if not isinstance(limits,list):limits=[limits]*len(values)
    for i,(value,limit) in enumerate(zip(values,limits)):
     if value>limit:result['failures'].append({'case':row['case'],'phase':phase,'channel':name,'component':i,'error':value,'bound':limit})
 if result['failures']:result['status']='failed';report['status']='failed'
 report['backends'][role]=result;parsed[role]=records
try:
 assert len(parsed['native'])==len(parsed['wasm'])==9
 maximum=0.
 for a,b in zip(parsed['native'],parsed['wasm']):
  assert (a['case'],a['relative_tolerance'],a['request'])==(b['case'],b['relative_tolerance'],b['request'])
  x,y=a['response'],b['response'];assert x['ok'] is True and y['ok'] is True
  assert len(x['points'])==len(y['points'])==23
  for p,q in zip(x['points'],y['points']):
   for name in ('time','segment','side'):assert p[name]==q[name]
   for name in ('state','strain','strain_rate','observables'):
    assert len(p[name])==len(q[name])
    for v,w in zip(p[name],q[name]):
     if v is None or w is None:assert v==w;continue
     assert math.isfinite(v) and math.isfinite(w)
     error=abs(v-w)/max(1,abs(v),abs(w));maximum=max(maximum,error);assert error<=policy['parity_scaled_max']
 report['parity']={'status':'passed','maximum_scaled_difference':maximum,'pairs':9}
except Exception as exc:report['parity']={'status':'failed','error':repr(exc),'traceback':traceback.format_exc()};report['status']='failed'
(s/'assessment.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['status'],[(k,v['status'],len(v['failures']))for k,v in report['backends'].items()],report['parity'])
