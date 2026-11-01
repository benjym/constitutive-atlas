"""Independent scalar/invariant source residual. No Atlas imports or kernels."""
from pathlib import Path
from decimal import Decimal,localcontext
import math,json,hashlib
D=Path(__file__).resolve().parent
# Source p260-263: n=(s/p-alpha)/norm, g interpolation, h hardening,
# endpoint stress/alpha/void residual and Fischer-Burmeister consistency.
def residual(z,decimal=False):
 Q=Decimal if decimal else float
 c=lambda x:Q(str(x));sq=lambda x:x.sqrt()if decimal else math.sqrt(x);log=lambda x:x.ln()if decimal else math.log(x)
 zero=c(0);one=c(1);p=sum(z[:3])/c(3);dev=[z[i]-(p if i<3 else zero)for i in range(6)];u=[dev[i]/p-z[7+i]for i in range(6)];rr=sq(sum(x*x for x in u));n=[x/rr for x in u];S=sq(c(2)/c(3))
 # tr(N^3) in the Mandel basis, direct scalar invariant expansion.
 cubic=sum(x*x*x for x in n[:3])+c('1.5')*((n[0]+n[1])*n[3]**2+(n[1]+n[2])*n[4]**2+(n[2]+n[0])*n[5]**2)+c(3)/sq(c(2))*n[3]*n[4]*n[5]
 angular=sq(c(6))*cubic
 g=lambda r:c(2)*r/(one+r-(one-r)*angular)
 psi=z[6]-c('.8')+c('.025')*log(p/c(160000));dense=max(-psi,zero)
 ab=S*(c('1.14')+g(c(2)/c('3.975'))*c('3.975')*dense-c('.05'))
 ad=S*(c('1.14')+g(c('.07')/c('4.2'))*c('4.2')*psi-c('.05'))
 b=[ab*n[i]-z[7+i]for i in range(6)];bn=sum(b[i]*n[i]for i in range(6));bref=c(2)*S*(c('1.14')+c('3.975')*dense-c('.05'));hard=c(1200)*abs(bn)/(bref-abs(bn));d=c('2.64')*sum((ad*n[i]-z[7+i])*n[i]for i in range(6))
 if psi>zero:d=max(d,zero)
 mod=c(31400000)*(p/c(100000))**c('.6');de=[c(x)for x in ['.00001','-.000005','-.000005','.000003','0','0']];tr=sum(de[:3]);gamma=z[13]
 out=[z[i]-(c(160000)if i<3 else zero)-c(2)*mod*(de[i]-(tr/c(3)if i<3 else zero))-(mod*tr if i<3 else zero)+gamma*(c(2)*mod*n[i]+(mod*d if i<3 else zero))for i in range(6)]
 out+=[z[6]-c('.65')+c('1.65')*tr]
 out +=[z[7+i]-gamma*hard*b[i]for i in range(6)]
 f=(sq(sum((dev[i]-p*z[7+i])**2 for i in range(6)))-S*c('.05')*p)/c(160000)
 out +=[sq(gamma*gamma+f*f)-gamma+f]
 return out
base=['110000','95000','100000','500','0','0','.65','0','0','0','0','0','0','.0001'];scales=[160000]*6+[1]*8

def secant(j,h,prec=70):
 with localcontext()as ctx:
  ctx.prec=prec;z=[Decimal(x)for x in base];plus=z.copy();minus=z.copy();step=Decimal(str(h));delta=step*Decimal(scales[j]);plus[j]+=delta;minus[j]-=delta;rp=residual(plus,True);rm=residual(minus,True)
  return [(a-b)/(2*step)for a,b in zip(rp,rm)],rp,rm

def main():
 rows=[];derivative_stability=0
 for j in range(14):
  exact,_,_=secant(j,'1e-18');check,_,_=secant(j,'1e-18',100);derivative_stability=max(derivative_stability,max(abs(float(a-b))for a,b in zip(exact,check)))
  for level in range(2):
   h=(5e-11 if 7<=j<=9 else 1e-6)/(2**level);z=[float(x)for x in base];plus=z.copy();minus=z.copy();plus[j]+=h*scales[j];minus[j]-=h*scales[j];rp=residual(plus);rm=residual(minus);hi,dp,dm=secant(j,str(h))
   for i in range(14):
    ref=float(exact[i]);fd=(rp[i]-rm[i])/(2*h);rounded=(float(dp[i])-float(dm[i]))/(2*h);budget=3e-5*max(1,abs(ref),abs(fd));quant=(math.ulp(rp[i])+math.ulp(rm[i]))/(4*h)
    rows.append(dict(column=j,row=i,level=level,h=h,source_derivative=ref,float_fd=fd,high_precision_secant=float(hi[i]),float_error=abs(fd-ref),storage_only_fd=rounded,storage_only_error=abs(rounded-ref),budget=budget,ulp_quantization_scale=quant,residual_plus=rp[i],residual_minus=rm[i],within_original_budget=abs(fd-ref)<budget))
 result=dict(identity='native-fixture-source-only-cancellation-v1',rows=rows,decimal70_100_max_difference=derivative_stability,source_float_diagnostic_failures=[x for x in rows if not x['within_original_budget']],compiled_calls=0,gate_changes=False)
 (D/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(rows=len(rows),diagnostic_failures=len(result['source_float_diagnostic_failures']),decimal_stability=derivative_stability,first=result['source_float_diagnostic_failures'][:2])))
if __name__=='__main__':main()
