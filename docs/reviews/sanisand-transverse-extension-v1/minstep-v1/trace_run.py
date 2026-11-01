"""Observe the frozen integrator with sys.settrace; never replace its arithmetic."""
from collections import Counter,deque
from contextlib import contextmanager
from decimal import Decimal as D
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;P=HERE.parent;ROOT=P.parents[2]
spec=importlib.util.spec_from_file_location('frozen_transverse_study',P/'study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(value):
 if isinstance(value,D):return str(value)
 if isinstance(value,(list,tuple,deque)):return [encode(x) for x in value]
 if isinstance(value,dict):return {str(k):encode(v) for k,v in value.items()}
 return value


class Observer:
 def __init__(self,destination):
  self.destination=destination;self.attempts=0;self.unsupported=Counter();self.recent=deque(maxlen=24);self.failure=None;self.partial=None
  lines,start=inspect.getsourcelines(study.advance)
  self.loop_line=next(start+i for i,s in enumerate(lines) if 'if accepted+rejected' in s)
  lines,start=inspect.getsourcelines(study.variational)
  self.sample_line=next(start+i for i,s in enumerate(lines) if 'matrix,diag=coefficients' in s)
 def save(self,name,data):
  (self.destination/name).write_text(json.dumps(encode(data),indent=2)+'\n')
 def trace(self,frame,event,arg):
  if event=='call':return self.trace if frame.f_code in (study.advance.__code__,study.variational.__code__) else None
  local=frame.f_locals
  if frame.f_code is study.advance.__code__:
   if event=='line' and frame.f_lineno==self.loop_line:
    self.attempts+=1
    self.recent.append({key:local[key] for key in ['t','target','h','accepted','rejected','error'] if key in local})
    if self.attempts%1000==0:self.save('progress.json',{'attempts':self.attempts,'last':self.recent[-1],'unsupported':dict(self.unsupported)})
   if event=='exception':
    exc=arg[1]
    if isinstance(exc,study.law.Unsupported):self.unsupported[str(exc)]+=1
    if isinstance(exc,ValueError) and str(exc)=='diagnostic minimum step':
     self.failure={key:local[key] for key in ['t','target','h','accepted','rejected','error','tolerance','variable_relative','scales','y','high','low'] if key in local}
     self.failure.update(attempts=self.attempts,unsupported_exceptions=dict(self.unsupported),recent=list(self.recent))
     self.save('failure.json',self.failure)
  elif frame.f_code is study.variational.__code__:
   if event=='line' and frame.f_lineno==self.sample_line:
    self.save('progress.json',{'attempts':self.attempts,'sample_index':local['index'],'parameter':local['t'],'accepted':local['accepted'],'rejected':local['rejected'],'unsupported':dict(self.unsupported)})
   if event=='exception' and isinstance(arg[1],ValueError) and str(arg[1])=='diagnostic minimum step':
    self.partial={key:local[key] for key in ['samples','precision','tolerance','entry','end','p0','e','v','k','accepted','rejected'] if key in local}
    self.save('partial.json',self.partial)
  return self.trace
 @contextmanager
 def active(self):
  previous=sys.gettrace();sys.settrace(self.trace)
  try:yield
  finally:sys.settrace(previous)


def main(destination):
 for path,expected in load(HERE/'freeze.json')['files'].items():assert sha(ROOT/path)==expected,path
 destination.mkdir(parents=True,exist_ok=False);policy=load(HERE/'policy.json');inputs=study.load(study.REF/'inputs.json');case=next(c for c in inputs['cases'] if c['id']==policy['case']);observer=Observer(destination)
 try:
  with observer.active():result=study.variational(case,inputs['parameters'],policy['precision'],policy['tolerance'])
  observer.save('result.json',{'status':'completed','result':result});return 0
 except Exception as exc:
  observer.save('result.json',{'status':'failed','exception':repr(exc),'original_source_unchanged':sha(P/'study.py'),'attempts':observer.attempts})
  print(repr(exc),flush=True);return 2


if __name__=='__main__':raise SystemExit(main(Path(sys.argv[1])))
