"""Read-only reverse exact-byte binding audit. Writes only the named output folder."""
import sys,json,pathlib,subprocess,hashlib,importlib.util,collections
ROOT=pathlib.Path('/private/tmp/atlas-bingham-delivery-v1');OUT=pathlib.Path(__file__).resolve().parent/'fast-v2';OUT.mkdir(exist_ok=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='b529a0efc3415b2bc567178a68174575c220cadc'
TARGETS={'web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','catalogue/publications.json','docs/STATUS.md','ROADMAP.md','IMPLEMENTATION_PLAN.md'}
sha=lambda b:hashlib.sha256(b).hexdigest()
for t in TARGETS:assert (ROOT/t).read_bytes()==subprocess.check_output(['git','show','HEAD:'+t],cwd=ROOT),t
spec=importlib.util.spec_from_file_location('scanner',ROOT/'docs/reviews/spectral-dsl-source-bindings-v1/audit/scan.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s);s.TARGETS=TARGETS
s.EXCLUDE_PARTS|={'frozen-source','frozen-sources-v1','inputs','prior-source'}
original_pairs=s.pairs
external=set()
def owned_pairs(node,parts=(),secondary=False):
 for row in original_pairs(node,parts,secondary):
  path=pathlib.Path(row[0])
  if path.is_absolute() or '..' in path.parts:external.add(row[0])
  else:yield row
s.pairs=owned_pairs
candidate_paths=[ROOT/x for x in pathlib.Path('/private/tmp/bingham-receipt-candidates.txt').read_text().splitlines()]
old_rglob=pathlib.Path.rglob
def candidate_rglob(p,pattern,**kw):
 if p.parent==ROOT and p.name in s.ROOTS and pattern=='*.json':return (x for x in candidate_paths if x.is_relative_to(p))
 return old_rglob(p,pattern,**kw)
pathlib.Path.rglob=candidate_rglob
result=s.scan(ROOT)
pathlib.Path.rglob=old_rglob
result['excluded_external_worktree_paths']=sorted(external)
(OUT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
# Only current-live primary hashes can be newly broken by changing these base files.
primary=[r for r in result['primary_references'] if r['expected_equals_current_live']]
need=[r for r in primary if r['resolution']=='live']
sidecars={str(pathlib.Path(r['document']).parent/'source-archive-map.json') for r in need}
secondary=[]
while True:
 n=len(sidecars)
 for r in result['secondary_source_map_references']:
  if r['original_path'] not in sidecars:continue
  p=ROOT/r['original_path']
  if not p.exists() or sha(p.read_bytes())!=r['sha256']:continue
  # Historical sidecar entries already resolve through their canonical archive;
  # merely preserve exact old map bytes rather than mutate those other maps.
  if r['document'].endswith('/source-archive-map.json'):continue
  if r['resolution']=='live':
   if r not in secondary:secondary.append(r)
   sidecars.add(str(pathlib.Path(r['document']).parent/'source-archive-map.json'))
 if len(sidecars)==n:break
rows=[]
for t in sorted(TARGETS):
 rows.append({'path':t,'base_sha256':sha((ROOT/t).read_bytes()),'canonical_archive':'catalogue/source-snapshots/'+sha((ROOT/t).read_bytes())+'/'+t,'archive_exists':(ROOT/'catalogue/source-snapshots'/sha((ROOT/t).read_bytes())/t).exists(),'current_hash_dependents':[r for r in primary if r['original_path']==t],'new_live_edges':[r for r in need if r['original_path']==t]})
# Existing sidecar doc pin discrepancies and required sibling coverage are explicit, never silently rewritten.
maprows=[]
for side in sorted(sidecars):
 p=ROOT/side; m=json.loads(p.read_text()) if p.exists() else {'documents':{},'entries':[]};docs=sorted({r['document'] for r in need+secondary if str(pathlib.Path(r['document']).parent/'source-archive-map.json')==side});mismatch=[]
 for doc in docs:
  live=sha((ROOT/doc).read_bytes());pin=m.get('documents',{}).get(doc)
  if pin is not None and pin!=live:mismatch.append({'document':doc,'current_sha256':live,'map_document_pin':pin,'prior_archive_exists':(ROOT/'catalogue/source-snapshots'/pin/doc).exists()})
 siblings=[]
 for f in p.parent.glob('*.json'):
  if f==p:continue
  v=json.loads(f.read_text());manifest=isinstance(v,dict) and (isinstance(v.get('files'),dict) or isinstance(v.get('dependencies'),dict) or (v and all(isinstance(h,str) and s.valid(h) for h in v.values())))
  if manifest:siblings.append({'document':f.relative_to(ROOT).as_posix(),'sha256':sha(f.read_bytes()),'already_bound':f.relative_to(ROOT).as_posix() in m.get('documents',{})})
 maprows.append({'sidecar':side,'exists':p.exists(),'base_sha256':sha(p.read_bytes()) if p.exists() else None,'documents_requiring_binding':docs,'document_pin_conflicts':mismatch,'file_manifest_sibling_coverage':siblings})
plan={'base_commit':'b529a0efc3415b2bc567178a68174575c220cadc','read_only':True,'targets':rows,'primary_live_edges_requiring_addition':need,'secondary_live_map_edges_requiring_addition':secondary,'sidecars_to_add_or_extend':maprows,'summary':{'target_files':len(rows),'current_hash_primary_edges':len(primary),'already_archived_current_edges':sum(r['resolution']=='archived' for r in primary),'new_primary_live_edges':len(need),'secondary_live_edges':len(secondary),'maps':len(maprows),'historical_unresolved_pairs':result['summary']['primary_unresolved']}}
(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan['summary'],indent=2))
