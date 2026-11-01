"""Additional saved-only counter/partition audit; original source gate is separate."""
from pathlib import Path
from fractions import Fraction as Q
import json,sys,math

def assess(data):
 failures=[];count=0;retries=0
 def walk(x):
  nonlocal count,retries
  if isinstance(x,list):
   for y in x:walk(y)
  elif isinstance(x,dict):
   if 'stdout' in x and 'args' in x:
    r=json.loads(x['stdout'],parse_int=float);d=r.get('diagnostics');args=x['args']
    if d and 'partition_retries' in d and len(args)==5:
     count+=1
     try:
      ok=r['ok'];n=int(d['substeps']);a=int(d['attempted_substeps']);discard=int(d['discarded_substeps']);budget=int(float(args[4].split(',')[4]));retry=int(d['partition_retries'])
      assert a<=budget and retry in (0,1) and d['partition_committed']==ok
      assert a==n+discard if ok else a==n==discard
      if retry:
       retries+=1;de=[float(v) for v in args[3].split(',')];actual=d['accepted_increment_tensors'];f=d['increment_fractions'];assert len(actual)==len(f)==n and all(math.isfinite(v) and v>0 for v in f)
       assert len(d['partition_defect'])==6
       for inc,fraction in zip(actual+d['discarded_increment_tensors'],f+d['discarded_increment_fractions']):
        assert len(inc)==6 and math.isfinite(fraction) and fraction>0
        for value,parent in zip(inc,de):
         expected=Q(float(fraction))*Q(parent)
         assert math.isfinite(value) and abs(Q(float(value))-expected)<=8*Q(sys.float_info.epsilon)*abs(expected)
       for j,v in enumerate(de):
        left=v/3;right=v-left;defect=Q(left)+Q(right)-Q(v)
        assert Q(float(d['partition_defect'][j]))==defect
        assert abs(defect)<=2*Q(sys.float_info.epsilon)*abs(Q(v))
        if ok:assert abs(sum(Q(float(inc[j])) for inc in actual)-Q(v))<=2*Q(sys.float_info.epsilon)*abs(Q(v))
       if ok:
        assert abs(sum(f)-1)<=1e-12 and len(d['discarded_increment_tensors'])==len(d['discarded_increment_fractions'])==discard
      else:assert discard==0 if ok else discard==a
     except (AssertionError,KeyError,ValueError,TypeError) as e:failures.append(dict(call=count,args=args,error=str(e)))
   for y in x.values():walk(y)
 walk(data)
 return dict(pass_=count>0 and retries>0 and not failures,calls=count,retry_calls=retries,failures=failures)
if __name__=='__main__':
 result=assess(json.loads(Path(sys.argv[1]).read_text()));print(json.dumps(result,indent=2));sys.exit(0 if result['pass_'] else 1)
