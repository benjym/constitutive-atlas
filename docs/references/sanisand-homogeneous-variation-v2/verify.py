"""Saved-only hash checks and unchanged failed/passing assessment replay."""
import hashlib,json,subprocess,sys
from assess import HERE,ROOT,load
from report import report

def main():
 for manifest in ('freeze.json','manifest.json'):
  for name,expected in load(HERE/manifest)['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
 result=load(HERE/'runs/result.json.gz')
 for r in result['runs']:assert r==load(HERE/f"runs/run-{r['precision']}-{r['tolerance']}.json.gz")
 assert report(result)==load(HERE/'assessment.json')
 receipt=load(HERE/'assessment-process.json');assert receipt['exit_code']==1 and 'ValueError: reference coordinates' in receipt['stderr']
 replay=subprocess.run([sys.executable,str(HERE/'assess.py'),str(HERE/'runs/result.json.gz')],capture_output=True,text=True)
 assert replay.returncode==1 and 'ValueError: reference coordinates' in replay.stderr
 assert load(HERE/'execution.json')['exit_code']==0
 print(json.dumps({'saved_evidence_integrity':True,'new_runs_completed':3,'original_output_gates_pass':True,'frozen_v2_assessment_pass':False,'original_v1_audit_pass':False,'native_qualification_pass':False,'scientific_admission':False},indent=2))
if __name__=='__main__':main()
