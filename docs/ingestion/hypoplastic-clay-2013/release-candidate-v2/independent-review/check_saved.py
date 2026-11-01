"""Metadata-only source candidate integrity replay; no compiled/material calls."""
from pathlib import Path
from collections import Counter
import json,hashlib,subprocess,sys,tempfile,sqlite3
HERE=Path(__file__).resolve().parent;PACKET=HERE.parent;ROOT=PACKET.parents[3]
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
def main():
 for n,h in json.loads((HERE/'input-freeze.json').read_text()).items():
  if sha(Path(n))!=h:raise RuntimeError('changed frozen review input '+n)
 plan=json.loads((PACKET/'PLAN.json').read_text());c=Path(plan['candidate'])
 def git(*args):return subprocess.check_output(['git',*args],cwd=c)
 if git('rev-parse','HEAD').decode().strip()!=plan['base']:raise RuntimeError('candidate base')
 if git('diff','--cached','--name-only'):raise RuntimeError('nonempty index')
 changed=set(filter(None,git('diff','--name-only','-z').decode().split('\0')))
 added=set(filter(None,git('ls-files','--others','--exclude-standard','-z').decode().split('\0')))
 if changed|added!={r['path'] for r in plan['writes']}:raise RuntimeError('candidate write whitelist')
 for row in plan['writes']:
  q=c/row['path']
  if sha(q)!=row['after_sha256'] or q.stat().st_size!=row['bytes'] or q.read_bytes()!=(ROOT/row['path']).read_bytes():raise RuntimeError('after bytes '+row['path'])
  proc=subprocess.run(['git','show','HEAD:'+row['path']],cwd=c,capture_output=True)
  if (hashlib.sha256(proc.stdout).hexdigest() if proc.returncode==0 else None)!=row['before_sha256']:raise RuntimeError('before bytes '+row['path'])
 for n,h in plan['preserved_base_inputs'].items():
  if sha(c/n)!=h:raise RuntimeError('base repair changed '+n)
 old=json.loads(git('show','HEAD:catalogue/approved-models.json'));new=json.loads((c/'catalogue/approved-models.json').read_text())
 if len(old['models'])!=17 or len(new['models'])!=20 or new!=dict(old,models=old['models']+new['models'][17:]):raise RuntimeError('nonadditive registry')
 for name in plan['accepted_reviews']:
  proc=subprocess.run([sys.executable,'-B','-m','atlas.agent_review',name,'--for-approval'],cwd=c,capture_output=True,text=True)
  if proc.returncode:raise RuntimeError('review metadata '+proc.stderr)
 def tables(path):
  with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as db:
   if db.execute('pragma integrity_check').fetchall()!=[('ok',)] or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('SQL integrity')
   return {n:Counter(db.execute('select * from '+n).fetchall()) for (n,) in db.execute("select name from sqlite_master where type='table'")}
 with tempfile.TemporaryDirectory(prefix='candidate-metadata-review-') as td:
  db=Path(td)/'fresh.sqlite';code='from atlas.research import export_database; export_database('+repr(str(db))+')'
  proc=subprocess.run([sys.executable,'-B','-c',code],cwd=c,text=True,capture_output=True)
  if proc.returncode:raise RuntimeError(proc.stderr)
  actual=tables(db)
  if actual!=tables(ROOT/'.local/clay2013-current-delivery-v1/site/atlas.sqlite'):raise RuntimeError('full SQL multiset difference')
 freeze=json.loads((ROOT/'docs/ingestion/hypoplastic-clay-2013/current-delivery-v1/EXECUTION_SOURCE_FREEZE.json').read_text())['files']
 same=[];different=[];missing=[];absolute=[]
 for n,h in freeze.items():
  q=Path(n)
  if q.is_absolute():
   if sha(q)!=h:raise RuntimeError('absolute qualified prerequisite changed '+n)
   absolute.append(n);continue
  q=c/n
  if not q.exists():missing.append(n)
  elif sha(q)!=h:different.append(n)
  else:same.append(n)
 expected=json.loads((PACKET/'CHECKS.json').read_text())['source_candidate']
 if same.__len__()!=expected['matching_tested_relative_inputs'] or set(different)!=set(expected['preserved_release_repair_differences']) or set(missing)!=set(expected['missing_historical_packet_only_inputs']):raise RuntimeError('source closure differences')
 compat=json.loads((PACKET/'DUNCAN_BASE_COMPATIBILITY.json').read_text())
 if sha(PACKET/'PLAN.json')!=compat['source_candidate_plan_sha256']:raise RuntimeError('compatibility plan identity')
 for row in compat['rows']:
  proc=subprocess.run(['git','show',compat['revision']+':'+row['path']],cwd=compat['repository'],capture_output=True)
  h=hashlib.sha256(proc.stdout).hexdigest() if proc.returncode==0 else None
  if h!=row['expected_before_sha256'] or h!=row['observed_before_sha256']:raise RuntimeError('pinned Duncan precondition '+row['path'])
 return {'status':'PASS','candidate_base':plan['base'],'exact_writes':len(plan['writes']),'index_empty':True,'review_validators':3,'registry_before':17,'registry_after':20,'database_table_multiset_rows':{n:sum(v.values()) for n,v in actual.items()},'matching_tested_relative_inputs':len(same),'unchanged_absolute_prerequisites':len(absolute),'preserved_base_differences':different,'missing_historical_packet_only_inputs':missing,'pinned_Duncan_revision':compat['revision'],'Duncan_write_preconditions_match':len(compat['rows']),'release_ready':False,'reviewer_compiled_calls':0,'reviewer_material_calls':0,'remote_actions':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
