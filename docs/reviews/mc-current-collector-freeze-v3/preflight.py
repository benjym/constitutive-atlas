from pathlib import Path
import json,copy,struct,math
from assess_paths import assess
from assess_binding import verify
verify()
from assess_parity import assess as parity
P=Path(__file__).parent
requests=json.loads((P/'requests.json').read_text());reference=json.loads((P/'reference/reference-p360.json').read_text());catalogue=json.loads((P/'generated/models.json').read_text());refs={x['id']:x for x in reference['paths']}
frames=json.loads((P/'manufactured-frames.json').read_text())['frames']
rows=[{'id':'describe','raw':json.dumps(catalogue)}]+[{'id':req['id'],'request':req,'raw':json.dumps(frame['result'])}for req,frame in zip(requests,frames)]
result=assess(rows,requests,reference,catalogue);p=parity(rows,rows,requests)
corruptions=[]
def reject(label,mutate):
 test=copy.deepcopy(rows);value=json.loads(test[1]['raw']);mutate(test,value);test[1]['raw']=json.dumps(value)
 try:assess(test,requests,reference,catalogue)
 except(Exception):corruptions.append(label)
 else:raise RuntimeError('false pass '+label)
reject('wrong model ID',lambda rows,r:r.update(model='linear-elastic'))
reject('object instead of string model',lambda rows,r:r.update(model={'id':'mohr-coulomb'}))
reject('wrong catalogue',lambda rows,r:r.update(catalogue_hash='wrong'))
reject('wrong API',lambda rows,r:r.update(api_version='wrong'))
reject('wrong loading version',lambda rows,r:r['loading'].update(version='wrong'))
reject('wrong encoding',lambda rows,r:r['loading'].update(encoding='wrong'))
reject('wrong bit echo',lambda rows,r:r['loading']['controls_bits'].__setitem__(1,'0000000000000000'))
reject('wrong numeric loading',lambda rows,r:r['loading']['controls'].__setitem__(1,0))
reject('wrong point control',lambda rows,r:r['points'][1].update(control=0))
reject('wrong protocol',lambda rows,r:r.update(protocol=4))
reject('wrong point count',lambda rows,r:r['points'].pop())
reject('missing strain components',lambda rows,r:r['points'][1].update(strain=[]))
reject('oversized strain components',lambda rows,r:r['points'][1]['strain'].append(0))
reject('wrong stress',lambda rows,r:r['points'][1]['state'].__setitem__(0,1e9))
reject('wrong strain',lambda rows,r:r['points'][1]['strain'].__setitem__(0,1))
reject('nonfinite state',lambda rows,r:r['points'][1]['state'].__setitem__(0,float('nan')))
reject('invalid source settings',lambda rows,r:r['integration_settings'].update(residual_tolerance=1))
reject('legacy target fiction',lambda rows,r:r.update(target=.01))
reject('legacy cycles fiction',lambda rows,r:r.update(cycles=1))
reject('empty diagnostics',lambda rows,r:r['points'][1].update(iterations=-1))
reject('boolean setting',lambda rows,r:r['integration_settings'].update(max_iterations=True))
reject('boolean stress',lambda rows,r:r['points'][0]['state'].__setitem__(3,False))
reject('boolean point control',lambda rows,r:r['points'][0].update(control=False))
reject('boolean elapsed',lambda rows,r:r.update(elapsed_ms=False))
reject('negative elapsed',lambda rows,r:r.update(elapsed_ms=-1))
reject('success message wrong type',lambda rows,r:r.update(message=False))
reject('missing diagnostics',lambda rows,r:r['points'][1].pop('error'))
reject('boolean request',lambda rows,r:rows[1]['request'].update(protocol=False))
# Descriptor equality and raw literal -0 require independent row mutations.
for label in ['descriptor boolean','negative-zero point control','negative-zero loading control']:
 test=copy.deepcopy(rows)
 if label=='descriptor boolean':
  d=json.loads(test[0]['raw']);key=next(iter(d['models'][0]['parameters']));d['models'][0]['parameters'][key]['min']=False;test[0]['raw']=json.dumps(d)
 else:
  d=json.loads(test[1]['raw'])
  if label=='negative-zero point control':d['points'][0]['control']=-0.0
  else:d['loading']['controls'][0]=-0.0
  test[1]['raw']=json.dumps(d).replace('-0.0','-0')
 try:assess(test,requests,reference,catalogue)
 except Exception:corruptions.append(label)
 else:raise RuntimeError('false pass '+label)
(P/'source-ideal.json').write_text(json.dumps(rows,indent=2)+'\n')
(P/'preflight-results.json').write_text(json.dumps({'source_ideal':result,'source_parity':p,'negative_checks':len(corruptions),'rejected_corruptions':corruptions,'compiled_observations':0},indent=2)+'\n')
print(json.dumps({'passed':True,'source_ideal_points':result['points'],'negative_checks':len(corruptions)}))
