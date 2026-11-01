#!/usr/bin/env python3
"""Read-only identity preflight; no material or compiled call."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 freeze=json.loads((D/'full-freeze.json').read_text())
 for name,h in freeze['files'].items():assert sha(ROOT/name)==h,'frozen input drift: '+name
 for name,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/name)==h,'rebind manifest drift: '+name
 source=json.loads((D/'source-freeze.json').read_text());assert len(source['source_files'])==578
 for name,h in source['source_files'].items():assert sha(Path(source['source_directory'])/name)==h,'corrected source drift: '+name
 return {'identity':'md1997-runtime-rebind-v1','source_freeze_sha256':sha(D/'source-freeze.json'),'full_freeze_sha256':sha(D/'full-freeze.json'),'rebind_manifest_sha256':sha(D/'manifest.json'),'source_directory':source['source_directory'],'source_files':len(source['source_files']),'compiled_build_correspondence':'requires separate coordinator exact build receipt'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
