"""Strict identity preflight; source/build receipt reads only, no backend calls."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;P=D.parent;ROOT=D.parents[4]
SOURCE_SHA='4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 assert sha(D/'source-freeze.json')==SOURCE_SHA
 for n,h in json.loads((D/'full-freeze.json').read_text())['files'].items():assert sha(ROOT/n)==h,'frozen input drift: '+n
 for n,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/n)==h,'rebind drift: '+n
 source=json.loads((D/'source-freeze.json').read_text());assert len(source['source_files'])==582
 for n,h in source['source_files'].items():assert sha(Path(source['source_directory'])/n)==h,'current runtime drift: '+n
 return {'identity':'md1997-control-runtime-rebind-v5','source_freeze_sha256':SOURCE_SHA,'source_directory':source['source_directory'],'source_files':582,'full_freeze_sha256':sha(D/'full-freeze.json'),'rebind_manifest_sha256':sha(D/'manifest.json'),'compiled_correspondence':'requires explicit external coordinator build receipt, not inferred from unchanged v4 report identity'}
def build_binding(receipt_path,backend,artifact):
 receipt_path=Path(receipt_path).resolve();r=json.loads(receipt_path.read_text());artifact=Path(artifact).resolve()
 assert r.get('identity')=='md1997-control-runtime-build-receipt-v5','external build receipt identity'
 assert r.get('source_freeze_sha256')==SOURCE_SHA and r.get('source_files')==582,'external build source binding'
 assert r.get('source_directory')==json.loads((D/'source-freeze.json').read_text())['source_directory'],'external source directory'
 assert r.get('backend')==backend and Path(r['artifact_path']).is_absolute() and Path(r['artifact_path']).resolve()==artifact,'external artifact/backend binding'
 for path_key,hash_key in [('artifact_path','artifact_sha256'),('catalogue_path','generated_catalogue_sha256'),('build_log_path','build_log_sha256')]:
  path=Path(r[path_key]);assert path.is_absolute() and path.is_file() and sha(path)==r[hash_key],'external byte binding: '+path_key
 expected=json.loads((P/'ordinary-regression-v7/policy.json').read_text())['generated_catalogue_sha256'];assert r['generated_catalogue_sha256']==expected,'unchanged normal16 catalogue'
 if backend=='wasm':
  wasm=artifact.with_suffix('.wasm');assert Path(r['wasm_path']).is_absolute() and Path(r['wasm_path']).resolve()==wasm and wasm.is_file() and sha(wasm)==r['wasm_sha256'],'external Wasm payload binding'
 else:assert backend=='native','unsupported backend'
 return {'coordinator_build_receipt_path':str(receipt_path),'coordinator_build_receipt_sha256':sha(receipt_path),'backend':backend,'artifact_path':str(artifact),'artifact_sha256':sha(artifact),'generated_catalogue_sha256':r['generated_catalogue_sha256'],'wasm_sha256':r.get('wasm_sha256') if backend=='wasm' else None,'build_log_sha256':r['build_log_sha256'],'external_build_receipt_is_coordinator_evidence_not_agent_approval':True}
if __name__=='__main__':print(json.dumps(check(),indent=2))
