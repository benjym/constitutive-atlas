"""Saved-only numerical audit of the independent transverse diagnosis."""
from decimal import Decimal as D,localcontext
import json
from pathlib import Path
import sys
from study import load


def require(test,message):
 if not test:raise ValueError(message)


def audit(data,policy):
 require(data['candidate_integrations']==0,'unexpected candidate integration')
 require(len(data['variational'])==len(policy['cases'])*3,'variation run count')
 require(len(data['nonlinear'])==8,'nonlinear run count')
 require(all(r['status']=='completed' for r in data['variational']+data['nonlinear']),'study run failed')
 require(all(x['derivative_components']==144 and D(x['maximum_scaled_derivative_difference'])<D('1e-24') for x in data['analytic_derivative_checks']),'analytic/full-law derivative agreement')
 worst_precision=worst_refinement=D(0);rows=[]
 with localcontext() as ctx:
  ctx.prec=100
  for case in policy['cases']:
   runs={(r['precision'],r['tolerance']):r for r in data['variational'] if r['case']==case}
   require(set(runs)=={(80,'1e-10'),(80,'1e-12'),(100,'1e-12')},'variation identity')
   p=temporal=D(0)
   for a,b,c in zip(runs[(80,'1e-10')]['samples'],runs[(80,'1e-12')]['samples'],runs[(100,'1e-12')]['samples']):
    require(abs(D(a['parameter'])-D(c['parameter']))<D('1e-70') and abs(D(b['parameter'])-D(c['parameter']))<D('1e-70'),'sample coordinates')
    for low,fine,precise in zip(a['variation'],b['variation'],c['variation']):
     scale=max(D(1),abs(D(precise)));p=max(p,abs(D(fine)-D(precise))/scale);temporal=max(temporal,abs(D(low)-D(precise))/scale)
   require(p<=D(policy['numerical_audit']['precision_variation_relative_difference']),'variation precision audit')
   require(temporal<=D(policy['numerical_audit']['fine_medium_variation_relative_difference']),'variation refinement audit')
   worst_precision=max(worst_precision,p);worst_refinement=max(worst_refinement,temporal)
   fine=runs[(100,'1e-12')];end=fine['samples'][-1];eigen=[D(s['diagnostics']['transverse_2x2_positive_eigenvalue']) for s in fine['samples'][1:] if s['diagnostics']['transverse_2x2_positive_eigenvalue'] is not None]
   extension=case.startswith('extension-')
   require(all(D(s['diagnostics']['transverse_2x2_determinant'])<0 for s in fine['samples'][1:]) if extension else all(D(s['diagnostics']['transverse_2x2_determinant'])>0 for s in fine['samples'][1:]),'analytic determinant sign')
   rows.append({'case':case,'scaled_stress_difference_gain':end['variation'][0],'alpha_difference_gain':end['variation'][1],'fabric_difference_gain':end['variation'][2],
                'maximum_instantaneous_growth_eigenvalue':str(max(eigen)) if eigen else None,'arithmetic_relative_difference':str(p),'refinement_relative_difference':str(temporal)})
  nonlinear_rows=[];worst_swap=D(0)
  for case in policy['nonlinear_cases']:
   p0=D(case.split('-p')[-1])
   for epsilon in policy['nonlinear_epsilon']:
    runs={r['sign']:r for r in data['nonlinear'] if r['case']==case and r['epsilon']==epsilon};require(set(runs)=={-1,1},'signed perturbation identity')
    a,b=runs[-1],runs[1];swap=D(0)
    for sa,sb in zip(a['samples'],b['samples']):
     x=list(map(D,sa['state_cartesian']));y=list(map(D,sb['state_cartesian']))
     for offset in [0,9,18]:
      for i in range(3):
       for j in range(3):
        pi=[0,2,1][i];pj=[0,2,1][j]
        # Proper rotation x->-x, y->z,z->y.
        sign=(-1 if i==0 else 1)*(-1 if j==0 else 1)
        delta=abs(sign*x[offset+3*pi+pj]-y[offset+3*i+j])/(p0 if offset==0 else 1);swap=max(swap,delta)
    require(swap<=D(policy['numerical_audit']['nonlinear_opposite_sign_swap_scaled_error']),'opposite-sign proper-rotation audit')
    worst_swap=max(worst_swap,swap)
    nonlinear_rows.append({'case':case,'epsilon':epsilon,'positive_endpoint_scaled_transverse':b['samples'][-1]['scaled_transverse'],
                           'negative_endpoint_scaled_transverse':a['samples'][-1]['scaled_transverse'],'opposite_sign_swap_error':str(swap),
                           'maximum_absolute_yield_excess_over_p0':str(max(abs(D(s['yield_excess_over_p0'])) for r in [a,b] for s in r['samples']))})
 return {'independent_diagnostic_audit_pass':True,'candidate_integrations':0,'variation_runs':18,'nonlinear_runs':8,'analytic_derivative_components':sum(x['derivative_components'] for x in data['analytic_derivative_checks']),
         'maximum_arithmetic_relative_difference':str(worst_precision),'maximum_refinement_relative_difference':str(worst_refinement),'maximum_opposite_sign_swap_error':str(worst_swap),'variational_rows':rows,'nonlinear_rows':nonlinear_rows,
         'scope':'Empirical diagnosis of selected full-tensor project law and its antisymmetric linearization; no original native accuracy failure is superseded and no scientific admission.'}


if __name__=='__main__':print(json.dumps(audit(load(Path(sys.argv[1])),load(Path(__file__).with_name('policy.json'))),indent=2))
