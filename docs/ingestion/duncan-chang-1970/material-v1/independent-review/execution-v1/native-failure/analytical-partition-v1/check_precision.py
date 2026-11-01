from pathlib import Path
from decimal import Decimal
import runpy,json
P=Path(__file__).resolve().parent
run=runpy.run_path(str(P/'analyze.py'))['run']
a=run(100); b=run(160); rows=[]
for x,y in zip(a['rows'],b['rows']):
 for u,v in zip(x['variants'],y['variants']):
  assert u['success'] and v['success']
  assert [(l['depth'],l['de'],l['branch']) for l in u['leaves']]==[(l['depth'],l['de'],l['branch']) for l in v['leaves']]
  delta=max(abs(Decimal(j)-Decimal(k)) for j,k in zip(u['final_state'],v['final_state']))
  assert delta<Decimal('1e-60')
  rows.append({'id':x['id'],'continuation':u['continuation'],'same_partition_and_branches':True,'maximum_final_state_100_160_difference':str(delta)})
print(json.dumps({'pass':True,'rows':rows},indent=2))
