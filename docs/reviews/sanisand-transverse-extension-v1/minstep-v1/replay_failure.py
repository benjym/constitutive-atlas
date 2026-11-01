"""Re-evaluate the saved last rejected RK trial, without advancing/committing state."""
from decimal import Decimal as D,localcontext
import json
from pathlib import Path
import sys
from trace_run import study


def replay(directory):
 failure=json.loads((directory/'failure.json').read_text());partial=json.loads((directory/'partial.json').read_text());stages=[]
 with localcontext() as ctx:
  ctx.prec=partial['precision'];y=list(map(D,failure['y']));h=D(failure['recent'][-2]['h']);e=D(partial['e']);p0=D(partial['p0']);v=list(map(D,partial['v']));k={key:D(value) for key,value in partial['k'].items()}
  assert D(failure['recent'][-2]['t'])==D(failure['t'])
  def fn(state):
   matrix,_=study.coefficients(state[:27],v,e,k,p0)
   diag=study.law.rates(state[:27],v,e,k,True)
   stages.append({'dilatancy':str(diag['dilatancy']),'plastic_multiplier_rate':str(diag['plastic_loading']),'fabric_rate_factor':str(k['cz']*max(D(0),-diag['plastic_loading']*diag['dilatancy'])),'variation':list(map(str,state[27:]))})
   return study.law.rates(state[:27],v,e,k)+[sum(matrix[i][j]*state[27+j] for j in range(3)) for i in range(3)]
  high,low=study.law.rk(y,h,fn);assert high==list(map(D,failure['high'])) and low==list(map(D,failure['low']))
  errors=[abs(a-b)/(max(D(scale),abs(a)) if i>=27 else D(scale)) for i,(a,b,scale) in enumerate(zip(high,low,failure['scales']))]
  assert max(errors)==D(failure['error'])
  worst=max(range(len(errors)),key=errors.__getitem__)
  global_amplitude=max(D(1),*(abs(x) for x in high[27:]))
  normalized_global_error=max(abs(a-b)/global_amplitude for a,b in zip(high[27:],low[27:]))
  return {'last_rejected_trial_exactly_reproduced':True,'trial_parameter':failure['t'],'trial_h':str(h),'next_h':failure['h'],'minimum_h':'1e-30','worst_component':worst,
          'worst_component_identity':'fabric yy-minus-zz variation' if worst==29 else 'other',
          'original_error':str(max(errors)),'original_tolerance':failure['tolerance'],
          'parent_variation':failure['y'][27:],'high_variation':list(map(str,high[27:])),'low_variation':list(map(str,low[27:])),
          'comparison_only_global_variation_error':str(normalized_global_error),'global_variation_amplitude':str(global_amplitude),'stages':stages,
          'interpretation':'A zero fabric variation is activated as dilatancy changes sign within the trial. The original componentwise error norm uses denominator1 for that newly activated component while other variations are enormous. This is a diagnostic error-control scaling failure, not evidence of a constitutive singularity. Alternative norm is descriptive only and was not used to accept a step or pass any original gate.',
          'new_integration_commits':0,'candidate_calls':0}


if __name__=='__main__':print(json.dumps(replay(Path(sys.argv[1])),indent=2))
