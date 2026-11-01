"""Remove observational hooks and namespace isolation, recover original source text."""
from pathlib import Path
P=Path(__file__).parent

def normalize(text):return text.replace('namespace atlas_trace','namespace atlas').replace('atlas_trace::','atlas::').replace('"trace/','"atlas/')
def check():
 result={}
 for original in (P/'frozen/cpp/include/atlas').rglob('*.hpp'):
  traced=P/'instrumented/cpp/include/trace'/original.relative_to(P/'frozen/cpp/include/atlas');s=normalize(traced.read_text())
  if original.name=='solver.hpp':
   s=s.replace('#include "trace_models.hpp"\n#include <string>','#include "models.hpp"')
   start=s.index('struct TraceEvent {');end=s.index('inline bool implicit_step(',start);s=s[:start]+s[end:]
   s=s.replace('if(!trace_jacobian(model,x,xn,d,p,r))','if(!evaluate_model(model,x,xn,d,p,r))')
   s=s.replace(' trace_iterate(it,z,residual,jac,err);','').replace(' trace_delta(delta);','').replace(' trace_trial(backtrack,alpha,trial);','')
   s=s.replace('!trace_physical(model,trial,p)||!trace_raw(model,trial,zn,de,p,rt)','!solution_admissible(model,trial,p)||!evaluate_model(model,trial,zn,de,p,rt)')
   s=s.replace('if(trace_descent(scaled_norm(rt,scales),err))','if(scaled_norm(rt,scales)<err)')
  assert s==original.read_text(),str(original);result[str(original.relative_to(P))]=True
 text=normalize((P/'generated/trace_models.hpp').read_text());text='\n'.join(l for l in text.splitlines()if l!='#include "trace_observer.hpp"'and not l.startswith('if(trace_enabled) { DerivedObservation record;'))+'\n'
 assert text==(P/'generated/models.hpp').read_text();result['generated/models.hpp']=True
 return result
if __name__=='__main__':print('Recovered exact original sources:',len(check()))
