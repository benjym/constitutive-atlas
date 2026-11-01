"""Assess retained Wasm rates/paths independently of native parity."""
import argparse,json
from pathlib import Path
from atlas.initialization import canonical_hash
from atlas.model import load

def verify(report, *, reference_receipt=None):
 if report['version']=='gis2024-coupled-rate-wasm-0.1':
  from tools.gis2024_rate_study import MODEL_PATH,REFERENCE_PATH,assess
  model=load(MODEL_PATH)
  result=assess(report['records'],model,json.loads(REFERENCE_PATH.read_text())['cases'])
 elif report['version']=='clay2013-nonisotropic-wasm-0.1':
  from tools.clay2013_nonisotropic_study import MODEL_PATH,assess,digest
  from tools.clay2013_path_reference import study
  model=load(MODEL_PATH);reference=study()
  receipt=reference if reference_receipt is None else reference_receipt
  if report['reference_sha256']!=digest(receipt):raise ValueError('reference identity mismatch')
  if reference_receipt is not None:
   # Archived floating-point grids record the original platform. Bind that
   # receipt's source/protocol, then assess outputs against a fresh independent
   # reference here; archived endpoint/statistical values are never the oracle.
   keys=('contract','basis','zero_spin','coordinate','source_sha256','resolutions','rotation','dependency_sha256')
   if any(digest(receipt[k])!=digest(reference[k]) for k in keys) or digest([c['input'] for c in receipt['cases']])!=digest([c['input'] for c in reference['cases']]):
    raise ValueError('archived reference source/protocol mismatch')
  result=assess(report['records'],model,reference)
 else:raise ValueError('unsupported research matrix')
 if report['model_sha256']!=canonical_hash(model) or report['catalogue_hash']!=canonical_hash([model]):raise ValueError('model/catalogue identity mismatch')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);a=p.parse_args()
 verify(json.loads(a.report.read_text()));print('Independent Wasm research-matrix assessment passed')
