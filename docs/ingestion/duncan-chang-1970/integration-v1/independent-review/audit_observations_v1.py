"""Saved integration observations only; no compiled code is imported/executed."""
from pathlib import Path
import json,hashlib,struct,re,math
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def same(a,b):
 if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):return struct.pack('>d',float(a))==struct.pack('>d',float(b))
 if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b
freeze=read(B/'freeze.json');catalogue=freeze['catalogue_hash'];policy=read(ROOT/'catalogue/laboratory-package-policy.json')
native=read(B/'native-laboratory.json');wasm=read(B/'wasm-examples-replay-v2.json')
assert native['status']==wasm['status']=='passed' and native['catalogue_hash']==wasm['catalogue_hash']==catalogue
assert len(native['ordinary'])==14
for row in native['ordinary']:
 r=row['result'];declared=next((x for x in policy['declared_failures'] if x['model']==row['id']),None)
 assert r['ok']==(declared is None) and len(r['points'])==(101 if declared is None else declared['committed_points'])
 if declared:assert r['message']==declared['message']
comparisons=0
for backend,current,calls in [('native',native['presets'],[native['calls'][-3]['raw'],native['calls'][-1]['raw']]),('wasm',wasm['examples'][:2],[wasm['calls'][1]['raw'],wasm['calls'][3]['raw']])]:
 e4=read(B.parent/'material-v1/execution-v2'/f'{backend}-results.json')
 for row,raw in zip(current,calls):
  old=next(x for x in e4['presets'] if x['id']==row['id']);a=json.loads(raw);b=json.loads(old['call']['stdout'])
  assert a['ok'] and b['ok'] and len(a['points'])==len(b['points'])==129
  for x,y in zip(a['points'],b['points']):
   for key in ['state','strain','control','p','q','q_signed','error']:
    assert same(x[key],y[key]),(backend,row['id'],key)
    comparisons+=1
index=read(ROOT/'catalogue/laboratory-examples.json')
fresh=[]
for row in index['examples']:
 if row['id'].startswith('duncan-') or row['id']=='gis2024-small-drained':
  doc=read(ROOT/row['document_path']);assert sha(ROOT/row['document_path'])==row['document_sha256']
  assert doc['catalogue_hash']==catalogue and doc['result']['ok']
  result=next(x['result'] for x in wasm['examples'] if x['id']==('dense-source-drained' if row['id'].startswith('duncan-dense') else 'loose-source-drained' if row['id'].startswith('duncan-loose') else row['id']))
  assert doc['result']==result;fresh.append(row['id'])
assert len(fresh)==3
scoped=read(B/'scoped-parity.json');assert scoped['status']=='passed' and len(scoped['cases'])==36
physical={'state','strain','p','q','q_signed','u','error'};count=0;worst=0
def compare(a,b,path='result',floating=False):
 global count,worst
 if isinstance(b,(int,float)) and not isinstance(b,bool):
  assert isinstance(a,(int,float)) and math.isfinite(a) and math.isfinite(b)
  if floating:
   fraction=abs(a-b)/(1e-10*max(1,abs(a),abs(b)));assert fraction<=1;count+=1;worst=max(worst,fraction)
  else:assert a==b,(path,a,b)
 elif isinstance(b,list):
  assert isinstance(a,list) and len(a)==len(b)
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]',floating)
 elif isinstance(b,dict):
  assert a.keys()==b.keys()
  for k in b:
   if k!='elapsed_ms':compare(a[k],b[k],path+'.'+k,k in physical if re.search(r'\.points\[\d+\]$',path) else floating)
 else:assert a==b,path
for row in scoped['cases']:compare(row['native'],row['wasm'])
assert count==scoped['compared_physical_scalars']==43201 and worst==scoped['maximum_budget_fraction']
receipt=read(B/'native-receipt.json');assert receipt['freeze_sha256']==sha(B/'freeze.json')
for manifest in [receipt,read(B/'wasm-artifacts.json')]:
 assert manifest['freeze_sha256']==sha(B/'freeze.json')
 for path,h in manifest['artifacts'].items():assert sha(ROOT/path)==h
app=read(ROOT/'catalogue/applicability/kfs-development-v1.json');old=read(ROOT/'catalogue/source-snapshots/65cb89a4a43e1b7df0d912aab8d7dd4e7c3bd41d1ebf177f7d936dd93f2e89f5/catalogue/applicability/kfs-development-v1.json')
assert app['rows'][:-1]==old['rows'] and app['rows'][-1]['assessment']=='not_assessed' and app['rows'][-1]['scientific_eligibility']=='undetermined'
browser=read(B/'browser-loading.json');last=browser['pairs'][-1];assert last['name']=='legacy/duncan-chang-1970-endpoint-average/1'
assert browser['status']=='running' and last['native']['ok'] and last['wasm']['ok']
assert last['native']['points'][23]['iterations']==5 and last['wasm']['points'][23]['iterations']==4
print(json.dumps({'identity':'independent-duncan-integration-observation-audit-v1','bounded_success_checks_pass':True,'native_ordinary_cases_checked':14,'exact_e4_source_preset_histories_checked':4,'exact_point_field_comparisons':comparisons,'fresh14catalogue_documents_checked':fresh,'scoped_cases_checked':36,'scoped_physical_scalars':count,'scoped_maximum_budget_fraction':worst,'durable_artifact_hashes_verified':6,'applicability_old_rows_unchanged':13,'new_applicability_assessment':'not_assessed/undetermined','full_e6_e7_acceptance':False,'browser_blocker':{'name':last['name'],'saved_rows':len(browser['pairs']),'status_field':'running means interrupted; not a pass','point':23,'iterations_native':5,'iterations_wasm':4,'later_browser_requests_not_qualified':True},'compiled_calls':0},indent=2))
