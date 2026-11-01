"""Saved-only build/helper/fidelity audit. Never invokes an artifact."""
from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;B=D.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.dont_write_bytecode=True;sys.path.insert(0,str(B));from fidelity import parse_response,same_response
build=json.loads((B/'native-build-receipt.json').read_text())
for p,h in build['files'].items():assert sha(Path(p))==h,p
assert build['parallel']==1
helpers={}
for name,count in [('outer-results.json',157),('hierarchical-results.json',33),('tail-results.json',10375),('seed-results.json',49),('metric-results.json',16)]:
 r=json.loads((B/name).read_text());assert r['checks']==count and r['failures']==0 and r['passed'];helpers[name]=count
r=json.loads((B/'outer-results.json').read_text());assert r['actual_reuses']==r['avoided_integrations']==12
f=json.loads((B/'fidelity-results.json').read_text());p=json.loads((B/'FIDELITY_POLICY.json').read_text());assert f['passed'] and len(f['records'])==6 and len(p['cases'])==3
for i,case in enumerate(p['cases']):
 pair=f['records'][2*i:2*i+2];responses=[]
 for row,kind in zip(pair,['baseline','reuse']):
  assert row['name']==case['name'] and row['kind']==kind and row['returncode']==0 and not row['timeout'];assert row['command'][1:]==case['command'][1:];assert sha(Path(row['command'][0]))==row['exe_sha256']
  for stream in ['stdout','stderr']:assert sha(Path(row[stream]['path']))==row[stream]['sha256']
  response=parse_response(Path(row['stdout']['path']).read_bytes());assert response['ok'] is True;responses.append(response)
 assert same_response(*responses) and pair[1]['pair_exact'] is True
out={'id':'REVIEW-lade-outer-reuse-saved-prerequisites-v1','verified_build_receipt_files':len(build['files']),'helper_checks':helpers,'actual_avoided_integrations':12,'independently_reparsed_exact_response_pairs':3,'raw_streams_verified':12,'compiled_execution':False,'material_advance':False,'hardcase_adjudicated':False}
(D/'saved-prerequisite-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
