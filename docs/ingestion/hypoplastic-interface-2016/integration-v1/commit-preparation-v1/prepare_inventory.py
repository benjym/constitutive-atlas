from pathlib import Path
import subprocess,json,hashlib,collections
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');RELEASE=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2');OUT=ROOT/'docs/ingestion/hypoplastic-interface-2016/integration-v1/commit-preparation-v1';OUT.mkdir(parents=True,exist_ok=True)
PARENT='54f409b37deaed0ab82a85cdac9f489bc65e1309';PACKET='docs/ingestion/hypoplastic-interface-2016/'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
def oid(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
base={}
for item in git('ls-tree','-rz',PARENT).split(b'\0'):
 if not item:continue
 meta,name=item.split(b'\t',1);mode,kind,digest=meta.decode().split();base[name.decode()]=(mode,kind,digest)
reasons=collections.defaultdict(set)
def add(name,reason):
 p=Path(name);assert not p.is_absolute() and '..' not in p.parts
 assert not any(part in {'.local','.git','.agents','.codex','.aws','private-sources','__pycache__'} for part in p.parts),(name,'private/cache')
 assert p.suffix.lower() not in {'.pdf','.dll','.dylib','.wasm','.so','.o','.a','.zip','.tar','.gz','.png','.jpg','.jpeg'},(name,'binary/private artifact')
 assert not name.startswith(('paper/','output/'))
 reasons[name].add(reason)
installation=json.loads((ROOT/(PACKET+'integration-v1/installation.json')).read_text())
for name in installation['copied_owned_files']:add(name,'explicit installation whitelist')
freeze=json.loads((ROOT/(PACKET+'integration-v1/integration-source-freeze.json')).read_text())
for name,digest in freeze['files'].items():
 assert sha((RELEASE/name).read_bytes())==digest,('integration reviewed bytes drift',name)
 add(name,'reviewed 11 integration paths')
for name in ['IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md']:add(name,'coordinator isolated tracking checkpoint')
# New model-owned packet evidence only: enumerate the assigned packet, never the full release diff.
for p in (RELEASE/PACKET).rglob('*'):
 if not p.is_file() or p.is_symlink():continue
 name=p.relative_to(RELEASE).as_posix()
 if '__pycache__' in p.parts:continue
 if name.startswith(PACKET+'integration-v1/commit-preparation-v1/'):continue
 if name not in base:add(name,'new isolated model-owned packet evidence')
 else:
  # Existing packet originals must retain exactly their historical object identity.
  if name not in reasons:assert oid(p.read_bytes())==base[name][2],('unapproved historical packet modification',name)
# Parent integration source scripts/receipts are copied explicitly by parent before execution.
integration=ROOT/(PACKET+'integration-v1')
for p in integration.iterdir():
 if p.is_file() and p.suffix in {'.py','.json'}:add(p.relative_to(ROOT).as_posix(),'coordinator integration preparation evidence')
preservation=[]
for receipt_name in ['preservation-receipt-v2.json','tracking-preservation-receipt.json']:
 receipt_path=integration/receipt_name;d=json.loads(receipt_path.read_text());assert d['isolated_release']==str(RELEASE)
 for name,digest in d['source_preimages'].items():
  archive=f'catalogue/source-snapshots/{digest}/{name}'
  if (RELEASE/archive).is_file():
   assert sha((RELEASE/archive).read_bytes())==digest
   add(archive,'exact source preimage from '+receipt_name)
 for entry in d['map_changes']:
  add(entry['map'],'historical receipt map from '+receipt_name)
  if entry['old_map_archive']:add(entry['old_map_archive'],'exact prior map from '+receipt_name)
  m=json.loads((RELEASE/entry['map']).read_text());document=RELEASE/entry['document'];assert m['documents'][entry['document']]==sha(document.read_bytes())
  matches=[v for v in m['entries'] if v.get('original_path')==entry['source'] and v.get('sha256')==entry['source_sha256']];assert len(matches)==1
  assert sha((RELEASE/matches[0]['archived_path']).read_bytes())==entry['source_sha256']
  add(matches[0]['archived_path'],'mapped exact preimage from '+receipt_name)
  if entry['old_map_archive']:
   archive=RELEASE/entry['old_map_archive'];expected=Path(entry['old_map_archive']).parts[2];assert sha(archive.read_bytes())==expected
  preservation.append({'receipt':receipt_path.relative_to(ROOT).as_posix(),'map':entry['map'],'document':entry['document'],'source':entry['source'],'source_sha256':entry['source_sha256']})
entries=[];unchanged=[];missing=[];root_copy=[]
for name in sorted(reasons):
 source=RELEASE/name
 if not source.is_file():
  candidate=ROOT/name
  assert name.startswith(PACKET+'integration-v1/') and candidate.is_file(),('missing isolated source',name)
  source=candidate;root_copy.append(name)
 assert not source.is_symlink()
 data=source.read_bytes();blob=oid(data)
 if name in base and blob==base[name][2]:unchanged.append(name);continue
 mode=base[name][0] if name in base else ('100755' if source.stat().st_mode&0o111 else '100644')
 assert mode in {'100644','100755'}
 entries.append({'path':name,'sha256':sha(data),'git_blob_sha1':blob,'size':len(data),'mode':mode,'change':'modify' if name in base else 'add','source':str(source),'reasons':sorted(reasons[name])})
summary={'parent':PARENT,'release_root':str(RELEASE),'owned_ref':'refs/heads/delivery/interface2016-v1','entries':entries,'unchanged_whitelist_paths':unchanged,'parent_copy_required_before_execution':root_copy,'checks':{'git_mutations_executed':False,'root_HEAD_index_worktree_shared_files_untouched':True,'full_isolated_tree_diff_used':False,'private_originals_or_compiled_artifacts_included':False,'paper_or_unrelated_model_inputs_included':False,'reviewed_integration_paths_verified':len(freeze['files']),'historical_preservation_events_verified':len(preservation),'receipt_resolutions':preservation}}
(OUT/'inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'paths.txt').write_text(''.join(e['path']+'\n' for e in entries))
print(json.dumps({'entries':len(entries),'adds':sum(e['change']=='add' for e in entries),'modifies':sum(e['change']=='modify' for e in entries),'bytes':sum(e['size'] for e in entries),'root_evidence_copy_required':root_copy,'unchanged':len(unchanged),'preservation_events':len(preservation)},indent=2))
