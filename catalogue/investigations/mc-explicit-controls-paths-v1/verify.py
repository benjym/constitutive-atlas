"""Saved-evidence replay only; never execute candidate artifacts."""
from pathlib import Path
import json,hashlib,sys
from assess_paths import assess as paths
from assess_parity import assess as parity
s=Path(__file__).resolve().parent
read=lambda p:json.loads((s/p).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read('manifest.json').items():assert sha(s/n)==h,n
assert read('prospective-freeze.json')['manifest_sha256']==sha(s/'manifest.json')
for n,h in read('evidence-manifest.json').items():assert sha(s/n)==h,n
requests=read('requests.json');invalid=read('rejection-requests.json');results={}
for role in ['native','wasm']:
 receipt=read(role+'/receipt.json');assert receipt['completed'] is True
 assert receipt['manifest_sha256']==sha(s/'manifest.json')
 assert all(c['exit_code']==0 for c in receipt['commands'])
 assert receipt['journal_sha256']==sha(s/role/'journal.json')
 assert receipt['rejections_sha256']==sha(s/role/'rejections.json')
 rows=read(role+'/journal.json');results[role]=paths(rows,requests,read('reference/reference-p360.json'),read('generated/models.json'))
 recovery=json.loads(next(r['raw']for r in rows if r['id']==invalid['recovery_request_id']));recovery.pop('elapsed_ms',None)
 failures=read(role+'/rejections.json');assert len(failures)==12
 assert [r['request']for r in failures]==invalid['cases']
 for row in failures:
  fail=json.loads(row['raw']);assert fail['ok'] is False
  assert 'points'not in fail or isinstance(fail['points'],list)and len(fail['points'])==0
  recovered=json.loads(row['recovery_raw']);recovered.pop('elapsed_ms',None);assert recovered==recovery
results['parity']=parity(read('native/journal.json'),read('wasm/journal.json'),requests)
old=read('legacy-regressions.json');assert old['passed']is True and old['backend_runs']==len(old['records'])==90
assert len(old['baselineBindings'])==7
keys=set()
for row in old['records']:
 keys.add((row['model'],row['protocol'],row['backend']))
 a=json.loads(row['old_raw']);b=json.loads(row['new_raw']);assert a['ok']is True and b['ok']is True
 for key in ['elapsed_ms','catalogue_hash']:a.pop(key,None);b.pop(key,None)
 assert a==b
assert len(keys)==90
for n in ['parity','legacy-regressions','generic-regressions']:assert read(n+'-command.json')['exit_code']==0
if '--artifacts' in sys.argv:
 for role in ['native','wasm']:
  for a in read(role+'/receipt.json')['artifacts'].values():assert sha(Path(a['path']))==a['sha256']
print(json.dumps({'passed':True,'path_assessments':results,'invalid_recovery_pairs_per_backend':12,'unchanged_legacy_runs':90,'candidate_calls':0,'local_artifacts_checked':'--artifacts'in sys.argv},indent=2))
