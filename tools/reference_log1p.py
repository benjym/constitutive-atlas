"""Independent stdlib Decimal oracle for actual binary64 log(1+x), d/dx.
No Atlas imports. Precision 500/650 preserves 1+x for min binary64 subnormal.
"""
import argparse, hashlib, json, math, pathlib, sys
from decimal import Decimal, localcontext
VERSION='decimal-log1p-binary64-v1'
PRECISIONS=(500,650)
def oracle(x, precision=650):
    if type(x) is not float or not math.isfinite(x) or x<=-1:
        raise ValueError('finite binary64 float x > -1 required')
    if type(precision) is not int or precision<400:
        raise ValueError('at least 400 digits required')
    with localcontext() as ctx:
        ctx.prec=precision
        exact=Decimal.from_float(x)
        one_plus=Decimal(1)+exact
        value=one_plus.ln()
        derivative=Decimal(1)/one_plus
        if x==0 and math.copysign(1,x)<0: value=Decimal('-0')
        return value,derivative

def inputs():
    small=math.ulp(0.)
    xs=[0.,-0.,small,-small,2*small,-2*small,sys.float_info.min,-sys.float_info.min]
    for x in (1e-300,1e-200,1e-100,1e-20,2.**-53,1e-12,.125,.5): xs.extend((x,-x))
    xs.extend((math.nextafter(-1.,0.),math.nextafter(math.nextafter(-1.,0.),0.),-.9999999,-.99,-.75,1.,2.,3.,7.,1e8,2.**53,1e100,1e300,sys.float_info.max))
    return xs

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def corpus():
    rows=[]
    for i,x in enumerate(inputs()):
        low=oracle(x,500); high=oracle(x,650)
        refinements=[]
        with localcontext() as ctx:
            ctx.prec=700
            for a,b in zip(low,high):
                diff=abs(a-b)
                refinements.append({'absolute':str(diff),'relative':str(diff/abs(b)) if b else '0'})
        rows.append({'id':f'log1p-{i:02d}','x':x,'x_hex':x.hex(),'value':float(high[0]),'derivative':float(high[1]),'decimal_value':str(high[0]),'decimal_derivative':str(high[1]),'precision_refinement':refinements})
    return {'version':VERSION,'definition':'value=ln(1+x); derivative=1/(1+x); exact Decimal.from_float(x), including signed zero convention','precisions':list(PRECISIONS),'scope':'Independent scalar value and unseeded derivative oracle; no AD seed products or model/integration admission','cases':rows,'case_count':len(rows),'invalid_cases':[{'kind':'domain','x':-1.},{'kind':'domain','x':math.nextafter(-1.,-math.inf)},{'kind':'nonfinite-token','x':'NaN'},{'kind':'nonfinite-token','x':'+Infinity'},{'kind':'nonfinite-token','x':'-Infinity'},{'kind':'wrong-type','x':True},{'kind':'wrong-type','x':0}], 'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
    args.output.write_text(json.dumps(corpus(),indent=2,allow_nan=False)+'\n')
