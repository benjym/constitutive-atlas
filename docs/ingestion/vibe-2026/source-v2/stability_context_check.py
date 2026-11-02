"""Exact invariant check and independent illustrative near-SBS initialization; no integration."""
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
import json

def determinant(A):
 return sum(A[0][j]*(A[1][(j+1)%3]*A[2][(j+2)%3]-A[1][(j+2)%3]*A[2][(j+1)%3]) for j in range(3))
def check():
 cases=0
 for n in range(1,31):
  p=F(100+n); z=[[F(n,7),F(n+1,11),F(-n,13)],[F(n+1,11),F(-2*n,7),F(n+2,17)],[F(-n,13),F(n+2,17),F(n,7)]]
  sig=[[z[i][j]-(p if i==j else 0) for j in range(3)] for i in range(3)]
  I1=sum(sig[i][i] for i in range(3));I2=(sum(x*x for row in sig for x in row)-I1*I1)/2;I3=determinant(sig)
  z2=sum(x*x for row in z for x in row);z3=determinant(z)
  assert (9*I3+I1*I2)/(I3+I1*I2)==(3*p*z2+9*z3)/(8*p**3-p*z2+z3);cases+=1
 with localcontext() as c:
  c.prec=70
  e=D('.725');s=D(10000000);target=D('1.005');pe=D(1000)*((D('1.43')-(1+e).ln())/D('.1')).exp()
  def context(pnet):
   pm=pnet+s;em=D('.55')*(-(D('.9')*(pm/D(150000000)).ln()).exp()).exp();eM=(e-em)/(1+em)
   se=D(2000000)*D('.2')/eM*D('.9');S=1-(-(D('1.1')*(se/s).ln()).exp()).exp();pM=pnet+S*s;OA=pe/pM
   eA=((1+e).ln()+D('.1')*OA.ln()).exp()-1;re=(e-em)/(eA-em)
   return {'pnet_Pa':pnet,'s_Pa':s,'T_K':D(294),'e':e,'a_scan':D(0),'pm_Pa':pm,'em':em,'eM':eM,'se_Pa':se,'S_M':S,'Sr':S+em/e*(1-S),'pM_Pa':pM,'pe_Pa':pe,'OA':OA,'eA':eA,'re':re,'fm':1-re**5,'OA_to_minus_1_over_Iv':(-OA.ln()/D('.004')).exp()}
  lo=D(1);hi=D(10000000)
  assert context(lo)['OA']>target>context(hi)['OA']
  for _ in range(240):
   mid=(lo+hi)/2
   if context(mid)['OA']>target:lo=mid
   else:hi=mid
  v=context((lo+hi)/2)
  assert abs(v['OA']-target)<D('1e-65') and 0<v['re']<1 and 0<v['S_M']<v['Sr']<1 and v['eM']>0
  return {'status':'pass','stable_Fm_exact_symmetric_matrix_cases':cases,'identity_derivation':'For sigma=-p I+z, tr(z)=0: I1=-3p; I2=-3p^2+(z:z)/2; I3=-p^3+p(z:z)/2+det(z). Substitute in A30; no approximate regularization.','decimal_precision':70,'near_SBS_context':{k:str(x) for k,x in v.items()},'scope':'Algebraically constructed unsaturated hydrostatic example, not source measured preparation, reference integration, or relaxation result; source Table1/2 calibration and A14-A35. Isotropic extension must be reviewed before execution.'}
if __name__=='__main__': print(json.dumps(check(),indent=2))
