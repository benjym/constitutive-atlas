"""Post-observation algebraic diagnostic of the retained reversal, no material execution."""
from pathlib import Path
from fractions import Fraction as F
import json,struct,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def bits(v):return [struct.pack('>d',float(x)).hex()for x in v]
def run():
 spec=importlib.util.spec_from_file_location('diagnostic_exact',ROOT/'docs/reviews/certified-spectral-range-v1/exact.py');exact=importlib.util.module_from_spec(spec);spec.loader.exec_module(exact)
 inputs=json.loads((P/'inputs.json').read_text());c=inputs['cases'][0];out={}
 for backend in ['native','wasm']:
  r=json.loads((P/(backend+'-responses.jsonl')).read_text().splitlines()[0])['response'];parent=r['points'][-1];z=list(map(F.from_float,parent['state']));control=F.from_float(parent['control']);da=F.from_float(c['controls'][len(r['points'])])-control
  _,lam,mu,k=map(F.from_float,c['parameters']);width=2*k;oldq=z[0]-z[1];qtrial=oldq+2*mu*da;mean=sum(z[:3])/3+(lam+2*mu/3)*da;q=min(width,max(-width,qtrial));new=[mean+2*q/3,mean-q/3,mean-q/3,F(0),F(0),F(0)]+[z[6]+(qtrial-q)/(3*mu),z[7]-(qtrial-q)/(6*mu),z[8]-(qtrial-q)/(6*mu),*z[9:]];rounded=list(map(float,new));member=exact.range_le(rounded[:6],float(width));assert member==exact.sturm_range_le(rounded[:6],float(width))
  # Exact boundary-to-boundary elastic jump from the actual saved parent.
  assert oldq==-width and qtrial==width and new[6:]==z[6:]
  out[backend]={'failed_step':len(r['points']),'parent_bits':bits(parent['state']),'parent_source_admissible':exact.range_le(parent['state'][:6],float(width)),'axial_increment':str(da),'old_q':str(oldq),'trial_q':str(qtrial),'yield_width':str(width),'exact_solution':[str(v)for v in new],'nearest_binary64_solution':rounded,'nearest_solution_bits':bits(rounded),'nearest_solution_source_admissible':member,'plastic_increment_exactly_zero':True,'failure_diagnostics_available':False}
 return {'version':'tresca-laboratory-reversal-diagnostic-0.1','scope':'post-observation exact rational check, no candidate execution or gate revision','backends':out,'conclusion':'Exact actual-parent boundary-to-boundary elastic solution exists. Saved API output lacks the failed Newton iterate/diagnostics; cause of rejection is not proven. Next isolate the same parent and increment with frozen instrumentation, without changing model, constraint, tolerances or iteration budget.'}
if __name__=='__main__':(P/'reversal-diagnostic.json').write_text(json.dumps(run(),indent=2)+'\n');print(json.dumps({b:run()['backends'][b]['nearest_solution_source_admissible']for b in ['native','wasm']}))
