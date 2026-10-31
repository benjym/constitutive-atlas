"""Replay prospective analytical certificates; no production engine imports."""
from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def replay():
 for name,digest in read(P/'manifest.json')['files'].items():assert sha(P/name)==digest,name
 a=P/'audit'
 for name,record in read(a/'manifest.json')['files'].items():
  assert (a/name).stat().st_size==record['bytes'] and sha(a/name)==record['sha256'],name
 bindings=read(a/'review-inputs.json')
 for key in ('reviewed_contract','reviewed_qualifier'):
  record=bindings[key];assert sha(a/record['snapshot'])==record['sha256']
 for name in ('FORMULAS.md','sources.json'):
  original='/Users/bmar5496/code/constitutive-atlas/docs/ingestion/mohr-coulomb/'+name
  record=next(x for x in bindings['source_bindings'] if x['path']==original)
  assert sha(ROOT/'docs/ingestion/mohr-coulomb'/name)==record['sha256']
 context=read(P/'context.json')
 assert sha(ROOT/'docs/ingestion/mohr-coulomb/manifest.json')==context['primary_manifest_sha256']
 pdf_record=next(x for x in bindings['source_bindings'] if x['path'].endswith('.pdf'))
 pdf=Path(pdf_record['path']);source='unavailable; pinned receipt retained'
 if pdf.exists():assert sha(pdf)==pdf_record['sha256'];source='exact hash verified'
 outputs=[]
 for script,expected in [(P/'check_guard_flow.py',P/'guard-flow-results.json'),(a/'check_projectors.py',a/'results.json')]:
  result=subprocess.run([sys.executable,'-B',str(script)],capture_output=True,text=True,check=True)
  value=json.loads(result.stdout);assert value==read(expected),script.name
  outputs.append(value)
 q,d=outputs
 witness=read(P/'mixed-scale-witness.json');large=1e300
 from fractions import Fraction
 exact=Fraction.from_float(large)+1-Fraction.from_float(large)
 assert exact==1 and (float(exact)-large)+large==witness['naive_left_associated_trace_minus_max_minus_min']==0
 return {'packet_manifest_verified':True,'audit_manifest_verified':True,'reviewed_snapshots_verified':True,'source_bindings_verified':True,'private_source':source,'qualifier':q,'directional_rows':d['directional_rows'],'rotated_checks':d['rotated_checks'],'pair_sum_checks':d['pair_sum_checks'],'analytical_failures':d['failed'],'mixed_scale_witness_reproduced':True,'compiled_calls':0,'production_engine_changed':False,'floating_policy_frozen':False,'parent_task_complete':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(replay(),indent=2,sort_keys=True))
