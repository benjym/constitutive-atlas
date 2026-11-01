"""Saved-only review integrity/algebra; no integration, builds or model execution."""
import argparse,hashlib,json,subprocess,sys
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[3]
def read(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--private-source',action='store_true');args=ap.parse_args()
 e=read(P/'evidence.json');d=read(P/'decision.json');manifest=read(P/'manifest.json')
 for p,h in manifest['files'].items(): assert digest(P/p)==h,p
 for p,h in e['files'].items(): assert digest(R/p)==h,p
 assert hashlib.sha256(json.dumps(d['reviewer'],sort_keys=True).encode()).hexdigest()==e['reviewer_identity_sha256']
 assert [x['id']for x in d['decisions']]==['D01','D02','D03','D04','D05','D06','D07','D08']
 assert all(d[k] is False for k in ['native_qualified','canonical_reversal_resolved','model_approved','public_installation','experimental_validation','reference_is_general_binary64_input_oracle'])
 assert d['new_integrations']==d['new_builds']==0
 native=read(R/'docs/reviews/sanisand-v03-monotonic-v1/native-assessment.json')
 assert native['research_qualification_pass'] is False
 assert (native['successful_trajectory_checks'],native['expected_trajectories'])==(77,81)
 assert sum(x['gate']=='fine trajectory accuracy'for x in native['failures'])==4
 v2=read(R/'docs/references/sanisand-homogeneous-variation-v2/assessment.json')
 assert v2['frozen_v2_assessment_pass'] is False and v2['original_v1_audit_pass'] is False
 c=F(89,125);B=(3*c-1)/2
 assert B-3*(1-c)==F(-37,125)
 assert B+F(3,2)*(1-c)==1
 # General finite-product identity tested as exact rational algebra, not integration.
 for dist,hbar,elastic,load,b0 in [(F(1,7),F(3),F(2),F(5),F(4)),(F(1,11),F(-1),F(2),F(-3),F(7))]:
  q=load/(hbar+dist*elastic);L=load/(hbar/dist+elastic)
  assert L==dist*q
  assert max(L,0)*b0/dist==b0*max(q,0)
 if args.private_source:
  assert digest(Path(e['private_source']['path']))==e['private_source']['sha256']
  for p,h in e['private_renders'].items(): assert digest(Path(p))==h,p
 commands=[['docs/references/sanisand-project-monotonic-v1/verify.py'],['docs/references/sanisand-project-monotonic-v1/test_assess.py','-q'],['docs/reviews/sanisand-source-scope-v1/verify.py']]
 results=[]
 for cmd in commands:
  proc=subprocess.run([sys.executable,'-B']+cmd,cwd=R,capture_output=True,text=True)
  assert proc.returncode==0,(cmd,proc.stdout,proc.stderr)
  results.append({'command':[sys.executable,'-B']+cmd,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
 print(json.dumps({'review_integrity_pass':True,'saved_checks':results,'native_qualified':False,'model_approved':False,'new_integrations':0,'new_builds':0},indent=2))
if __name__=='__main__':main()
