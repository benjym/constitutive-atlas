"""Post-observation summary with failed coverage explicit; no revised acceptance gates."""
from decimal import Decimal as D,localcontext
import gzip,json
from pathlib import Path
import sys

def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def summarize(data):
 rows=[]
 with localcontext() as ctx:
  ctx.prec=100
  for case in sorted({r['case'] for r in data['variational']}):
   runs={(r['precision'],r['tolerance']):r for r in data['variational'] if r['case']==case};failed=[r for r in runs.values() if r['status']!='completed']
   if failed:rows.append({'case':case,'status':'failed','failures':failed});continue
   coarse,fine,precise=[runs[k] for k in [(80,'1e-10'),(80,'1e-12'),(100,'1e-12')]];p=temporal=D(0)
   for a,b,c in zip(coarse['samples'],fine['samples'],precise['samples']):
    for x,y,z in zip(a['variation'],b['variation'],c['variation']):
     scale=max(D(1),abs(D(z)));p=max(p,abs(D(y)-D(z))/scale);temporal=max(temporal,abs(D(x)-D(z))/scale)
   rows.append({'case':case,'status':'completed','endpoint_variation':precise['samples'][-1]['variation'],'maximum_arithmetic_relative_difference':str(p),'maximum_refinement_relative_difference':str(temporal)})
  nonlinear=[]
  for case in sorted({r['case'] for r in data['nonlinear']}):
   for epsilon in ['1e-16','1e-24']:
    pair={r['sign']:r for r in data['nonlinear'] if r['case']==case and r['epsilon']==epsilon};a,b=pair[-1],pair[1];worst=D(0);p0=D(case.split('-p')[-1])
    for sa,sb in zip(a['samples'],b['samples']):
     x=list(map(D,sa['state_cartesian']));y=list(map(D,sb['state_cartesian']))
     for offset in [0,9,18]:
      for i in range(3):
       for j in range(3):
        pi,pj=[0,2,1][i],[0,2,1][j];sign=(-1 if i==0 else 1)*(-1 if j==0 else 1)
        worst=max(worst,abs(sign*x[offset+3*pi+pj]-y[offset+3*i+j])/(p0 if offset==0 else 1))
    nonlinear.append({'case':case,'epsilon':epsilon,'signed_endpoints':[a['samples'][-1]['scaled_transverse'],b['samples'][-1]['scaled_transverse']], 'opposite_sign_swap_error':str(worst),
                      'maximum_abs_yield_excess_over_p0':str(max(abs(D(s['yield_excess_over_p0'])) for r in pair.values() for s in r['samples']))})
 return {'kind':'descriptive_completed_and_failed_run_summary','overall_original_audit_pass':False,'variational_completed':sum(r['status']=='completed' for r in data['variational']),'variational_expected':18,'nonlinear_completed':sum(r['status']=='completed' for r in data['nonlinear']),'nonlinear_expected':8,
         'analytic_derivative_components':sum(x['derivative_components'] for x in data['analytic_derivative_checks']),'variational_rows':rows,'nonlinear_rows':nonlinear,'candidate_integrations':0,'limits':'Original audit fails; no failed run excluded to obtain a pass. Nonlinear runs have only one precision/tolerance and cannot provide an independently refined finite-amplitude solution certificate. Minimum-step cause not localized by original receipts.'}
if __name__=='__main__':print(json.dumps(summarize(load(Path(sys.argv[1]))),indent=2))
