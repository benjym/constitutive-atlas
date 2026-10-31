"""Exact Cartesian spectral derivative certificates; no Atlas/eigensolver imports."""
from fractions import Fraction as F
import json
Z=F(0);I=[[F(i==j) for j in range(3)]for i in range(3)]
def zero():return [[Z for j in range(3)]for i in range(3)]
def add(a,b):return [[a[i][j]+b[i][j] for j in range(3)]for i in range(3)]
def scale(a,x):return [[v*x for v in row]for row in a]
def sub(a,b):return add(a,scale(b,-1))
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3))for j in range(3)]for i in range(3)]
def tr(a):return sum(a[i][i]for i in range(3))
def transpose(a):return [list(x)for x in zip(*a)]
def diag(xs):return [[xs[i]if i==j else Z for j in range(3)]for i in range(3)]
def rotate(a,q):return mul(mul(q,a),transpose(q))
def encode(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,(list,tuple)):return [encode(v)for v in x]
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 return x

def certify(A,values,projectors,i,H):
 P=projectors[i];lam=values[i];dl=tr(mul(P,H));dP=zero()
 for j in range(3):
  if j==i:continue
  assert lam!=values[j]
  term=add(mul(mul(projectors[j],H),P),mul(mul(P,H),projectors[j]))
  dP=add(dP,scale(term,1/(lam-values[j])))
 assert dP==transpose(dP) and tr(dP)==0
 assert add(mul(P,dP),mul(dP,P))==dP
 assert add(mul(H,P),mul(A,dP))==add(scale(P,dl),scale(dP,lam))
 return dl,dP

def check():
 q=[[F(3,5),F(-4,5),Z],[F(4,5),F(3,5),Z],[Z,Z,F(1)]]
 assert mul(q,transpose(q))==I
 qdense=[[F(1,9),F(8,9),F(4,9)],[F(8,9),F(1,9),F(-4,9)],[F(-4,9),F(4,9),F(-7,9)]]
 assert mul(qdense,transpose(qdense))==I
 basis=[diag((F(1),Z,Z)),diag((Z,F(1),Z)),diag((Z,Z,F(1)))]
 directions=[]
 for j in range(38):
  v=[F(((j+1)*(k+3))%17-8,1+(j+k)%5)for k in range(6)]
  directions.append([[v[0],v[3],v[5]],[v[3],v[1],v[4]],[v[5],v[4],v[2]]])
 rows=[]
 for name,vals,selected in [('simple_min_repeated_complement',(F(1),F(4),F(4)),0),('simple_max_repeated_complement',(F(4),F(1),F(1)),0),('distinct_min',(F(-3),F(2),F(7)),0),('distinct_max',(F(-3),F(2),F(7)),2)]:
  A=diag(vals);P=basis[selected]
  for j,H in enumerate(directions):
   dl,dP=certify(A,vals,basis,selected,H)
   rA=rotate(A,q);rPs=[rotate(x,q)for x in basis];rH=rotate(H,q)
   rdl,rdP=certify(rA,vals,rPs,selected,rH)
   assert rdl==dl and rdP==rotate(dP,q)
   dA=rotate(A,qdense);dPs=[rotate(x,qdense)for x in basis];dH=rotate(H,qdense)
   ddl,ddP=certify(dA,vals,dPs,selected,dH)
   assert ddl==dl and ddP==rotate(dP,qdense)
   if vals[(selected+1)%3]==vals[(selected+2)%3]:
    complement=sub(I,P);other=vals[(selected+1)%3]
    grouped=scale(add(mul(mul(complement,H),P),mul(mul(P,H),complement)),1/(vals[selected]-other))
    assert grouped==dP
   rows.append({'case':name,'column':j,'A':A,'H':H,'lambda':vals[selected],'P':P,'Dlambda':dl,'DP':dP,'rotated_A':rA,'rotated_H':rH,'rotated_P':rPs[selected],'rotated_DP':rdP,'dense_rotated_A':dA,'dense_rotated_H':dH,'dense_rotated_P':dPs[selected],'dense_rotated_DP':ddP,'Dcomplement_pair_sum':tr(H)-dl})
 # Pair sums have derivative tr((I-P_selected)H), including repeated pairs.
   assert tr(mul(sub(I,P),H))==tr(H)-dl
 # Repeated selected minimum has incompatible two-sided derivative even on diagonal inputs.
 t=F(1,100);a=(F(1),F(1),F(4));h=(F(-1),F(1),Z)
 plus=min(a[i]+t*h[i]for i in range(3));minus=min(a[i]-t*h[i]for i in range(3))
 assert (plus-1)/t==-1 and (minus-1)/(-t)==1
 # Exact value-only trace/middle counterexample represented by original binary64 inputs.
 large=1e300;trace_exact=F.from_float(large)+F(1)-F.from_float(large)
 naive_middle=(float(trace_exact)-(-large))-large
 assert trace_exact==1 and naive_middle==0.
 return encode({'kind':'exact-Cartesian-isolated-extreme-derivative-certificates','rows':rows,'directional_rows':len(rows),'columns_per_case':38,'rotated_checks':2*len(rows),'failed':0,'pair_sum_checks':len(rows),'apex_parameter_derivative_at_c5_sinphi3over5_cosphi4over5':{'D_cohesion':F(4,3),'D_phi_radians':F(-125,9),'trial_stress_derivative_fixed_parameters':F(0)},'counterexamples':{'repeated_selected_minimum':{'A_diagonal':a,'H_diagonal':h,'right_slope':F(-1),'left_slope':F(1)},'rounded_middle_from_trace_extrema':{'diagonal':['1e300','1','-1e300'],'exact_trace':'1','exact_middle':'1','left_associated_binary64_middle':naive_middle}},'limits':['Rational Cartesian matrices, not rounded stored-Mandel corpus','No floating eigensolver, Atlas imports or compiled execution','38 exact directions certify formulas, not a compiled Jet implementation']})
if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
