"""Independent numerical differentiation of local Decimal constitutive evaluation.
No Atlas/native derivative implementation is executed. Not a rounding certificate.
"""
import json,sys
from decimal import Decimal,localcontext
from tools import reference_barodesy2017_hydro as ref

def main():
 results=[]
 with localcontext()as ctx:
  ctx.prec=140
  sig=list(map(Decimal,['120000','80000','100000','2000','-3000','4000']));e=Decimal('.8')
  for soil,pars in ref.SOILS.items():
   for sign in(-1,1):
    s=Decimal(sign)/10;E=[s]*3+[Decimal(0)]*3;j=ref.hydro_jacobian(sig,e,s,pars,140)
    for col in range(13):
     steps=[]
     for exponent in(14,20,26):
      h=Decimal(10)**(-exponent)*(max(Decimal(1),abs(sig[col]))if col<6 else Decimal(1)if col==6 else abs(s));a=sig.copy();b=sig.copy();ea=eb=e;u=E.copy();v=E.copy()
      if col<6:a[col]+=h;b[col]-=h
      elif col==6:ea+=h;eb-=h
      else:u[col-7]+=h;v[col-7]-=h
      fa=ref.evaluate(a,ea,u,pars,140)['rate'];fb=ref.evaluate(b,eb,v,pars,140)['rate'];fd=[(x-y)/(2*h)for x,y in zip(fa,fb)]
      err=max(abs(x-j[i][col])/max(Decimal(1),abs(j[i][col]))for i,x in enumerate(fd));steps.append(dict(relative_step_exponent=-exponent,scaled_error=str(err)))
     results.append(dict(soil=soil,sign=sign,column=col,steps=steps))
 out=dict(kind='independent-directional-differentiation-diagnostic',cases=len(results),maximum_scaled_error_fine=max(float(r['steps'][-1]['scaled_error'])for r in results),results=results)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
