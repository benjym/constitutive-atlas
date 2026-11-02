"""Restore three existing exact receipt contexts; read archive bytes, never execute."""
from pathlib import Path
import gzip,hashlib,io,json,sys,zipfile
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-clean-checkout-evidence-v1/tracked-context');sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();doc='docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json';receipt=json.loads((R/doc).read_text());inst=json.loads((H/'INSTALLATION.json').read_text());(H/'INSTALLATION-export-only-v1.json').write_bytes((H/'INSTALLATION.json').read_bytes());(H/'INTEGRITY-export-only-v1.json').write_bytes((H/'INTEGRITY.json').read_bytes())
archive='docs/ingestion/bingham-comsol63/asset-provision-v1/qualified-assets.zip';tracked=json.loads(gzip.decompress((H/'TRACKED-INPUTS.json.gz').read_bytes()));assert archive in tracked and sha(C/archive)==tracked[archive]['sha256'];rows=[]
with zipfile.ZipFile(C/archive) as z:
 for key,item in receipt['artifacts'].items():
  n=item['path'];h=item['sha256'];local=checked_receipt(R,doc,n,h);target=local.relative_to(R).as_posix();assert target not in tracked;member={'module':'bingham.mjs','wasm':'bingham.wasm','metadata':'generated/models.json'}[key];data=z.read(member);assert hashlib.sha256(data).hexdigest()==h and local.read_bytes()==data
  try:checked_receipt(C,doc,n,h)
  except ValueError as e:before={'passed':False,'error':str(e)}
  else:raise AssertionError('Expected clean missing historical context')
  payload=H/'candidate-bytes'/(h+Path(target).suffix);payload.write_bytes(data);p=C/target;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert checked_receipt(C,doc,n,h).read_bytes()==data
  inst['files'][target]={'sha256':h,'before_local_sha256':h,'tracked_in_baseline':False,'candidate':payload.relative_to(H).as_posix(),'provenance':str(local),'classification':'Existing mapped Bingham build-receipt context; not an active export read','tracked_qualified_archive':archive,'archive_member':member,'action':'Track existing exact hash-pinned archive member; no receipt/map change'}
  rows.append({'document':doc,'original_path':n,'sha256':h,'canonical_snapshot':target,'before':before,'after':{'passed':True,'resolved':target},'tracked_archive_member_equal':True,'archive_member':member})
assert len(inst['files'])==10;inst['scope_split']={'active_export_inputs':7,'existing_mapped_bingham_asset_receipts':3};(H/'INSTALLATION.json').write_text(json.dumps(inst,indent=2)+'\n');(H/'SUPPLEMENTARY-RECEIPTS.json').write_text(json.dumps({'passed':True,'records':rows,'tracked_qualified_archive':{'path':archive,'sha256':sha(C/archive)},'binary_execution':False},indent=2)+'\n')
