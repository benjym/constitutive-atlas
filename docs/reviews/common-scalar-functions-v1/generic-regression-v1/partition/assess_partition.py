"""Saved-only independent linear branch/derivative and exact partition arithmetic."""
from pathlib import Path
from fractions import Fraction as Q
import json,math,sys

def assess(rows):
 checks={};r=rows[0];z=[0.]*6+[50/64];checks['coverage']=len(rows)==8;checks['exact_replay']=all(r['exact_replay'] for r in rows[:5])
 checks['alternate']=r['ok'] and r['substeps']==3 and r['attempted']==12 and r['retries']==1 and r['first']==9 and r['discarded']==r['first'] and r['attempted']==r['substeps']+r['discarded']<=20000
 checks['counts']=len(r['increments'])==len(r['fractions'])==r['substeps'] and len(r['discarded_increments'])==len(r['discarded_fractions'])==r['discarded']
 checks['endpoint']=all(abs(a-b)<=2e-10 for a,b in zip(r['state'],[77/96]+[0.]*5+[77/96])) and len(r['state'])==7
 checks['fractions']=all(math.isfinite(f) and f>0 for f in r['fractions']) and abs(sum(r['fractions'])-1)<=1e-14
 state=[Q(0)]*6;h=Q(50,64);weighted=Q(0)
 for inc,f in zip(r['increments'],r['fractions']):
  assert len(inc)==6 and all(math.isfinite(x) for x in inc)
  # Solve each source branch algebraically; exactly one valid root is required.
  roots=[]
  for E in (10,2):
   target=[x+E*Q(float(d)) for x,d in zip(state,inc)]
   if (sum(target[:3])<h)==(E==10):roots.append((target,E))
  if len(roots)!=1:checks['unique_source_root']=False;break
  state,E=roots[0];h=max(h,sum(state[:3]));weighted+=E*Q(float(f))
 else:checks['unique_source_root']=True
 checks['source_endpoints']=all(abs(float(a)-b)<=2e-10 for a,b in zip(state+[h],r['state']))
 checks['loading_sum']=all(abs(sum(Q(float(inc[j])) for inc in r['increments'])-Q(7,64) if j==0 else sum(Q(float(inc[j])) for inc in r['increments']))<=2*Q(sys.float_info.epsilon)*(Q(7,64) if j==0 else 0) for j in range(6))
 a=float(7/64/3);b=float(7/64-a);checks['split_defect']=Q(a)+Q(b)-Q(7/64)==Q(float(r['defect'][0])) and all(x==0 for x in r['defect'][1:])
 tangent=rows[5];expected=[[float(weighted) if i==j else 0. for j in range(6)] for i in range(6)]+[[float(weighted) if j<3 else 0. for j in range(6)]]
 checks['tangent']=tangent['state']==r['state'] and tangent['ok'] and len(tangent['matrix'])==7 and all(len(row)==6 for row in tangent['matrix']) and all(abs(x-y)<=2e-10 for aa,bb in zip(tangent['matrix'],expected) for x,y in zip(aa,bb)) and abs(float(weighted)-22/3)<=2e-10
 checks['original_failed']=not rows[6]['ok'] and rows[6]['substeps']==r['first']==9
 checks['global_budget_witness']=rows[3]['first']==9 and rows[3]['attempted']==rows[3]['discarded']==rows[3]['substeps']==10 and rows[3]['retries']==1
 checks['leaf_loading']=True
 for increments,fractions in [(r['increments'],r['fractions']),(r['discarded_increments'],r['discarded_fractions'])]:
  for inc,f in zip(increments,fractions):
   for j,v in enumerate(inc):
    expected=Q(float(f))*(Q(7,64) if j==0 else 0)
    checks['leaf_loading'] &= math.isfinite(f) and f>0 and abs(Q(float(v))-expected)<=8*Q(sys.float_info.epsilon)*abs(expected)
 for i,budget in [(1,20000),(2,1),(3,10),(4,20000)]:
  c=rows[i];checks['rollback_'+str(i)]=not c['ok'] and c['state']==([100000.]*3+[0.]*4 if i==4 else z) and c['attempted']<=budget
 checks['depth_and_budget_no_retry']=rows[1]['retries']==rows[2]['retries']==0
 checks['guards']=rows[7]=={'kind':'guards','normal':True,'underflow':False,'nonfinite':False}
 return dict(pass_=all(checks.values()),checks=checks,source_endpoint=[float(x) for x in state+[h]],source_derivative=float(weighted))
if __name__=='__main__':
 result=assess([json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines()]);print(json.dumps(result,indent=2));sys.exit(0 if result['pass_'] else 1)
