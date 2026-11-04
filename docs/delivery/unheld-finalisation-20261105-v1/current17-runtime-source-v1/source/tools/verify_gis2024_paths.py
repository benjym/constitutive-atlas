"""Independently assess GIS finite paths, separating archive receipts from numerics."""
import argparse,json
from pathlib import Path
from atlas.model import load
from atlas.initialization import canonical_hash as digest
from tools.gis2024_integration_study import MODEL_PATH,assess,assess_probes,check_response
from tools import gis2024_path_reference as reference

def verify(report, *, reference_receipt=None):
 if report['version']not in ('gis2024-coupled-integration-0.1','gis2024-coupled-integration-wasm-0.1'):raise ValueError('unsupported GIS path report')
 model=load(MODEL_PATH);fresh=reference.study();receipt=fresh if reference_receipt is None else reference_receipt
 if report['model_sha256']!=digest(model)or report['catalogue_hash']!=digest([model]):raise ValueError('model/catalogue identity mismatch')
 if report['reference_sha256']!=digest(receipt):raise ValueError('reference receipt mismatch')
 if reference_receipt is not None:
  keys=('contract','basis','coordinate','zero_spin','source_sha256','source_url','source_doi','source_locators','resolutions','rotation','dependency_sha256')
  if any(digest(receipt[k])!=digest(fresh[k])for k in keys)or digest([c['input']for c in receipt['cases']])!=digest([c['input']for c in fresh['cases']]):raise ValueError('archived reference source/protocol mismatch')
 result=assess(report['records'],model,fresh);assess_probes(report['failure_probes'],report['records'],model)
 if report['version']=='gis2024-coupled-integration-wasm-0.1':assess_recovery(report,model)
 return result

def assess_recovery(report,model):
 expected=next(g for g in report['records']if g['tolerance']==1e-8 and g['partitions']==1)['calls'][0]
 control=report['recovery_control'];recoveries=report['recovery_responses']
 if report.get('persistent_recovery_verified')is not True or control!=expected or [r['after']for r in recoveries]!=['budget','domain','zero']:raise ValueError('persistent recovery provenance mismatch')
 check_response(control['response'],control['request'],model)
 for r in recoveries:
  check_response(r['response'],r['request'],model)
  if r['request']!=control['request']or r['response']!=control['response']:raise ValueError('persistent recovery differs from control')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);p.add_argument('--reference-receipt',type=Path);a=p.parse_args()
 result=verify(json.loads(a.report.read_text()),reference_receipt=json.loads(a.reference_receipt.read_text())if a.reference_receipt else None)
 print(f"Independently assessed {len(result['trajectories'])} GIS path trajectories")
