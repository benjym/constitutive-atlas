"""Independent homogeneous variation with exact power-of-ten coordinate rescaling."""
from decimal import Decimal as D,localcontext
import gzip,hashlib,importlib.util,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'docs/reviews/sanisand-transverse-extension-v1'
spec=importlib.util.spec_from_file_location('frozen_transverse',OLD/'study.py');law=importlib.util.module_from_spec(spec);spec.loader.exec_module(law)


def load(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check_pins():
 for name,expected in load(HERE/'freeze.json')['files'].items():assert sha(ROOT/name)==expected,name


def rescale(state,exponent):
 """Only homogeneous variation coordinates change. Base27 stays bit-for-bit intact."""
 assert len(state)==30
 largest=max(abs(x) for x in state[27:])
 if not largest:return state.copy(),exponent
 shift=largest.adjusted()
 out=state[:27]+[x.scaleb(-shift) for x in state[27:]]
 return out,exponent+shift


def reconstructed(state,exponent):return [x.scaleb(exponent) for x in state[27:]]


def step_to(y,t,target,h,fn,scales,tolerance,exponent):
 accepted=rejected=rescales=0;min_h=None
 while t<target:
  if accepted+rejected>=20000:raise ValueError('diagnostic attempt budget')
  h=min(h,target-t)
  if h<D('1e-30'):raise ValueError('diagnostic minimum step')
  min_h=h if min_h is None else min(min_h,h)
  try:
   high,low=law.law.rk(y,h,fn)
   error=max(abs(a-b)/(max(scale,abs(a)) if i>=27 else scale) for i,(a,b,scale) in enumerate(zip(high,low,scales)))
  except law.law.Unsupported:rejected+=1;h/=2;continue
  if error>tolerance:rejected+=1;h*=max(D('.1'),D('.9')*(tolerance/error)**D('.2'));continue
  t+=h;accepted+=1;old_exponent=exponent;y,exponent=rescale(high,exponent);rescales+=int(old_exponent!=exponent)
  h*=2 if error==0 else min(D(2),max(D('.2'),D('.9')*(tolerance/error)**D('.2')))
 return y,t,h,exponent,accepted,rejected,rescales,min_h


def run(case,raw,precision,tolerance,progress):
 with localcontext() as ctx:
  ctx.prec=precision;k,p0,e,v,t,y=law.starting(case,raw);end=D(case['end_parameter']);entry=t
  y += [D(1),D(0),D(0)];exponent=0;h=(end-entry)/100;scales=[p0]*9+[D(1)]*21;samples=[];accepted=rejected=rescales=0;minimum=None
  def fn(state):
   matrix,_=law.coefficients(state[:27],v,e,k,p0)
   return law.law.rates(state[:27],v,e,k)+[sum(matrix[i][j]*state[27+j] for j in range(3)) for i in range(3)]
  for index in range(17):
   target=entry+(end-entry)*index/16
   if index:
    y,t,h,exponent,a,r,s,m=step_to(y,t,target,h,fn,scales,D(tolerance),exponent);accepted+=a;rejected+=r;rescales+=s;minimum=m if minimum is None else min(minimum,m)
   matrix,diag=law.coefficients(y[:27],v,e,k,p0)
   samples.append({'parameter':str(t),'variation':list(map(str,reconstructed(y,exponent))),
                   'normalized_variation':list(map(str,y[27:])),'decimal_exponent':exponent,
                   'base_state_cartesian':list(map(str,y[:27])),
                   'matrix':[[str(x) for x in row] for row in matrix],
                   'diagnostics':{key:str(x) if x is not None else None for key,x in diag.items()}})
   progress({'precision':precision,'tolerance':tolerance,'sample':index,'accepted':accepted,'rejected':rejected,'exponent':exponent,'minimum_h':str(minimum)})
  return {'case':case['id'],'precision':precision,'tolerance':tolerance,'method':'power10-homogeneous-variation-v2','status':'completed','samples':samples,'accepted':accepted,'rejected':rejected,'rescales':rescales,'minimum_h':str(minimum)}


def main(destination):
 check_pins();destination.mkdir(parents=True,exist_ok=False);policy=load(HERE/'policy.json');inputs=load(law.REF/'inputs.json');case=next(c for c in inputs['cases'] if c['id']==policy['case'])
 def progress(value):
  with (destination/'progress.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')
 rows=[]
 for precision,tolerance in policy['configs']:
  try:r=run(case,inputs['parameters'],precision,tolerance,progress)
  except Exception as exc:r={'case':case['id'],'precision':precision,'tolerance':tolerance,'status':'failed','exception':repr(exc)}
  rows.append(r)
  (destination/f'run-{precision}-{tolerance}.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0))
  print(precision,tolerance,r['status'],flush=True)
 result={'kind':'independent-homogeneous-variation-v2','case':case['id'],'new_candidate_calls':0,'new_configs':3,'runs':rows}
 (destination/'result.json.gz').write_bytes(gzip.compress((json.dumps(result,indent=2)+'\n').encode(),mtime=0))
 return 0 if all(r['status']=='completed' for r in rows) else 2


if __name__=='__main__':raise SystemExit(main(Path(sys.argv[1])))
