"""Source-only checks under a frozen policy; no Atlas material imports or execution."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,hashlib
P=Path(__file__).parent;ROOT=P.parents[2]
s=importlib.util.spec_from_file_location('centered_design',P/'exact.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e)

def run():
 for n,h in json.loads((P/'pre-check-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 inputs=json.loads((P/'inputs.json').read_text());rows=[];known=0
 for c in inputs['cases']:
  v=list(map(float.fromhex,c['mandel']));w=float.fromhex(c['width']);a=e.invariant_middle_gt(v,w);b=e.sturm_middle_gt(v,w);assert a==b,c['id']
  if c['expected']is not None:assert a==c['expected'],c['id'];known+=1
  rows.append({'id':c['id'],'result':a,'group':c['group']})
 lookup={r['id']:r['result']for r in rows};metamorphic=0
 for i in range(12):
  base=lookup['metamorphic/base/'+str(i)]
  for kind in ['shift','permutation','sign','scale']:assert lookup['metamorphic/'+kind+'/'+str(i)]==base;metamorphic+=1
 # Root multiplicity and strict-zero tests are independent of the tensor predicate.
 roots_tests=[([-1,2,2],2),([-1,0,1],1),([0,0,0],0),([1,1,1],3),([-1,-1,-1],0),([0,2,2],2),([-2,0,0],0)]
 for roots,wanted in roots_tests:
  p=[e.Q(1)]
  for root in roots:p=e.mul(p,[e.Q(-root),e.Q(1)])
  assert e.positive_with_multiplicity(p)==wanted,roots
 # Exact rational rotations certify non-diagonal oracle behavior without binary64 rounding.
 R=[[F(3,5),F(-4,5),F(0)],[F(4,5),F(3,5),F(0)],[F(0),F(0),F(1)]];rotations=0
 for eigen in [(-3,1,2),(-2,1,1),(-1,-1,2),(0,0,0),(-2,0,2),(2,3,4)]:
  A=[[e.Q(sum(R[i][k]*eigen[k]*R[j][k]for k in range(3)))for j in range(3)]for i in range(3)]
  for w in [F(0),F(1),F(2),F(3),F(1,2)]:assert e.sturm_middle_gt_matrix(A,w)==(3*sorted(eigen)[1]-sum(eigen)>w);rotations+=1
 # Check direct characteristic coefficients against derived invariants, using actual radical entries.
 identities=0
 for c in inputs['cases'][750:780]:
  x,w=e.inputs(list(map(float.fromhex,c['mandel'])),float.fromhex(c['width']));a,b,c0,u,v,z=x;h=e.Q(0,F(1,2));A=[[e.Q(a),h*u,h*z],[h*u,e.Q(b),h*v],[h*z,h*v,e.Q(c0)]];t=a+b+c0;S=[[3*A[i][j]-(e.Q(t)if i==j else e.Q())for j in range(3)]for i in range(3)];poly=e.characteristic(S);aa,bb,cc=[3*v-t for v in x[:3]];uu,vv,zz=[3*v for v in x[3:]];J=(aa*aa+bb*bb+cc*cc+uu*uu+vv*vv+zz*zz)/2;D=e.Q(aa*bb*cc-(aa*vv*vv+bb*zz*zz+cc*uu*uu)/2,uu*vv*zz/2)
  assert poly==[-D,e.Q(-J),e.Q(),e.Q(1)];identities+=1
 bad=[([],0),([0.]*5,0),([0.]*7,0),([0.]*6,-1),([0.]*6,True),([0.]*6,None),([0.]*6,float('nan')),([0.]*6,float('inf')),([0.]*6,-float('inf'))]
 for slot in range(6):
  for poison in [float('nan'),float('inf'),-float('inf'),None,True]:
   v=[0.]*6;v[slot]=poison;bad.append((v,0))
 invalid=0
 for fn in [e.invariant_middle_gt,e.sturm_middle_gt]:
  for v,w in bad:
   try:fn(v,w)
   except ValueError:invalid+=1
   else:raise AssertionError('invalid input accepted')
 return {'version':'centered-middle-design-checks-0.1','pass':True,'literal_cases':len(rows),'known_expected':known,'original_tresca_trial_tensors':sum(r['group']=='original-tresca-trial'for r in rows),'metamorphic_checks':metamorphic,'root_multiplicity_checks':len(roots_tests),'exact_rotations':rotations,'coefficient_identities':identities,'invalid_rejections':invalid,'failed_reversal':{'upper':lookup['failed-reversal/1.0'],'lower_via_negation':lookup['failed-reversal/-1.0']},'rows':rows,'builds':0,'material_calls':0}
if __name__=='__main__':
 report=run();(P/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
