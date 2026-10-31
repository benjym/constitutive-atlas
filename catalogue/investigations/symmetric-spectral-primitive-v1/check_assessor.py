"""Synthetic assessor contract checks, explicitly not solver evidence."""
from decimal import Decimal,localcontext
import copy,json
import study

def ideal_rows(requests):
 ref=study.load(study.P/'reference/reference-p360.json.gz');cases={c['input']['id']:c for c in ref['cases']};rows=[]
 with localcontext()as ctx:
  ctx.prec=500
  for r in requests:
   base={'id':r['id'],'operation':r['operation'],'kind':r['kind'],'status':r['expected_status'],'ok':r['expected_status']=='ok','failed_output_preserved':r['expected_status']!='ok'}
   if not base['ok']:base['output']=[{'value':-777,'derivatives':[123+j for j in range(38)]}];rows.append(base);continue
   c=cases[r['case']];op=r['operation'];name=study.selector(op)
   if op.startswith('projector_'):values=study.cart_to_mandel(c['reference']['selected'][name]['projector'])
   else:values=[study.scalar_reference(c,op)]
   out=[{'value':float(v)}for v in values]
   if r['kind']=='jet':
    for x in out:x['derivatives']=[0.]*38
    if not op.endswith('_value'):
     for column in range(38):
      if op.startswith('projector_'):der=study.cart_to_mandel(c['reference']['selected'][name]['directions'][column]['projector'])
      elif op in ('upper_sum','lower_sum'):der=[Decimal(c['reference']['pair_sums']['upper'if op=='upper_sum'else'lower']['directions'][column])]
      else:der=[Decimal(c['reference']['selected'][name]['directions'][column]['eigenvalue'])]
      for x,v in zip(out,der):x['derivatives'][column]=float(v)
   base['output']=out;rows.append(base)
 return rows

def check():
 requests=study.load(study.P/'requests.json.gz');rows=ideal_rows(requests);baseline=study.assess(rows);assert baseline['passed'],baseline['failures'][:3]
 probes=[]
 for label,edit in [('wrong-status',lambda x:x.update(status='wrong')),('wrong-primal',lambda x:x['output'][0].update(value=1e100)),('false-failure-preservation',lambda x:x.update(failed_output_preserved=False))]:
  changed=copy.deepcopy(rows);i=next(i for i,r in enumerate(changed)if (r['ok']if label!='false-failure-preservation'else not r['ok']));edit(changed[i]);assert not study.assess(changed)['passed'];probes.append(label)
 # Value-only transport is checked independently from ordinary derivative accuracy.
 changed=copy.deepcopy(rows);i=next(i for i,r in enumerate(changed)if r['ok']and r['kind']=='jet'and r['operation']=='max_value');changed[i]['output'][0]['derivatives'][37]=1;assert not study.assess(changed)['passed'];probes.append('value-only-leak-column37')
 changed=copy.deepcopy(rows);i=next(i for i,r in enumerate(changed)if r['ok']and r['kind']=='jet'and r['operation']=='projector_max');changed[i]['output'][3]['derivatives'][37]=1e100;assert not study.assess(changed)['passed'];probes.append('projector-shear-column37')
 changed=copy.deepcopy(rows);i=next(i for i,r in enumerate(changed)if r['id']=='mixed-scale-mid_value-double');changed[i]['output'][0]['value']=0;assert not study.assess(changed)['passed'];probes.append('mixed-scale-middle-exactness')
 return {'ideal_synthetic_transport_passed':True,'corruption_probes_rejected':probes,'requests':len(requests),'solver_calls':0,'limits':'Tests assessor acceptance/rejection only; ideal values are assembled from reference, not compiled results.'}
if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
