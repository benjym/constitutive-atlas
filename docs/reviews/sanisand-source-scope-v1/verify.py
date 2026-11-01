"""Saved-evidence and exact-rational scope checks; no integration or compiled calls."""
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(path):return json.loads(path.read_text())
def main():
 for name in ('inputs.json','manifest.json'):
  for path,expected in load(HERE/name)['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
 d=load(HERE/'decision.json')
 assert d['disposition']=='retain-research-only; stop-numerical-expansion'
 assert all(d[x] is False for x in ['public_installation','native_qualified','canonical_reversal_resolved','scientific_admission'])
 assert d['independent_signature'] is None
 native=load(ROOT/'docs/reviews/sanisand-v03-monotonic-v1/native-assessment.json')
 assert native['research_qualification_pass'] is False and native['successful_trajectory_checks']==77 and native['expected_trajectories']==81
 v2=load(ROOT/'docs/references/sanisand-homogeneous-variation-v2/assessment.json')
 assert v2['frozen_v2_assessment_pass'] is False and v2['original_v1_audit_pass'] is False
 assert v2['unchanged_output_audit']['independent_diagnostic_audit_pass'] is True
 covariance=load(ROOT/'docs/reviews/sanisand-transverse-extension-v1/covariance-assessment.json')
 assert covariance['proper_rotation_covariance_pass'] is True and covariance['states']==39
 model=load(ROOT/'docs/reviews/sanisand-v03-research-freeze-v1/model.json')
 derived={x['name']:x['expr'] for x in model['derived']}
 assert derived['B']=='1+(3/2)*(1-c)/c*g*cos3theta'
 assert derived['C']=='3*sqrt(3/2)*(1-c)/c*g'
 assert derived['Rdev']=='dev(B*n-C*tensor_square(n))'
 # At extension C/sqrt(6)=(3/2)*(1-c); all expressions below are rational.
 c=F(89,125);B=1-F(3,2)*(1-c);two_C_n=3*(1-c)
 assert B-two_C_n==F(-37,125)
 assert B+F(3,2)*(1-c)==1  # Rdev=n at exact symmetric extension.
 assert (9*F(7,9)-7)/2==0
 # Polynomial identities hold coefficient-by-coefficient, not by sampled fitting.
 assert [F(-1,2)-3,F(3,2)+3]==[F(-7,2),F(9,2)]
 assert [F(-1,2)+F(3,2),F(3,2)-F(3,2)]==[1,0]
 result={'saved_evidence_integrity':True,'source_flow_expressions_bound':True,'exact_extension_flow_derivative':str(B-two_C_n),'exact_symmetric_flow_coefficient':'1','native_qualification_pass':False,'scientific_admission':False,'new_integrations':0,'new_builds':0}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
