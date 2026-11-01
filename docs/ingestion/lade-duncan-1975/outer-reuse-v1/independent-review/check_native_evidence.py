"""Replay frozen checker logic against saved responses only; no artifact invocation.
subprocess.run is replaced by an exact-command saved-response dispatcher; every
checker write is intercepted and compared with retained bytes/JSON. No root writes.
"""
from pathlib import Path
import contextlib,io,json,hashlib,runpy,subprocess,sys,types,math
D=Path(__file__).resolve().parent;B=D.parent;ROOT=D.parents[4];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.dont_write_bytecode=True;sys.path.insert(0,str(B))
f=json.loads((B/'freeze-v1.json').read_text())
for p,h in f['files'].items():assert sha(B/p)==h,p
build=json.loads((B/'native-build-receipt.json').read_text())
for p,h in build['files'].items():assert sha(ROOT/p)==h,p
jobs=[('check_candidate.py','interpreter-results.json'),('check_native_triaxial.py','native-triaxial-results.json'),('check_native_triaxial_fixed.py','native-triaxial-fixed-results.json'),('check_native_domain.py','native-domain-results.json'),('check_native_lifecycle.py','native-lifecycle-corrected-results.json'),('check_native_legacy.py','native-legacy-results.json'),('check_domain_supplement.py','native-supplement-results.json')]
rows_total=0;raws=0;outcomes=[]
for script,reportname in jobs:
 report=json.loads((B/reportname).read_text());assert report['passed'];rows=report.get('requests',[]);payloads=[]
 for row in rows:
  assert row['command'][0]==str(ROOT/'.local/lade-outer-reuse-v1/native-build/atlas_lade_domain_candidate')
  if 'raw_path' in row:
   p=ROOT/row['raw_path'];assert sha(p)==row['raw_sha256'];text=p.read_text();raws+=1
  else:text=json.dumps(row['response'])
  payloads.append(text)
 index=0;writes=0;original_run=subprocess.run;original_write=Path.write_text;original_mkdir=Path.mkdir
 def saved_run(cmd,*args,**kwargs):
  global index
  assert index<len(rows),(script,'extra request',cmd)
  assert cmd==rows[index]['command'],(script,index,'command mismatch',cmd,rows[index]['command'])
  assert kwargs.get('timeout')==120,(script,'deadline mismatch')
  result=types.SimpleNamespace(stdout=payloads[index],stderr='',returncode=rows[index]['returncode']);index+=1;return result
 def intercepted_write(path,text,*args,**kwargs):
  global writes
  assert path.exists(),('unexpected new write',path)
  existing=path.read_text()
  if path==B/reportname:assert json.loads(text)==json.loads(existing),(script,'recomputed aggregate mismatch')
  else:assert text==existing,(script,'raw byte mismatch',path)
  writes+=1;return len(text)
 def existing_mkdir(path,*args,**kwargs):assert path.is_dir(),('unexpected directory',path)
 subprocess.run=saved_run;Path.write_text=intercepted_write;Path.mkdir=existing_mkdir
 try:
  with contextlib.redirect_stdout(io.StringIO()):
   try:runpy.run_path(str(B/script),run_name='__main__')
   except SystemExit as e:assert e.code in (0,None),(script,'gate failure',e.code)
 finally:subprocess.run=original_run;Path.write_text=original_write;Path.mkdir=original_mkdir
 assert index==len(rows),(script,'unconsumed requests',index,len(rows));assert writes>=1
 outcomes.append({'checker':script,'report':reportname,'saved_requests':len(rows),'checks':len(report.get('checks',report.get('cases',[]))),'all_recomputed_report_fields_identical':True});rows_total+=len(rows)
# Independently recompute every triaxial point-bound and joint trend, apart from script replay.
reference_report=json.loads((B/'triaxial-reference-results.json').read_text());assert reference_report['passed'] and len(reference_report['cases'])==8 and all(x['passed'] for x in reference_report['cases']);assert sha(B.parent/'delivery-v1/supplied-original-v2/candidate-v2/triaxial_reference.py')==reference_report['reference_script_sha256'];refs=reference_report['cases'];policy=json.loads((B/'triaxial-policy.json').read_text());error_rows=[]
for name in ['native-triaxial-results.json','native-triaxial-fixed-results.json']:
 report=json.loads((B/name).read_text())
 for row in report['requests']:
  r=json.loads((ROOT/row['raw_path']).read_text());assert r['ok'] and len(r['points'])==row['steps']+1
  for point in r['points']:assert len(point['state'])==8 and len(point['strain'])==6 and all(math.isfinite(x) for x in point['state']+point['strain'])
  reference=next(x['reference'] for x in refs if x['set']==row['set'] and x['reference']['axial_strain']==row['target']);last=r['points'][-1]
  err={'relative_axial_stress':abs(last['state'][0]-reference['axial_stress'])/reference['axial_stress'],'absolute_radial_strain':abs(last['strain'][1]-reference['radial_strain']),'relative_work_using_1Pa_floor':abs(last['state'][7]-reference['wp'])/max(1,abs(reference['wp']))}
  assert err==row['errors'] and all(v<=policy['native_final_reference_bounds'][k] for k,v in err.items())
  error_rows.append({'report':name,'set':row['set'],'target':row['target'],'steps':row['steps'],'errors':err})
 for case in report['refinement']:
  if name=='native-triaxial-results.json':assert case['stress_error_decreases']
# Independent complete domain transaction checks across primary and all recovery calls.
failed=0;success=0
for name in ['native-domain-results.json','native-supplement-results.json']:
 for row in json.loads((B/name).read_text())['requests']:
  cmd=row['command'];parent=list(map(float,cmd[cmd.index('--initial')+1].split(',')));de=list(map(float,cmd[cmd.index('--strain')+1].split(',')));r=json.loads((ROOT/row['raw_path']).read_text());assert len(r['state'])==8 and all(math.isfinite(x) for x in r['state'])
  if not r['ok']:assert r['state']==parent;failed+=1
  else:
   success+=1
   if all(x==0 for x in de):assert r['state']==parent
# Source private original stays exact. Do not read/redistribute source bytes here.
source=ROOT/'.local/private-sources/lade-duncan-1975/original-1975-supplied.pdf';assert sha(source)=='bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5'
# Verify retained historical checkpoint closures, including private failed responses.
prior=[]
for name in ['domain-control-v1','midpoint-control-v1','warmstart-control-v1','derivative-tail-v1','finite-tail-v1','hierarchical-seeds-v1']:
 base=B.parent/name;manifest=base/'checkpoint-manifest.json';checkpoint=json.loads(manifest.read_text());count=0
 for key in ['files','private_raw_responses','private','private_raw']:
  if key not in checkpoint:continue
  value=checkpoint[key]
  if isinstance(value,list):entries=value
  elif 'path' in value and 'sha256' in value:entries=[value]
  else:entries=[{'path':a,'sha256':h} for a,h in value.items()]
  for row in entries:
   path=Path(row['path']);target=ROOT/path if str(path).startswith(('docs/','.local/')) else base/path
   assert sha(target)==row['sha256'],('historical drift',name,target);count+=1
 prior.append({'checkpoint':name,'sha256':sha(manifest),'verified_files':count})
mirror=0
for p in (B/'proposed-native-source').rglob('*'):
 if p.is_file():assert p.read_bytes()==(ROOT/'.local/lade-outer-reuse-v1/native-source'/p.relative_to(B/'proposed-native-source')).read_bytes();mirror+=1
out={'id':'REVIEW-lade-outer-fullnative-saved-v1','retained_prior_checkpoints':prior,'local_native_source_mirror_files':mirror,'original_frozen_files':len(f['files']),'build_receipt_files':len(build['files']),'replayed_saved_requests':rows_total,'hashed_separate_raw_files':raws,'checker_replays':outcomes,'independently_recomputed_triaxial_error_rows':error_rows,'domain_and_recovery_successful_calls':success,'domain_and_recovery_failed_calls_exact_rollback':failed,'source_original_hash_verified':True,'compiled_execution':False,'material_advance':False,'Wasm_qualified':False,'E5_approval':False}
(D/'native-evidence-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'saved_requests':rows_total,'raws':raws,'replayed_checkers':len(outcomes),'domain_success':success,'domain_failed_exactrollback':failed,'passed':True}))
