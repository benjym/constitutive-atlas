"""Author source-data payloads only; never installs into the export."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent; ROOT=P.parents[3]; BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
B=ROOT/'docs/delivery/unheld-finalisation-20261102-v1'; OUT=P/'proposed'
IDS=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']
changes={}; support={}; mappings={}
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(x):return (json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
def put(path,data,reason):
 assert not Path(path).is_absolute() and '..' not in Path(path).parts
 if path in changes:assert changes[path]['sha256']==sha(data);return
 old=(BASE/path).read_bytes() if (BASE/path).is_file() else None
 if old==data:return
 q=OUT/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
 changes[path]={'path':path,'preimage_sha256':sha(old) if old is not None else None,'sha256':sha(data),'bytes':len(data),'mode':'100644','proposal':q.relative_to(P).as_posix(),'reason':reason}
def current(path):return (OUT/path).read_bytes() if (OUT/path).is_file() else (BASE/path).read_bytes()
def archive(path,data,reason):
 dest=f'catalogue/source-snapshots/{sha(data)}/{path}';put(dest,data,reason);return dest
def locate(path,expected):
 candidates=[BASE/path,ROOT/path,B/'baseline-integration-v2/proposed'/path]
 for c in candidates:
  if c.is_file() and sha(c.read_bytes())==expected:return c.read_bytes()
 m=BASE/Path(path).parent/'source-archive-map.json'
 # Explicit matching intrinsic archived bytes may exist independently of caller map.
 for home in [BASE,ROOT]:
  c=home/f'catalogue/source-snapshots/{expected}/{path}'
  if c.is_file() and sha(c.read_bytes())==expected:return c.read_bytes()
 raise ValueError('Missing exact source '+path+' '+expected)
def mapping(document):
 path=(Path(document).parent/'source-archive-map.json').as_posix()
 if path not in mappings:
  mappings[path]=json.loads((BASE/path).read_text()) if (BASE/path).is_file() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 return mappings[path]
def redirect(document,path,expected,data):
 m=mapping(document);m['documents'][document]=sha(current(document))
 if sha(current(path))==expected:return
 dest=archive(path,data,'Retain exact historical receipt bytes')
 row={'original_path':path,'sha256':expected,'archived_path':dest}
 found=[r for r in m['entries'] if r['original_path']==path and r['sha256']==expected]
 assert not found or found==[row]
 if not found:m['entries'].append(row)
# Five accepted exact definitions and new review records.
newhash={}
for mid in IDS:
 data=(B/f'baseline-migration/proposals/{mid}.json').read_bytes();newhash[mid]=sha(data)
 path=f'models/{mid}.json';archive(path,(BASE/path).read_bytes(),'Immutable superseded definition');put(path,data,'Accepted schema0.3 definition')
 path=f'catalogue/agent-reviews/{mid}-v03-agent-v1.json'
 data=(B/'baseline-five-v03-scientific-review-v1/actual-phase-v1/proposed'/path).read_bytes();put(path,data,'Genuine independent E5 record')
# Preserve current30 ordered objects; append only five accepted E5 approvals.
registry=json.loads((BASE/'catalogue/approved-models.json').read_text());before=list(registry['models'])
oldreg=json.loads((B/'baseline-five-publication-additive-source-v1/proposed/catalogue/approved-models.json').read_text())
added=[a for a in oldreg['models'] if a['model_id'] in IDS and '-v03-' in a['id']];assert len(before)==30 and len(added)==5
registry['models']+=added;assert len({a['id'] for a in registry['models']})==35
put('catalogue/approved-models.json',dump(registry),'Preserve current30 and append genuine five approvals')
# Exact direct E5 support closure (62 paths), immutable records and model archives.
for approval in added:
 for pin in [approval['definition'],approval['review']]+approval.get('supporting_files',[]):
  path,expected=pin['path'],pin['sha256'];data=locate(path,expected) if not ((OUT/path).is_file() and sha((OUT/path).read_bytes())==expected) else (OUT/path).read_bytes()
  support[path]=expected
  if not (BASE/path).is_file():put(path,data,'Exact E5 supporting-file closure')
# Every review remains unchanged; redirect only mismatching direct receipt bytes.
reviewpaths=set(p.relative_to(BASE).as_posix() for p in (BASE/'catalogue/agent-reviews').glob('*.json') if p.name!='source-archive-map.json')|{a['review']['path'] for a in added}
for document in sorted(reviewpaths):
 rec=json.loads(current(document)); mapping(document)['documents'][document]=sha(current(document))
 for pin in [rec['model']]+rec['artifacts']:
  path,expected=pin['path'],pin['sha256']
  try:data=current(path)
  except FileNotFoundError:data=b''
  if sha(data)!=expected:
   data=locate(path,expected);redirect(document,path,expected,data)
# Registry resolver preserves historical approvals without approving new canonical bytes.
for a in registry['models']:
 pin=a['definition'];path,expected=pin['path'],pin['sha256'];data=locate(path,expected) if sha(current(path))!=expected else current(path)
 redirect('catalogue/approved-models.json',path,expected,data)
# Current sixteen package allocation: five exact identity changes only.
policy=json.loads((BASE/'catalogue/laboratory-package-policy.json').read_text());policy['id']='supported-package-sixteen-baseline-five-v03-v1';policy['models'].update(newhash)
put('catalogue/laboratory-package-policy.json',dump(policy),'Current sixteen allocation with five new definitions; gates unchanged')
profile=json.loads((BASE/'catalogue/laboratory-profile-policy.json').read_text());profile['id']='current-sixteen-baseline-five-v03-profiles-v1';profile['supported_policy']['sha256']=sha(current('catalogue/laboratory-package-policy.json'))
put('catalogue/laboratory-profile-policy.json',dump(profile),'Bind successor package policy; all43 cases and thresholds unchanged')
matrix=json.loads((BASE/'catalogue/applicability/kfs-development-v1.json').read_text());matrix['id']='kfs-development-applicability-baseline-five-v03-20261105-v1';matrix['prepared_on']='2026-11-05'
for row in matrix['rows']:
 if row['model']['id'] in newhash:row['model']['sha256']=newhash[row['model']['id']]
 if row['model']['id']=='hypoplastic-sand-vw96':
  row['limitations'][0]='Historical TMD7 file/file development compatibility up to the first 2% cutoff applies to the exact linked legacy definition 1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61 and its recorded engine, not the full test or all six evaluation tests. No current schema0.3 or current sixteen-model engine experimental equivalence is inferred.'
put('catalogue/applicability/kfs-development-v1.json',dump(matrix),'Identity-only successor; all pending assessments unchanged')
# Reader profiles already carry correct law/limits. Add explicit preparation and exact E5 link only to five entries.
text=(BASE/'web/model-profile-data.mjs').read_text()
for mid in IDS:
 match=re.search(r'^  "'+re.escape(mid)+r'": ',text,re.M);assert match
 start=match.end();obj,n=json.JSONDecoder().raw_decode(text[start:]);old=dict(obj)
 # Preserve the public schema and prose: no unsupported new keys.
 # Current descriptions remain correct for the same laws; hash/model facts are builder generated.
assert text==(BASE/'web/model-profile-data.mjs').read_text()
# Discovery: exact source acceptance replaces only stale IGS review-pending assertion.
manifest=json.loads((BASE/'catalogue/manifest.json').read_text())
entry=next(e for e in manifest['models'] if e['id']=='hypoplastic-sand-igs97')
entry['note']='Intergranular-strain overlay on the von Wolffersdorff sand law; compression-positive Mandel components, explicit caller history and bounded documented cap/admission band. Exact schema0.3 source/numerical scope has independent agent review; calibration, experimental validity and arbitrary-path accuracy remain unclaimed.'
put('catalogue/manifest.json',dump(manifest),'Replace stale IGS review-pending prose only')
# Old named request/results are retained as historical evidence, not repinned to current16.
oldexamples=B/'baseline-five-current-example-integration-v1/proposed'
examples=json.loads((oldexamples/'catalogue/laboratory-examples.json').read_text())
requests=[]
for e in examples['examples']:
 if e['model'] in IDS:
  doc=(oldexamples/e['document_path']).read_bytes();assert sha(doc)==e['document_sha256']
  requests.append({'entry':e,'historical_document':{'path':str(oldexamples/e['document_path']),'sha256':sha(doc)},'current16_observation_required':True})
(P/'named-example-handoff.json').write_bytes(dump(requests))
# Archive every replaced canonical file before proposing replacement. Preserve old map bytes too.
for path,row in list(changes.items()):
 if row['preimage_sha256'] is not None:archive(path,(BASE/path).read_bytes(),'Archive exact replaced canonical preimage')
for path,m in mappings.items():
 if (BASE/path).is_file():archive(path,(BASE/path).read_bytes(),'Archive original additive resolver map')
 # Bind changed checked-receipt documents in catalogue map while preserving all entries.
 if path=='catalogue/source-archive-map.json':
  for doc in list(m['documents']):
   if doc in changes:m['documents'][doc]=sha(current(doc))
 put(path,dump(m),'Add exact historical definition/contract receipt redirects')
# Generic research subset is separately scoped/reviewed.
p=P/'historical-resolution-v1/proposed/atlas/research.py';put('atlas/research.py',p.read_bytes(),'Separately scoped historical approval resolution')
archive('atlas/research.py',(BASE/'atlas/research.py').read_bytes(),'Exact generic source predecessor')
(P/'source-delta.json').write_bytes(dump({'base_revision':'6b957b866c977263fad0c02be4216c7f9170cf5b','files':sorted(changes.values(),key=lambda r:r['path'])}))
(P/'direct-support.json').write_bytes(dump(support))
print(json.dumps({'changes':len(changes),'new_approvals':len(added),'direct_support':len(support),'new_hashes':newhash},indent=2))
