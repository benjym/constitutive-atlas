"""Source-only coordinator replay. Does not validate complete executable models."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 packets=[('docs/ingestion/wu-bauer-1994/visual-review-v1','files'),('docs/ingestion/mohr-coulomb','files_sha256')]
 pins={}
 for rel,key in packets:
  p=ROOT/rel
  for name,h in json.loads((p/'manifest.json').read_text())[key].items():
   assert sha(p/name)==h,name
  pins[rel+'/manifest.json']=sha(p/'manifest.json')
 w=ROOT/packets[0][0];m=ROOT/packets[1][0]
 checked=subprocess.run([sys.executable,'-B',str(w/'check.py'),'--root',str(ROOT)],capture_output=True,text=True,check=True)
 wu=json.loads(checked.stdout)
 mc=subprocess.run([sys.executable,'-B',str(m/'check_certificates.py')],capture_output=True,text=True,check=True)
 assert json.loads(mc.stdout)==json.loads((m/'results.json').read_text())
 original=subprocess.run([sys.executable,'-B',str(m/'initial-boundary-tangent.py')],capture_output=True,text=True)
 assert original.returncode==1 and 'AssertionError' in original.stderr
 # Compare the failing assertion itself; traceback absolute paths are environment metadata.
 expected=(m/'initial-failure.log').read_text()
 assert expected.splitlines()[-2:]==original.stderr.splitlines()[-2:]
 src=json.loads((m/'sources.json').read_text())['primary'];pdf=Path(src['private_path'])
 source='unavailable; exact receipt retained'
 if pdf.exists():
  assert pdf.stat().st_size==src['bytes'] and sha(pdf)==src['sha256'];source='exact hash verified'
 return {'packet_manifest_hashes':pins,'wu_bauer':wu,'mohr_coulomb':{'certificates':14,'rotated_plastic_residuals':11,'bounded_tangent_checks':2,'exact_results_reproduced':True,'original_boundary_tangent_failure_reproduced':True,'private_source':source},'complete_executable_model_validation':False,'compiled_calls':0,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
