"""Independent scalar accepted-partition explanation of frozen failed clay2014 study.
No Atlas/source-rate/production integration imports; historical negative remains failed.
"""
import argparse,hashlib,json,math
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='clay2014-scalar-midpoint-diagnostic-v1'
REPORT='catalogue/investigations/clay2014-paths-v1/native.json'
RAW='catalogue/investigations/clay2014-paths-v1/native.transport.jsonl'
PINS={'catalogue/investigations/clay2014-paths-v1/native.json': '8f9971fd1e620f54b9fbcf1dd886ca87b7a75f572690fb0de846ed3eca2cdb11', 'catalogue/investigations/clay2014-paths-v1/native.transport.jsonl': '030a8359d68218f4c87a172ac1c3be10cf71cf9ea4a6bbd9210a789b090e8add', 'catalogue/investigations/clay2014-path-reference-v1/reference.json': '7f7b2f8fb0eb04294fcd9959470a4dd7d342a38ea403dc1b18bc6d338cd5f301'}
def require(ok,message):
 if not ok:raise ValueError(message)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def same(a,b):
 if type(a)is bool or type(b)is bool:return type(a)is type(b)and a==b
 if type(a)in(int,float)and type(b)in(int,float):return math.isfinite(a)and math.isfinite(b)and a==b
 if type(a)is not type(b):return False
 if type(a)is dict:return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def read_inputs(root):
 held={p:(root/p).read_bytes()for p in PINS}
 for p,blob in held.items():require(hashlib.sha256(blob).hexdigest()==PINS[p],'immutable input hash mismatch: '+p)
 parse=lambda x:json.loads(x,parse_constant=lambda v:(_ for _ in()).throw(ValueError('nonfinite JSON')))
 r=parse(held[REPORT]);raw=[parse(x)for x in held[RAW].splitlines()]
 require(r['transport_sha256']==PINS[RAW],'raw file receipt')
 calls=[{'request':{'mode':'describe'},'response':r['runtime_descriptor']}]+[c for g in r['records']for c in g['calls']]+[c for p in r['failure_probes']for c in(p,p['recovery'])]
 require(len(raw)==len(calls)==295,'complete historical transport')
 for row,c in zip(raw,calls):
  require(row['backend']=='native'and row['mode']=='persistent_stream','historical stream identity')
  require(same(row['request'],c['request'])and same(parse(row['stdout']),c['response']),'historical raw request/response binding')
 return r
def rates(z,v,p):
 pressure,e=z;la=p[3];ka=p[4];sinphi=math.sin(p[2]);af=math.sqrt(3)*(3-sinphi)/(2*math.sqrt(2)*sinphi)
 alpha=math.log((la-ka)/(la+ka)*(3+af*af)/(af*math.sqrt(3)))/math.log(2)
 pe=p[0]*math.exp((p[5]-math.log1p(e))/la)
 return [pressure/2*((1/la+1/ka)*v+(1/la-1/ka)*(pressure/pe)**alpha*abs(v)),-(1+e)*v]
def midpoint(z,v,p,defect=False):
 k1=rates(z,v,p);mid=[x+.5*k for x,k in zip(z,k1)];k2=rates(mid,v,p);out=[x+k for x,k in zip(z,k2)]
 if not defect:return out
 k3=rates(out,v,p);return out,[(a-2*b+c)/6 for a,b,c in zip(k1,k2,k3)]
def build(root=ROOT):
 r=read_inputs(Path(root))
 groups=[g for g in r['records']if g['case']=='isotropic-ratios-hydro-reversal'and g['partitions']==7]
 rows=[]
 for group in groups:
  initial=group['calls'][0]['request']['initial'];z=[initial[0],initial[6]];decimal_w=Decimal.from_float(initial[6])+1;totalV=Decimal(0);calls=[]
  with localcontext()as ctx:
   ctx.prec=100;decimal_w=Decimal.from_float(initial[6])+1
   for c in group['calls']:
    request=c['request'];p=request['parameters'];strain=request['strain'];v=sum(strain[:3]);fracs=c['response']['diagnostics']['increment_fractions'];z0=z.copy();dv=sum((Decimal.from_float(x)for x in strain[:3]),Decimal(0))
    for f in fracs:
     z=midpoint(z,v*f,p)
     x=dv*Decimal.from_float(f);decimal_w*=1-x+x*x/2
    totalV+=dv;exact_w=(Decimal.from_float(initial[6])+1)*(-totalV).exp()
    observed=c['response']['state'];calls.append(dict(volume=v,fractions=fracs,scalar_midpoint_minus_native=[z[0]-observed[0],z[1]-observed[6]],decimal_midpoint_void_minus_native=float(decimal_w-1-Decimal.from_float(observed[6])),signed_void_truncation=float(decimal_w-exact_w)))
  rows.append(dict(tolerance=group['tolerance'],calls=calls))
 first=groups[0]['calls'][0]['request'];z=[first['initial'][0],first['initial'][6]];p=first['parameters'];v=sum(first['strain'][:3]);full=midpoint(z,v,p);half,hd=midpoint(z,v/2,p,True);two,td=midpoint(half,v/2,p,True)
 components=dict(full_vs_two=[abs(a-b)for a,b in zip(full,two)],half_endpoint_defect=list(map(abs,hd)),second_endpoint_defect=list(map(abs,td)))
 scaled={k:[a/p[1],b]for k,(a,b)in components.items()};estimated=max(x for v in scaled.values()for x in v)
 uniform=[]
 for count in(2,4,8,16):
  group=groups[0];initial=group['calls'][0]['request']['initial'];z=[initial[0],initial[6]];end=[]
  for i,c in enumerate(group['calls']):
   v=sum(c['request']['strain'][:3]);p=c['request']['parameters']
   for j in range(count):z=midpoint(z,v/count,p)
   if(i+1)%7==0:end.append(dict(segment=(i+1)//7,state=z.copy()))
  uniform.append(dict(uniform_substeps_per_piece=count,endpoints=end))
 out=dict(uniform_scalar_midpoint_diagnostic=uniform,native_report_sha256=PINS[REPORT],recorded_partition_replays=rows,first_piece_stepdoubling_and_endpoint_defects=components,scaled_first_piece_candidates=scaled,estimated_first_piece_acceptance_error=estimated,interpretation='Analytic scalar midpoint reproduction at recorded fractions diagnoses plateau/cancellation; not fresh engine execution or admission')
 return dict(version=VERSION,input_pins=dict(PINS),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),claims=dict(original_study_passed=False,scientific_admission=False,production_solver_executed=False,rigorous_error_bound=False),**out)
def verify(document,root=ROOT):
 require(canonical(document)==canonical(build(root)),'diagnostic differs from fresh immutable-input scalar replay')
 return document
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'fresh output required');a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(build(),indent=2,allow_nan=False)+'\n')
