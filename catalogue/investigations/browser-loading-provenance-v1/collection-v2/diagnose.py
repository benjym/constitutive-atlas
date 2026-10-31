from pathlib import Path
import json
s=Path(__file__).resolve().parents[1];data=json.loads((s/'collection-v2/backend-results.json').read_text());errors=[];checks=0
for row in data['pairs']:
 tol=1e-7 if row['name'].startswith('legacy/') else 1e-10
 def visit(a,b,path='result'):
  global checks
  if type(b)in(int,float):
   checks+=1
   if abs(a-b)>tol*max(1,abs(a),abs(b)):errors.append({'case':row['name'],'path':path,'native':a,'wasm':b,'budget':tol*max(1,abs(a),abs(b))})
  elif isinstance(b,list):
   assert len(a)==len(b)
   for i,(x,y)in enumerate(zip(a,b)):visit(x,y,path+f'[{i}]')
  elif isinstance(b,dict):
   assert set(a)==set(b)
   for k,v in b.items():
    if k!='elapsed_ms':visit(a[k],v,path+'.'+k)
  else:assert a==b,(path,a,b)
 visit(row['native'],row['wasm'])
exact=[]
for e in errors:
 assert e['path'].endswith('.q'),e
 row=next(r for r in data['pairs']if r['name']==e['case']);i=int(e['path'].split('points[')[1].split(']')[0]);states={}
 for role in ['native','wasm']:
  v=row[role]['points'][i]['state'][:6];assert v[0]==v[1]==v[2]and v[3:]==[0,0,0]
  states[role]={'mandel_hex':[float(x).hex()for x in v],'exact_q':0,'reported_q':row[role]['points'][i]['q']}
 exact.append({**e,'states':states})
report={'identity':'browser-loading-isotropic-q-saved-diagnosis-v1','overall_status':'failed','pairs_collected':len(data['pairs']),'numeric_comparisons':checks,'failed_scalars':errors,'exact_isotropic_proofs':exact,'original_gate_unchanged':True,'candidate_calls':0,'scope':'saved-output diagnosis; no implemented fix or new acceptance bound'}
(s/'collection-v2/diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['failed_scalars','exact_isotropic_proofs']},indent=2));print('failed scalars',len(errors))
