"""Independent read-only hash and exhaustive receipt replay in supplied draft context."""
from pathlib import Path
import json,hashlib,gzip,re,sys,runpy
OUT=Path(__file__).resolve().parent;R=OUT.parents[3];P=OUT.parent/'current-integration-v3-preparation-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'MANIFEST.json')=='9047674e208d1db45f620030de6e0a479c9521e9dc2180abd3461e1127340129'
assert sha(P/'COMPOSITION.json')=='c334be60a6c093e6472908430ffa9280f284b90edfcf744b232aec44851b730c'
manifest=json.loads((P/'MANIFEST.json').read_text())
for n,h in manifest['files'].items():assert sha(P/n)==h,n
check=runpy.run_path(str(P/'check_preparation.py'))['main']();assert check['pass']
context=P/'consumer-context';inv=json.loads(gzip.decompress((P/'consumer-context-inventory-final-v3.json.gz').read_bytes()))
actual={p.relative_to(context).as_posix():sha(p) for p in context.rglob('*') if p.is_file() and '__pycache__' not in p.parts};assert actual==inv
proof=json.loads(gzip.decompress((P/'PROOF.json.gz').read_bytes()));composition=json.loads((P/'COMPOSITION.json').read_text())
for n,h in composition['candidate_files'].items():assert sha(P/'candidates'/n)==sha(context/n)==h,n
for n,h in composition['preservation_files'].items():assert sha(P/'preservation-candidates'/n)==sha(context/n)==h,n
valid=lambda h:isinstance(h,str) and bool(re.fullmatch('[0-9a-f]{64}',h))
def pairs(v):
 if isinstance(v,dict):
  for k,h in v.items():
   if valid(h) and ('/' in k or '.' in k or (R/k).is_file()):yield k,h
  if isinstance(v.get('path'),str):
   for k in ['sha256','hash']:
    if valid(v.get(k)):yield v['path'],v[k]
  for z in v.values():yield from pairs(z)
 elif isinstance(v,list):
  for z in v:yield from pairs(z)
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
def outcome(root,doc,path,h):
 try:
  value=checked_receipt(root,doc,path,h);return {'ok':True,'sha256':sha(value),'resolved':value.relative_to(root).as_posix()}
 except Exception as e:return {'ok':False,'error_type':type(e).__name__,'error':str(e).replace(str(root),'<ROOT>')}
record={(e['document'],e['original_path'],e['sha256']):e for e in proof['edges']};assert len(record)==3173
passed=failed=redirected=0
for doc,h in proof['documents'].items():
 assert sha(R/doc)==h
 actual=set(pairs(json.loads((R/doc).read_text())));expected={(p,s) for d,p,s in record if d==doc};assert actual==expected,doc
 for path,digest in actual:
  e=record[(doc,path,digest)];a=outcome(R,doc,path,digest);b=outcome(context,doc,path,digest);assert a==e['before'] and b==e['after'],(doc,path)
  if a['ok']:
   assert b['ok'] and a['sha256']==b['sha256'];passed+=1;redirected+=a['resolved']!=b['resolved']
  else:assert a==b;failed+=1
for m in proof['maps']:
 live=R/m['path'];assert (sha(live) if live.exists() else None)==m['before_sha256']
 if m['changed']:
  new=json.loads((P/'preservation-candidates'/m['path']).read_text())
  if live.exists():
   old=json.loads(live.read_text());assert all(e in new['entries'] for e in old['entries']);assert all(new['documents'][n]==h for n,h in old['documents'].items())
  for sib in live.parent.glob('*.json'):
   if sib.name!='source-archive-map.json':assert new['documents'][sib.relative_to(R).as_posix()]==sha(sib)
  for entry in new['entries']:assert sha(context/entry['archived_path'])==entry['sha256']
assert (passed,failed,redirected)==(469,2704,9)
results={'manifest_files':len(manifest['files']),'candidate_files':len(composition['candidate_files']),'proof_pairs':len(record),'documents':len(proof['documents']),'contexts':len(proof['maps']),'before_pass':passed,'prior_failures_retained':failed,'redirected':redirected,'newly_broken':0,'context_files':len(inv),'source_checks':check,'compiled_calls':0,'material_calls':0}
(OUT/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
