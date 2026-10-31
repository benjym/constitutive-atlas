from pathlib import Path
import json,copy,struct,math
from assess_paths import assess
from assess_parity import assess as parity
P=Path(__file__).parent
requests=json.loads((P/'requests.json').read_text());reference=json.loads((P/'reference/reference-p360.json').read_text());catalogue=json.loads((P/'generated/models.json').read_text());refs={x['id']:x for x in reference['paths']}
rows=[{'id':'describe','raw':json.dumps(catalogue)}]
for req in requests:
 controls=[struct.unpack('>d',bytes.fromhex(x))[0]for x in req['controls_bits_csv'].split(',')]
 initial=[float(x)for x in req['initial'].split(',')];points=[]
 for control,ref in zip(controls,refs[req['id']]['points']):
  state=[float(x)for x in ref['state']];strain=[float(x)for x in ref['strain']];q=state[0]-.5*(state[1]+state[2]);points.append({'control':control,'strain':strain,'state':state,'p':sum(state[:3])/3,'q':abs(q),'q_signed':q,'u':100000.-.5*(state[1]+state[2])if req['protocol']in(2,3)else 0.,'iterations':0,'substeps':0,'rejected':0,'error':0.})
 r={'ok':True,'message':'','schema_version':'0.1','api_version':'experimental-laboratory-controls-0.1','catalogue_hash':catalogue['sha256'],'model':req['model'],'elapsed_ms':0.,'parameters':[float(x)for x in req['parameters'].split(',')],'initial':initial,'integration_settings':dict(zip(('version','norm','residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),['incremental-settings-0.1','scaled_component_max']+[float(x)for x in req['integration_settings'].split(',')])),'protocol':req['protocol'],'steps':req['steps'],'loading':{'version':req['loading_version'],'encoding':'ieee754-binary64-hex','controls_bits':req['controls_bits_csv'].split(','),'controls':controls},'points':points}
 rows.append({'id':req['id'],'request':req,'raw':json.dumps(r)})
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
(P/'source-ideal.json').write_text(json.dumps(rows,indent=2)+'\n')
(P/'preflight-results.json').write_text(json.dumps({'source_ideal':result,'source_parity':p,'negative_checks':len(corruptions),'rejected_corruptions':corruptions,'compiled_observations':0},indent=2)+'\n')
print(json.dumps({'passed':True,'source_ideal_points':result['points'],'negative_checks':len(corruptions)}))
