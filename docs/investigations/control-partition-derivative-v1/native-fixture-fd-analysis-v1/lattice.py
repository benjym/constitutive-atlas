from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from pathlib import Path
import json,math
D=Path(__file__).resolve().parent
from analyze import base,residual

def derivative(precision):
 with localcontext()as ctx:
  ctx.prec=precision;q=Decimal;z=[q(x)for x in base];p=sum(z[:3])/3;u=[(z[i]-(p if i<3 else 0))/p for i in range(6)];r=sum(x*x for x in u).sqrt();n=[x/r for x in u];j=1
  dn=[-(q(int(i==j))-n[i]*n[j])/r for i in range(6)];sqrt2=q(2).sqrt();sqrt6=q(6).sqrt();S=(q(2)/3).sqrt()
  grad=[3*(n[0]**2+(n[3]**2+n[5]**2)/2),3*(n[1]**2+(n[3]**2+n[4]**2)/2),3*(n[2]**2+(n[4]**2+n[5]**2)/2),3*((n[0]+n[1])*n[3]+n[4]*n[5]/sqrt2),3*((n[1]+n[2])*n[4]+n[3]*n[5]/sqrt2),3*((n[2]+n[0])*n[5]+n[3]*n[4]/sqrt2)]
  dt=sqrt6*sum(a*b for a,b in zip(grad,dn));cubic=sum(x**3 for x in n[:3])+q('1.5')*((n[0]+n[1])*n[3]**2+(n[1]+n[2])*n[4]**2+(n[2]+n[0])*n[5]**2)+3/sqrt2*n[3]*n[4]*n[5];t=sqrt6*cubic;cd=q('.07')/q('4.2');dg=2*cd*(1-cd)*dt/(1+cd-(1-cd)*t)**2
  psi=q('.65')-q('.8')+q('.025')*(p/q(160000)).ln();dD=q('2.64')*(S*q('4.2')*psi*dg-n[j]);G=q(31400000)*(p/q(100000))**q('.6')
  return z[13]*(2*G*dn[0]+G*dD)

a=derivative(70);b=derivative(100);lattice=[]
with localcontext()as ctx:
 ctx.prec=70
 for h in ['5e-11','2.5e-11']:
  spacing=Decimal(2)**-37/(2*Decimal(h));k=(a/spacing).to_integral_value(rounding=ROUND_HALF_EVEN);nearest=k*spacing;budget=Decimal('3e-5')*max(1,abs(a),abs(nearest));gap=abs(nearest-a)
  lattice.append(dict(h=h,ulp='2^-37 Pa',spacing=str(spacing),nearest_fd=str(nearest),minimum_absolute_error=str(gap),original_budget=str(budget),impossible_to_pass_at_source_derivative=gap>budget))
result=dict(identity='source-analytic-residual-binary64-lattice-v1',row=0,column=8,analytic_derivative70=str(a),analytic_derivative100=str(b),decimal_difference=str(abs(a-b)),lattice=lattice,binade_assumption='both raw endpoint row0 residuals have magnitude between32768 and65536Pa',compiled_calls=0)
(D/'lattice-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
