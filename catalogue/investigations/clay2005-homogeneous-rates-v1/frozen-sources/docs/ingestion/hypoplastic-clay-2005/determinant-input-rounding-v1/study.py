"""Independent exact-input normalization diagnostic; no Atlas imports/material rates."""
import argparse,hashlib,json,math
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decimal(x):return D(x.numerator)/D(x.denominator)
def rne(x):return F(float(x))
def det(v):
 x,y,z,u,v,w=map(decimal,v);q=D(2).sqrt();a=[[x,u/q,w/q],[u/q,y,v/q],[w/q,v/q,z]]
 return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def encode(x):
 if isinstance(x,D):return str(x)
 if isinstance(x,F):return {'numerator':str(x.numerator),'denominator':str(x.denominator),'binary64_hex':float(x).hex()}
 if isinstance(x,list):return [encode(v)for v in x]
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 return x

def run(root,packet):
 f=json.loads((packet/'prospective-freeze.json').read_text())
 for n,s in f['files'].items():assert sha(root/n)==s,n
 rows=[]
 for case in f['cases']:
  sigma=[F(int(v['numerator']),int(v['denominator']))for v in case['exact_binary64_stress']];trace=sum(sigma[:3],F());t=rne(trace);reciprocal=rne(1/t)
  routes={'target_exact_normalized':[v/trace for v in sigma],'trace_only_exact_components':[v/t for v in sigma],'components_RNE_exact_trace':[rne(v/trace)for v in sigma],'components_RNE_direct_division':[rne(v/t)for v in sigma],'components_RNE_reciprocal_multiply':[rne(v*reciprocal)for v in sigma]}
  k=math.frexp(max(abs(float(v))for v in sigma))[1];power=F(2)**k;K=[v/power for v in sigma];assert all(F(float(v))==v for v in K),'power2normalization loststoredvalue';traceK=sum(K[:3],F());tK=rne(traceK)
  outputs={};errors=[]
  for prec in f['policy']['precisions']:
   try:
    with localcontext()as ctx:
     ctx.prec=prec;rawdet=det(sigma);target=rawdet/(decimal(trace)**3);values={n:det(v)for n,v in routes.items()};dk=det(K);values['power2_exact_ratio']=dk/(decimal(traceK)**3)
     dk_float=float(dk);assert math.isfinite(dk_float)
     values['power2_rounded_scalars_ratio']=decimal(F(dk_float))/(decimal(tK)**3)
     diagnostics={n:{'value':v,'signed_relative_error':(v-target)/target,'relative_error':abs(v-target)/abs(target),'reciprocal_factor_signed_error':target/v-1 if v else None}for n,v in values.items()}
     outputs[prec]={'raw_cartesian_det_sigma':rawdet,'target':target,'routes':diagnostics,'power2_detK':dk,'power2_detK_RNE_hex':dk_float.hex()}
   except Exception as exc:errors.append({'precision':prec,'exception':type(exc).__name__,'message':str(exc)})
  convergence=[]
  if 160 in outputs and 320 in outputs:
   with localcontext()as ctx:
    ctx.prec=340
    for name in outputs[320]['routes']:
     lo=outputs[160]['routes'][name]['value'];hi=outputs[320]['routes'][name]['value'];e=abs(lo-hi)/abs(hi)if hi else abs(lo-hi);convergence.append({'route':name,'relative_difference':e,'passed':e<=D('1e-120')})
   assert outputs[160]['power2_detK_RNE_hex']==outputs[320]['power2_detK_RNE_hex']
  row={'id':case['id'],'stress_literals':case['stress_literals'],'trace_exact':trace,'trace_RNE':t,'reciprocal_RNE':reciprocal,'trace_RNE_relative_error_exact_fraction':(t-trace)/trace,'normalized_input_routes':routes,'power2':{'exponent':k,'K_exact':K,'traceK_exact':traceK,'traceK_RNE':tK,'inputscaling_exact':True},'precision_results':outputs,'convergence':convergence,'errors':errors,'all_converged':not errors and len(convergence)==7 and all(v['passed']for v in convergence)}
  rows.append(encode(row))
 return {'version':'clay2005-determinant-input-rounding-v1-results','input_freeze_sha256':sha(packet/'prospective-freeze.json'),'script_sha256':sha(Path(__file__)),'cases':rows,'all_cases_converged':all(c['all_converged']for c in rows),'compiled_calls':0,'Atlas_math_execution':False,'full_source_rates_evaluated':False,'new_accuracy_gate':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.root,a.packet);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print('cases',len(r['cases']),'allconverged',r['all_cases_converged'])
