"""Retain pure Python instantaneous oracle cases; no Atlas/author code imports."""
import argparse,hashlib,json,math,pathlib
from decimal import Decimal,localcontext
from tools.reference_barodesy2017 import SOILS,VERSION,rate,rotate,UnsupportedDomain,constants
Q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
REFLECTION=[[0.,1.,0.],[1.,0.,0.],[0.,0.,1.]]
BASE={'sigma':[120000.,80000.,100000.,2000.,-3000.,4000.],'e':.8}
SHEAR=[.125,-.0625,-.0625,.08,-.04,.03]
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def scaled(x,c):return [v*c for v in x]
def cases():
 out=[];rejections=[]
 def add(name,soil,state,de):
  p=SOILS[soil];request=dict(state=state,increment=de,parameters=p);lo=rate(state,de,p,80);hi=rate(state,de,p,140)
  value_error=max(abs(a-b)for a,b in zip(lo['sigma_rhs']+[lo['e_rhs']],hi['sigma_rhs']+[hi['e_rhs']]))
  decimal_difference=None
  if lo['expm'] is not None:
   with localcontext()as ctx:
    ctx.prec=160
    decimal_difference=str(max(abs(Decimal(a)-Decimal(b))for a,b in zip(lo['expm']['decimal_normalized'],hi['expm']['decimal_normalized'])))
  out.append(dict(id=soil.lower()+'-'+name,request=request,input_sha256=digest(request),oracle=hi,precision_refinement={'digits':[80,140],'rate_absolute_max':value_error,'normalized_expm_decimal_max':decimal_difference}))
 for soil,p in SOILS.items():
  for pressure in (1000.,100000.,500000.):
   state=dict(sigma=[pressure]*3+[0.]*3,e=math.exp(p['N'])*(pressure/1000.)**(-p['lambda_star'])-1)
   add('ncl-compression-'+str(int(pressure)),soil,state,[1/3]*3+[0.]*3)
  for name,de in [('oedometric',[1.,0.,0.,0.,0.,0.]),('noncoaxial',SHEAR),('reversal',scaled(SHEAR,-1)),('zero',[0.]*6),('hydro-compression',[1/3]*3+[0.]*3),('hydro-expansion',[-1/3]*3+[0.]*3)]:add(name,soil,BASE,de)
  for name,q in [('rotation',Q),('reflection',REFLECTION)]:add(name,soil,dict(sigma=rotate(BASE['sigma'],q),e=BASE['e']),rotate(SHEAR,q))
  for c in (.001,1000.):add('positive-scale-'+str(c),soil,BASE,scaled(SHEAR,c))
  for sign in (1.,-1.):
   for epsilon in (1e-2,1e-4,1e-6,1e-8,1e-10,1e-12):
    for pname,perturb in [('diagonal',[1.,-1.,0.,0.,0.,0.]),('offdiagonal',[0.,0.,0.,1.,-.5,.25])]:
     base=[sign/3]*3+[0.]*3;add('nearhydro-'+str(sign)+'-'+str(epsilon)+'-'+pname,soil,BASE,[x+epsilon*y for x,y in zip(base,perturb)])
  c2=constants(p)['c2'];delta=math.sqrt(6*c2*c2/(9+2*c2*c2));q=math.sqrt(1-delta*delta/3);de=[-delta/3+q/math.sqrt(2),-delta/3-q/math.sqrt(2),-delta/3,0.,0.,0.]
  try:rate(BASE,de,p);raise AssertionError('expected unsupported nearK0actualbinaryinput')
  except UnsupportedDomain as e:rejections.append(dict(id=soil.lower()+'-near-source-K0-rounded-input',request=dict(state=BASE,increment=de,parameters=p),message=str(e),claim='Actual rounded input rejected; not asserted exact sourceK0'))
 return dict(version=VERSION,scope='Independent instantaneous source-body research oracle, not integration/model admission',formula_source=dict(doi='10.1007/s11440-016-0458-4',pdf_sha256='bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15',selected='bodyEqs1–10 with2p/sigma_star; footnote13voidclosure',differences_retained=['App41uses6p','objective-rateWTprint','zero/hydrocontinuationsdeclared','noauthorcodeequivalence']),basis='Mandelxx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz',parameters='Fourexplicitradian/dimensionlessinputs;1000Pareferencepressurefixed',numeric_scope='Scalarloading/constants/statearithmetic binary64; matrixexponentialandnormalization independentadaptiveDecimal80/140digits onactualbinary64matrixargument; refinementnotrigorouserrorcertificate',support='ResearchSPDcompressionstress,e>=0,finiteconstants/density; exactMandelexponentialargumentFrobenius<=64;K0unsupported;nogeneralspin',cases=out,rejected_cases=rejections,case_count=len(out))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output',type=pathlib.Path);args=ap.parse_args();data=cases();args.output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');print(data['case_count'],'retained rates;',len(data['rejected_cases']),'rejections')
