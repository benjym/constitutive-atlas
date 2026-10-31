"""Apply corrected envelope to hash-pinned saved observations, with no candidate execution."""
from pathlib import Path
import json,hashlib,sys,traceback
from assess_paths import load,assess
from assess_parity import assess as parity
s=Path(__file__).resolve().parent;parent=Path(sys.argv[1]).resolve()
assert not(s/'assessment.json').exists()
manifest=load(s/'manifest.json')
for name,pin in manifest.items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
identity=load(s/'correction.json');assert hashlib.sha256((parent/'manifest.json').read_bytes()).hexdigest()==identity['parent_manifest_sha256']
# Verify all original prospective inputs, not just the reused journal hashes.
for name,pin in load(parent/'manifest.json').items():assert hashlib.sha256((parent/name).read_bytes()).hexdigest()==pin,name
requests=load(s/'requests.json');reference=load(s/'reference/reference-p360.json');catalogue=load(s/'generated/models.json');journals={};results={}
for b in ('native','wasm'):
 path=parent/b/'journal.json';assert hashlib.sha256(path.read_bytes()).hexdigest()==identity['parent_journal_sha256'][b]
 journals[b]=load(path)
 try:results[b]=assess(journals[b],requests,reference,catalogue)
 except Exception as exc:
  results[b]={'passed':False,'error':type(exc).__name__+':'+str(exc)};(s/(b+'-assessment.stderr.txt')).write_text(traceback.format_exc())
if all(v['passed']for v in results.values()):
 try:results['parity']=parity(journals['native'],journals['wasm'],requests)
 except Exception as exc:
  results['parity']={'passed':False,'error':type(exc).__name__+':'+str(exc)};(s/'parity-assessment.stderr.txt').write_text(traceback.format_exc())
else:results['parity']={'passed':False,'not_run':'source gates failed'}
output={'identity':'mc-preview-envelope-assessment-v2','passed':all(x['passed']for x in results.values()),'new_candidate_calls':0,'new_builds':0,'numeric_policy_changed':False,'results':results}
(s/'assessment.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n');print(json.dumps(output,indent=2));raise SystemExit(0 if output['passed']else 1)
