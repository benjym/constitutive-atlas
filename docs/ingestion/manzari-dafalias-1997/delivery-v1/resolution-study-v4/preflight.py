"""Read-only source and study integrity preflight; no backend calls."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
ROOT=D.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 for n,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/n)==h,'study drift: '+n
 for n,h in json.loads((D/'parent-inputs.json').read_text()).items():assert sha(ROOT/n)==h,'parent drift: '+n
 source=json.loads((D/'source-freeze.json').read_text());assert len(source['source_files'])==578
 for n,h in source['source_files'].items():assert sha(Path(source['source_directory'])/n)==h,'runtime drift: '+n
 plan=json.loads((D/'requests.json').read_text())
 for c in plan['cases']:
  if c['kind']=='controls':assert len(c['controls'])<=5001 and c['controls'][0]==0,'unchanged runtime controls limit: '+c['id']
 return {'identity':'md1997-resolution-study-v4','source_receipt_sha256':sha(D/'source-freeze.json'),'source_directory':source['source_directory'],'source_files':578,'requests_sha256':sha(D/'requests.json'),'manifest_sha256':sha(D/'manifest.json'),'actual_build_correspondence':'requires coordinator build receipt','prospective_review_and_independent_resolution_justification':'required before execution; this preflight does not assert acceptance'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
