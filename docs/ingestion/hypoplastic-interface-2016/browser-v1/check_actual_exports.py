"""Prospective offline verifier of real UI downloads; no engine/browser execution."""
from pathlib import Path
import argparse,hashlib,json,math,sys
MODEL='hvwe2016-reconciled-fixed-local'
DEFINITION='8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce'
PINS={'example.json':'e2aa1b780f1f481257c4a88a1116737e43a64cde610e9db12d9a78af718b5173','package-cases.json':'05e81820c7ecdaf37b314f5a629bab2fa8cc8f5eb6214473cb73688405f23013'}
STATES=['sigma_normal','sigma_plane','tau_x','tau_z','e']
def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 def pairs(items):
  d={}
  for k,v in items:require(k not in d,'Duplicate JSON key: '+k);d[k]=v
  return d
 return json.loads(p.read_text(),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON: '+x)))
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',required=True,type=Path);p.add_argument('--default',required=True,type=Path);p.add_argument('--reset',required=True,type=Path);p.add_argument('--replay',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 base=a.package/'material-point-interface2016/engine-path';identity=load(base/'identity.json');require(identity['model']==MODEL and identity['definition_sha256']==DEFINITION and identity['profile']=='controlled-path-ode-v1','Unexpected package identity')
 for name,h in identity['files'].items():
  require(Path(name).name==name,'Unsafe identity asset path');require(digest(base/name)==h,'Package asset hash differs: '+name)
 for name,h in identity['components'].items():
  require(Path(name).name==name,'Unsafe component path');require(digest(base.parent/name)==h,'Component hash differs: '+name)
 for name,h in PINS.items():require(digest(base/name)==h and identity['files'][name]==h,'Frozen reference changed: '+name)
 example=load(base/'example.json');cases=load(base/'package-cases.json');require(cases['tolerance']=={'stress_absolute_Pa':.2,'void_ratio_absolute':2e-6},'Frozen tolerances changed')
 request={'context':example['context'],'progress':example['advance']['progress'],'controls_end':example['advance']['controls_end'],'samples':40,'settings':[example['execution'][k] for k in ['absolute','relative','min_step','max_step','max_depth','max_trials']]}
 matches=[c for c in cases['cases'] if c['request']['context']==request['context'] and c['request']['progress']==request['progress'] and c['request']['controls_end']==request['controls_end']]
 require(len(matches)==1,'Default reference ambiguous/absent');reference=matches[0]
 require([reference['request']['settings'][k] for k in ['absolute','relative','min_step','max_step','max_depth','max_trials']]==request['settings'],'Reference execution settings differ')
 checks=[];documents={};inputs={}
 for label,path in [('default',a.default),('reset',a.reset),('replay',a.replay)]:
  d=load(path);documents[label]=d;inputs[label]={'path':str(path.resolve()),'sha256':digest(path)}
  require(set(d)=={'kind','model','identity','request','result'},label+': unexpected export fields')
  require(d['kind']=='atlas-interface2016-path-run-v1' and d['model']==MODEL and d['identity']==identity,label+': model/identity mismatch')
  require(d['request']==request,label+': exact qualified default request differs')
  result=d['result'];require(set(result)=={'model','request','points'} and result['model']==MODEL and result['request']==request,label+': result request/model differs')
  points=result['points'];require(len(points)==41,label+': require initial plus40points')
  for i,point in enumerate(points):
   context=point['context'];require(set(context)=={'state','coordinate','controls','parameters'},label+': incomplete context')
   require(set(context['state'])==set(STATES) and all(finite(v) for v in context['state'].values()),label+': incomplete/nonfinite state')
   require(context['parameters']==request['context']['parameters'],label+': parameters changed along path')
   require(finite(context['coordinate']) and (i==0 or context['coordinate']>points[i-1]['context']['coordinate']),label+': invalid path coordinate')
   require(set(context['controls'])==set(request['controls_end']) and all(finite(v) for v in context['controls'].values()),label+': incomplete controls')
   obs=point['observables'];require(len(obs['stress'])==6 and all(finite(v) for v in obs['stress']),label+': incomplete/nonfinite stress')
   require(all(finite(v) for k,v in obs.items() if k!='stress'),label+': invalid scalar observable')
  require(points[0]['context']==request['context'],label+': initial context differs')
  endpoint=points[-1];require(endpoint['context']['controls']==request['controls_end'] and endpoint['context']['coordinate']==request['context']['coordinate']+request['progress'],label+': endpoint controls/coordinate differ')
  for location,actual,expected in [('initial',points[0],reference['expected'][0]),('endpoint',endpoint,reference['expected'][-1])]:
   for name in STATES:
    error=abs(actual['context']['state'][name]-expected['context']['state'][name]);tol=2e-6 if name=='e' else .2;require(error<=tol,f'{label}/{location}/{name}: error {error} exceeds {tol}');checks.append({'export':label,'location':location,'field':name,'error':error,'tolerance':tol})
   for i,(value,ref) in enumerate(zip(actual['observables']['stress'],expected['observables']['stress'])):
    error=abs(value-ref);require(error<=.2,f'{label}/{location}/stress{i}: error {error} exceeds0.2');checks.append({'export':label,'location':location,'field':'stress'+str(i),'error':error,'tolerance':.2})
 require(documents['default']==documents['reset']==documents['replay'],'Default/reset/replay exports differ in exact parsed JSON values')
 report={'status':'passed-offline-actual-export-check','model':MODEL,'definition_sha256':DEFINITION,'package_identity_sha256':digest(base/'identity.json'),'inputs':inputs,'frozen_reference_case':reference['id'],'reference_pins':PINS,'exact_default_request':True,'exact_default_reset_replay':True,'points_per_export':41,'state_stress_reference_comparisons':len(checks),'checks':checks,'compiled_material_browser_calls':0,'scope':'Verifies supplied downloads offline; does not establish browser provenance, visible controls, network/console, stale-worker behavior or live delivery.'}
 text=json.dumps(report,indent=2)+'\n'
 if a.output:
  require(not a.output.exists(),'Refuse to overwrite prior result');a.output.write_text(text)
 print(text,end='')
if __name__=='__main__':
 try:main()
 except (ValueError,KeyError,TypeError,OSError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
