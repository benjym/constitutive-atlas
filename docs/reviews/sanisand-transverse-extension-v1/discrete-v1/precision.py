"""Independent high-precision replay of stored-prefix map products; no material calls."""
from decimal import Decimal as D,localcontext
from pathlib import Path
import json
import audit as study


def replay():
 policy=study.load(study.HERE/'precision-policy.json');saved=study.load(study.HERE/'assessment.json');native=study.ROOT/'docs/reviews/sanisand-v03-monotonic-v1/native-results';index=study.load(native/'index.json');model=study.load(study.ROOT/'docs/reviews/sanisand-v03-research-freeze-v1/model.json');by_id={r['id']:r for r in saved['paths']};worst=D(0);rows=[]
 with localcontext() as ctx:
  ctx.prec=policy['replay_precision']
  for item in index['records']:
   if item['id'] not in by_id:continue
   receipt=study.load(native/item['file']);pars=dict(zip(model['parameters'],[float(x) for x in receipt['request']['args'][1].split(',')]));points=receipt['response']['points'];gain=[D(1),D(0)];count=0
   for i,point in enumerate(points[1:],1):
    if not study.symmetric(point['state']) or not study.symmetric(points[i-1]['state']):break
    _,inverse=study.inverse2(study.matrix(point['state'],pars,D(20000)))
    gain=[sum(inverse[j][k]*gain[k] for k in range(2)) for j in range(2)];count+=1
   assert count==by_id[item['id']]['exact_symmetric_prefix_steps']
   err=max(abs(x-D(y))/max(D(1),abs(x)) for x,y in zip(gain,by_id[item['id']]['prefix_endpoint_gain']));worst=max(worst,err)
   rows.append({'id':item['id'],'gain':list(map(str,gain)),'relative_gain_difference':str(err)})
  assert worst<=D(policy['maximum_relative_gain_difference'])
 return {'arithmetic_replay_pass':True,'cases':len(rows),'maximum_relative_gain_difference':str(worst),'rows':rows,'candidate_integrations':0,'compiled_calls':0}


if __name__=='__main__':print(json.dumps(replay(),indent=2))
