from pathlib import Path
import json,hashlib,struct,sys,copy,subprocess
P=Path(__file__).parent;S=P/'snapshot';sys.path.insert(0,str(S))
from assess_paths import assess
from assess_parity import assess as parity
root=Path('/Users/bmar5496/code/constitutive-atlas');old=root/'catalogue/investigations/mc-laboratory-preview-v1'
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
def read(p):return json.loads(p.read_text())
reqs=read(S/'requests.json');inputs=read(S/'source-input.json');refs=read(S/'reference/reference-p360.json');cat=read(S/'generated/models.json');rows=read(S/'source-ideal.json')
check('14 immutable corpus paths',len(reqs)==len(inputs['paths'])==14)
check('source input unchanged', (S/'source-input.json').read_bytes()==(old/'source-input.json').read_bytes())
check('source reference unchanged',(S/'reference/reference-p360.json').read_bytes()==(old/'reference/reference-p360.json').read_bytes())
for name in ('models.hpp','models.json'):check('generated unchanged '+name,(S/'generated'/name).read_bytes()==(old/'generated'/name).read_bytes())
oldreq=read(old/'requests.json');paths={p['id']:p for p in inputs['paths']}
for r,o in zip(reqs,oldreq):
 check(r['id']+' historical metadata unchanged',{k:v for k,v in r.items()if k not in ('mode','loading_version','controls_bits_csv')}=={k:v for k,v in o.items()if k!='mode'})
 bits=r['controls_bits_csv'].split(',');vals=[struct.unpack('>d',bytes.fromhex(x))[0]for x in bits];p=paths[r['id']]
 check(r['id']+' exact target bits',[x.hex()for x in vals]==['0x0.0p+0']+p['control_targets'])
 check(r['id']+' RN deltas exact',[(b-a).hex()for a,b in zip(vals,vals[1:])]==p['control_deltas'])
 check(r['id']+' valid length/version/protocol',len(vals)==r['steps']+1 and r['loading_version']=='laboratory-controls-0.1' and r['protocol']==p['protocol'] and r['mode']=='run-controls')
pol=read(S/'acceptance-paths.json');op=read(old/'acceptance-paths.json')
check('all quantitative policy fields unchanged',all(pol[k]==v for k,v in op.items()if k not in ('identity','control_uncertainty','claims')))
check('parity assessor unchanged',(S/'assess_parity.py').read_bytes()==(root/'catalogue/investigations/mc-preview-envelope-v2/assess_parity.py').read_bytes())
solver=(S/'solver.hpp').read_text();original=(S/'production-old-solver.hpp').read_text()
check('initial guard only solver change',solver.replace('!domain(model,initial,p,true)','!domain(model,initial,p)')==original)
check('guard precedes initial point',solver.index('!domain(model,initial,p,true)')<solver.index('run.points.push_back(committed)'))
check('same controller exact difference', 'control-previous.control,lateral,previous.strain.v[0],de,result,settings)'in solver)
api=(S/'api-main.cpp').read_text();check('serializer model ID string','<<quote(id)'in api);check('explicit envelope excludes legacy target','if(controls){o<<",\\\"api_version' in api and 'else o<<",\\\"target' in api)
extra=[]
def reject(name,mutation):
 v=copy.deepcopy(rows);r=json.loads(v[1]['raw']);mutation(r);v[1]['raw']=json.dumps(r)
 try:assess(v,reqs,refs,cat)
 except Exception:extra.append({'name':name,'rejected':True})
 else:extra.append({'name':name,'rejected':False});(P/(name+'.json')).write_text(json.dumps(v));raise AssertionError(name)
reject('signed-zero-bits',lambda r:r['loading']['controls'].__setitem__(0,-0.0))
reject('signed-zero-point',lambda r:r['points'][0].update(control=-0.0))
reject('nan-loading',lambda r:r['loading']['controls'].__setitem__(1,float('nan')))
reject('bool-control',lambda r:r['loading']['controls'].__setitem__(0,False))
reject('fractional-steps',lambda r:r.update(steps=float(r['steps'])))
reject('bool-protocol',lambda r:r.update(protocol=False))
reject('altered-q-channel',lambda r:r['points'][1].update(q=1e9))
reject('missing-bits',lambda r:r['loading'].pop('controls_bits'))
reject('reordered-bits',lambda r:r['loading']['controls_bits'].reverse())
reject('extra-point',lambda r:r['points'].append(r['points'][-1]))
# Independently prove parity is tighter than source accuracy on a permissible stress offset.
b=copy.deepcopy(rows);v=json.loads(b[1]['raw']);pt=v['points'][1];pt['state'][0]+=1e-4;pt['p']=sum(pt['state'][:3])/3;pt['q_signed']=pt['state'][0]-.5*(pt['state'][1]+pt['state'][2]);pt['q']=abs(pt['q_signed']);b[1]['raw']=json.dumps(v)
check('offset remains inside source budget',assess(b,reqs,refs,cat)['passed'])
try:parity(rows,b,reqs)
except AssertionError:check('independent pair parity rejects offset',True)
else:check('independent pair parity rejects offset',False)
(P/'checks.json').write_text(json.dumps({'passed':True,'source_checks':checks,'extra_corruptions':extra,'compiled_observations':0},indent=2)+'\n')
print(json.dumps({'passed':True,'source_checks':len(checks),'extra_corruptions':len(extra)}))
