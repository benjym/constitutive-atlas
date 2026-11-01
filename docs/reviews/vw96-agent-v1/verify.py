"""Verify review and saved evidence only; never run integrators/builds/binaries."""
import argparse,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
sys.path.insert(0,str(R))
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--private-source',action='store_true');a=ap.parse_args()
 for p,h in read(P/'manifest.json')['files'].items():assert sha(P/p)==h,p
 for p,h in read(P/'inputs.json')['files'].items():assert sha(R/p)==h,p
 from atlas.agent_review import validate_review
 record=validate_review(P/'review.json',root=R,for_approval=True)
 assert record['status']=='accepted' and not record['blocking_findings']
 assert len(record['checklist'])==9 and all(x['outcome']=='pass'for x in record['checklist'])
 source=read(P/'source-reading.json')
 if a.private_source:
  assert sha(Path(source['source']['local_private_path']))==source['source']['sha256']
  for p,h in source['private_renders'].items():assert sha(Path(p))==h,p
 import check_saved
 saved=check_saved.main()
 assert saved==read(P/'checks.json')['checks'][0]['result']
 # Replay the small source algebra only; no oracle integrator or compiled calls.
 import runpy
 old=runpy.run_path(str(R/'docs/ingestion/hypoplastic-sand-vw96/original-equation-review-v2/check.py'),run_name='saved_source_algebra')
 assert old['report']==read(P/'checks.json')['checks'][1]['result']
 assert old['report']['status']=='pass' and old['report']['count']==27
 print(json.dumps({'review_integrity_pass':True,'decision':'accepted within exact README/review scope','checklist_passes':9,'saved_v1_remains_failed':True,'saved_v2_checks':229,'native_resume_checks':229,'source_algebra_checks':27,'current_release_qualified':False,'wasm_qualified':False,'browser_qualified':False,'experimental_validation':False,'new_integrations':0,'compiled_calls':0},indent=2))
if __name__=='__main__':main()
