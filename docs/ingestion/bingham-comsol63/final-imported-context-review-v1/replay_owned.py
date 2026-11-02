"""Independent exact receipt replay of sealed imported proposal; never mutates source/context."""
from pathlib import Path
import ast,collections,gzip,hashlib,json,re,sys,time
from functools import lru_cache
from types import SimpleNamespace
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];P=OUT.with_name('final-imported-context-v1');CONTEXT=Path('/private/tmp/atlas-bingham-final-context-v1')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(sys.argv)==2,'Exact sealed manifest SHA required'
assert h(P/'MANIFEST.json')==sys.argv[1]
manifest=json.loads((P/'MANIFEST.json').read_text())
for n,v in manifest['files'].items():assert h(P/n)==(v if isinstance(v,str) else v['sha256']),n
composition=json.loads((P/'SEALED-COMPOSITION.json').read_text());preservation=json.loads((P/'SEALED-PRESERVATION.json').read_text());proof=json.loads(gzip.decompress((P/'SEALED-REPLAY.json.gz').read_bytes()));siblings=json.loads((P/'SIBLINGS.json').read_text())
for n,v in composition['selected_source_and_admission_files'].items():
 source=Path(composition['selected_file_sources'][n]);assert h(source)==v,n
 assert h(CONTEXT/n)==composition['preservation_files'].get(n,v),n
for n,v in composition['preservation_files'].items():assert h(P/'preservation-candidates'/n)==h(CONTEXT/n)==v,n
for n,m in preservation['maps'].items():
 old=ROOT/n;new=json.loads((CONTEXT/n).read_text());assert (h(old) if old.exists() else None)==m['before_sha256'],n
 if old.exists():
  b=json.loads(old.read_text());assert all(x in new['entries'] for x in b['entries']);assert all(new['documents'][k]==v for k,v in b['documents'].items())
 for q in (CONTEXT/n).parent.glob('*.json'):
  if q.name!='source-archive-map.json':assert new['documents'][q.relative_to(CONTEXT).as_posix()]==h(q),str(q)
 for entry in new['entries']:
  assert entry['archived_path']=='catalogue/source-snapshots/'+entry['sha256']+'/'+entry['original_path']
  assert h(CONTEXT/entry['archived_path'])==entry['sha256']
valid=lambda v:isinstance(v,str) and bool(re.fullmatch('[0-9a-f]{64}',v))
def pairs(v):
 if isinstance(v,dict):
  for k,s in v.items():
   if valid(s) and ('/' in k or '.' in k or (ROOT/k).is_file()):yield k,s
  if isinstance(v.get('path'),str):
   for k in ['sha256','hash']:
    if valid(v.get(k)):yield v['path'],v[k]
  for x in v.values():yield from pairs(x)
 elif isinstance(v,list):
  for x in v:yield from pairs(x)
for parent in siblings['parent_contexts']:
 actual={q.relative_to(ROOT).as_posix():h(q) for q in (ROOT/parent).glob('*.json') if q.name!='source-archive-map.json'}
 expected={n:v for n,v in siblings['documents'].items() if Path(n).parent.as_posix()==parent};assert actual==expected,parent
record={(e['document'],e['original_path'],e['sha256']):e for e in proof['edges']};assert len(record)==len(proof['edges'])
for n,v in siblings['documents'].items():
 assert h(ROOT/n)==v,n
 if n in siblings.get('malformed_json_siblings',{}):assert (ROOT/n).read_bytes()==(CONTEXT/n).read_bytes();continue
 expected={(path,s) for d,path,s in record if d==n};actual=set(pairs(json.loads((ROOT/n).read_text())));assert actual==expected,(n,len(actual),len(expected))
sys.path.insert(0,str(ROOT));import atlas.evidence as evidence
# Parsed objects are read-only in this unmodified resolver; hashes/outcomes are never cached.
evidence.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads));checked_receipt=evidence.checked_receipt
def outcome(root,e):
 try:
  p=checked_receipt(root,e['document'],e['original_path'],e['sha256']);return {'ok':True,'resolved':p.relative_to(root).as_posix(),'sha256':h(p)}
 except Exception as error:return {'ok':False,'error_type':type(error).__name__,'error':str(error).replace(str(root),'<ROOT>')}
c=collections.Counter()
for i,e in enumerate(proof['edges']):
 a=outcome(ROOT,e);b=outcome(CONTEXT,e);assert a==e['before'] and b==e['after'],e
 if a['ok']:assert b['ok'] and a['sha256']==b['sha256'];c['preserved_pass']+=1
 elif b['ok']:c['restored_prior_failure']+=1
 else:assert a==b,e;c['retained_failure']+=1
 if i%5000==0:print('independent edges',i,flush=True)
assert c['preserved_pass']==proof['summary']['preserved_pass'] and c['restored_prior_failure']==proof['summary']['restored_prior_failure'] and c['retained_failure']==proof['summary']['retained_failure']
from atlas.agent_review import validate_review,approval_entry
n='catalogue/agent-reviews/bingham-comsol63-agent-v1.json';v=validate_review(CONTEXT/n,root=CONTEXT,for_approval=True);approval=approval_entry(CONTEXT/n,root=CONTEXT);assert len(v['artifacts'])==88 and len(v['checklist'])==9
assert [x for x in json.loads((CONTEXT/'catalogue/approved-models.json').read_text())['models'] if x['model_id']==v['model']['id']]==[approval]
result={'exact_manifest':sys.argv[1],'receipt_pairs':len(record),'sibling_documents':len(siblings['documents']),'malformed_siblings_preserved':len(siblings.get('malformed_json_siblings',{})),'outcomes':dict(c),'newly_broken':0,'changed_failure':0,'maps':len(preservation['maps']),'accepted_existing_E5_artifacts':88,'scientific_E5_redecided':False,'compiled_or_material_calls':0,'shared_installation':False}
(OUT/'REPLAY-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
