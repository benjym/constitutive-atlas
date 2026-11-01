"""Post-observation saved diagnosis; never changes the frozen assessor or gates."""
import copy,json
from decimal import Decimal as D,localcontext
from assess import HERE,ROOT,OLD,audit,coordinates,load,previous

def report(data):
 try:
  audit(data)
 except ValueError as exc:failure=str(exc)
 else:raise AssertionError('expected retained frozen-assessor failure absent')
 assert failure=='reference coordinates'
 for r in data['runs']:coordinates(r)
 old=load(OLD/'continuous-v1/study.json.gz');composite=copy.deepcopy(old)
 for i,r in enumerate(composite['variational']):
  if r['case']==data['case']:
   assert r['status']=='failed'
   composite['variational'][i]=next(x for x in data['runs'] if (x['precision'],x['tolerance'])==(r['precision'],r['tolerance']))
 output_audit=previous.audit(composite,load(OLD/'policy.json'))
 reference=load(ROOT/'docs/references/sanisand-project-monotonic-v1/reference-p80-t12.json.gz')
 ref=next(c for c in reference['cases'] if c['id']==data['case'])
 worst_t=worst_base=D(0)
 with localcontext() as ctx:
  ctx.prec=100
  for r in data['runs']:
   for s,b in zip(r['samples'],ref['samples'][1:]):
    worst_t=max(worst_t,abs(D(s['parameter'])-D(b['parameter'])))
    raw=list(map(D,b['state']));expected=[]
    for offset in (0,7,13):
     q=raw[offset:offset+6];expected += [q[0],q[3]/D(2).sqrt(),q[5]/D(2).sqrt(),q[3]/D(2).sqrt(),q[1],q[4]/D(2).sqrt(),q[5]/D(2).sqrt(),q[4]/D(2).sqrt(),q[2]]
    worst_base=max(worst_base,max(abs(D(a)-b)/(D(20000) if i<9 else D(1)) for i,(a,b) in enumerate(zip(s['base_state_cartesian'],expected))))
 return {'kind':'retained-failure-with-separated-output-audit','frozen_v2_assessment_pass':False,'frozen_failure':failure,'completed_new_runs':3,'coordinate_reconstruction_pass':True,'reused_variation_runs':15,'reused_nonlinear_runs':8,'unchanged_output_audit':output_audit,'descriptive_only':{'maximum_reference_parameter_difference':str(worst_t),'maximum_index_matched_base_scaled_difference':str(worst_base),'interpretation':'Index-matched serialized samples only; no passing prospective base-binding claim or changed coordinate gate.'},'original_v1_audit_pass':False,'native_qualification_pass':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(report(load(HERE/'runs/result.json.gz')),indent=2))
