"""Common-engine comparison with an independent converged Cartesian path reference.
The reusable assess(records,model,reference) accepts the same retained native/Wasm
request/response matrix. Run raw records are saved before numerical assessment.
"""
import argparse,hashlib,json,math
from pathlib import Path
from atlas.model import ROOT,load
from tools.clay2013_integration_study import request,native_call,MODEL_PATH,TOLERANCES
from tools.clay2013_path_reference import study
REFERENCE_UNCERTAINTY_PA=1e-5
STRESS_RELATIVE_BOUNDS={1e-4:.02,1e-6:.002,1e-8:.0002}
E_BOUNDS={1e-4:1e-6,1e-6:1e-7,1e-8:1e-8}

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def scalar(x):return type(x) in (int,float) and math.isfinite(x)
def vector(x,n):return type(x) is list and len(x)==n and all(scalar(a)for a in x)
from tools import clay2013_path_reference as path_reference
from tools import reference_clay2013_cartesian as cartesian

PINNED_SOURCE='21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281'
PINNED_DEPENDENCIES={
 'tools/clay2013_path_reference.py':'ff3213708b185f91a7a85e18e9dffebff5b02d9f76b893117908fe677516ad05',
 'tools/reference_clay2013_cartesian.py':'d37b6b87206cafc0a74af53f4effd51c37495f318dcf4889eeec19d55943e50b',
}

def canonical(value):
 try:
  return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
 except (ValueError,TypeError,OverflowError) as exc:
  raise ValueError('invalid finite JSON reference') from exc

def replay_checked_cases(reference):
 if type(reference) is not dict:
  raise ValueError('reference object required')
 if reference.get('source_sha256')!=PINNED_SOURCE or path_reference.SOURCE_SHA256!=PINNED_SOURCE or cartesian.SOURCE_SHA256!=PINNED_SOURCE:
  raise ValueError('reference source receipt mismatch')
 if reference.get('dependency_sha256')!=PINNED_DEPENDENCIES:
  raise ValueError('reference dependency receipts mismatch')
 for name,module in [('tools/clay2013_path_reference.py',path_reference),('tools/reference_clay2013_cartesian.py',cartesian)]:
  if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()!=PINNED_DEPENDENCIES[name]:
   raise ValueError('current reference implementation differs from reviewed pin: '+name)
 # Fresh replay recomputes every trajectory, initial row, coarse/fine/ratio,
 # Richardson estimate and covariance; canonical equality also binds metadata,
 # units/basis, zero spin, rotation, resolutions and exact input identities.
 actual=canonical(reference)
 expected=canonical(path_reference.study())
 if actual!=expected:
  raise ValueError('reference differs from fresh pinned Cartesian replay')
 return {c['input']['id']:c for c in reference['cases']}

def checked_cases(reference):
 replay_checked_cases(reference)
 if reference.get('contract')!='clay2013-independent-cartesian-path-reference-v1':raise ValueError('reference contract mismatch')
 expected={c['id']:c for c in __import__('tools.clay2013_path_reference',fromlist=['cases']).cases()}
 found={}
 for c in reference['cases']:
  name=c['input']['id']
  if name not in expected or name in found or c['input']!=expected[name] or c['input_sha256']!=digest(c['input']):raise ValueError('reference input mismatch')
  if [g['steps_per_segment']for g in c['grids']]!=[8,16,32]:raise ValueError('reference grid mismatch')
  for g in c['grids']:
   if [r['segment']for r in g['trajectory']]!=[0,1,2,3] or any(not vector(r['state'],7)for r in g['trajectory']):raise ValueError('reference state mismatch')
  if not 14<c['refinement_ratio']['stress']<18 or c['fine_difference']['stress']>5e-6:raise ValueError('reference convergence unresolved')
  found[name]=c
 if set(found)!=set(expected):raise ValueError('incomplete reference matrix')
 return found

def validate_model(model,refs):
 if model.get('id')!='hypoplastic-clay-2013-research':raise ValueError('wrong comparison model')
 p=model['parameters']['p_ref']
 if (p['default'],p['min'],p['max'])!=(1000,1000,1000):raise ValueError('fixed source reference pressure mismatch')
 for c in refs.values():
  if any(model['parameters'][k]['default']!=v for k,v in c['input']['parameters'].items()):raise ValueError('reference/model parameter mismatch')

def assess(records,model,reference):
 refs=checked_cases(reference);validate_model(model,refs);expected={(name,t)for name in refs for t in TOLERANCES};seen={};summary=[];cat=digest([model])
 for group in records:
  key=(group['case'],group['tolerance'])
  if key not in expected or key in seen:raise ValueError('unexpected/duplicate trajectory')
  seen[key]=group;ref=refs[key[0]];case=ref['input'];tol=key[1];initial=case['initial'][:];scale=sum(initial[:3])/3
  if len(group['calls'])!=3:raise ValueError('incomplete caller segments')
  errors=[];cumulative=0
  for j,(record,strain)in enumerate(zip(group['calls'],case['increments']),1):
   r,a=record['request'],record['response']
   if not all(vector(r.get(k),n)for k,n in [('initial',7),('strain',6),('parameters',len(model['parameters'])),('settings',6)]):raise ValueError('invalid request vectors')
   if r!=request(model,initial,strain,tol,stress_scale=scale):raise ValueError('request identity mismatch')
   if a.get('ok') is not True:raise ValueError('trajectory failed')
   for k in ('model','parameters','initial','strain'):
    if a.get(k)!=r[k]:raise ValueError('response echo mismatch: '+k)
   if a.get('catalogue_hash')!=cat:raise ValueError('catalogue identity mismatch')
   settings=dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
   if a.get('integration_settings')!=settings:raise ValueError('settings echo mismatch')
   z=a.get('state')
   if not vector(z,7):raise ValueError('invalid state')
   d=a.get('diagnostics',{})
   if any(type(d.get(k))is not int or d[k]<0 for k in ('iterations','substeps','rejected')):raise ValueError('invalid diagnostics counters')
   if 'error' in d and (not scalar(d['error'])or d['error']<0):raise ValueError('invalid optional error diagnostic')
   fractions=d.get('increment_fractions')
   if not isinstance(fractions,list) or len(fractions)!=d['substeps'] or not fractions or any(not scalar(x)or not 0<x<=1 for x in fractions)or abs(math.fsum(fractions)-1)>1e-12:raise ValueError('invalid increment coverage')
   target=ref['grids'][-1]['trajectory'][j]['state'];component=[abs(x-y)for x,y in zip(z,target)]
   if max(component[:6])>scale*STRESS_RELATIVE_BOUNDS[tol]+REFERENCE_UNCERTAINTY_PA or component[6]>E_BOUNDS[tol]:raise ValueError('reference endpoint bound exceeded')
   cumulative+=sum(strain[:3]);exact_e=(1+case['initial'][6])*math.exp(-cumulative)-1;volume_error=abs(z[6]-exact_e)
   if volume_error>E_BOUNDS[tol]:raise ValueError('exact volume relation exceeded')
   errors.append(dict(segment=j,component_absolute=component,stress_max=max(component[:6]),void_ratio_absolute=component[6],exact_volume_error=volume_error))
   initial=z[:]
  summary.append(dict(case=key[0],tolerance=tol,endpoints=errors,stress_max=max(x['stress_max']for x in errors),void_ratio_max=max(x['void_ratio_absolute']for x in errors)))
 if set(seen)!=expected:raise ValueError('incomplete trajectory matrix')
 for name in refs:
  v=[next(s['stress_max']for s in summary if s['case']==name and s['tolerance']==t)for t in TOLERANCES]
  if v[1]>.65*v[0]+2*REFERENCE_UNCERTAINTY_PA or v[2]>.35*v[0]+2*REFERENCE_UNCERTAINTY_PA or v[2]>.65*v[1]+2*REFERENCE_UNCERTAINTY_PA:raise ValueError('stress refinement did not improve beyond reference uncertainty')
 if set(seen)!=expected:raise ValueError('incomplete trajectory matrix')
 return summary

def run(solver,raw_output,reference=None):
 model=load(MODEL_PATH);reference=study()if reference is None else reference;refs=checked_cases(reference);validate_model(model,refs);records=[]
 raw_output=Path(raw_output);raw_output.parent.mkdir(parents=True,exist_ok=True)
 for name,ref in refs.items():
  case=ref['input'];scale=sum(case['initial'][:3])/3
  for tol in TOLERANCES:
   initial=case['initial'][:];group=dict(case=name,tolerance=tol,calls=[]);records.append(group)
   for strain in case['increments']:
    r=request(model,initial,strain,tol,stress_scale=scale);a=native_call(solver,r);group['calls'].append(dict(request=r,response=a))
    raw_output.write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
    if a.get('ok')is not True or not vector(a.get('state'),7):raise ValueError('native trajectory failed; raw response retained')
    initial=a['state'][:]
 summary=assess(records,model,reference)
 return dict(version='clay2013-nonisotropic-integration-0.1',scope='zero-spin numerical research; no admission/experimental validation',model_sha256=digest(model),catalogue_hash=digest([model]),native_sha256=hashlib.sha256(Path(solver).read_bytes()).hexdigest(),reference_sha256=digest(reference),reference_uncertainty_pa=REFERENCE_UNCERTAINTY_PA,records=records,summary=summary)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--solver',type=Path,default=ROOT/'build/atlas_clay2013_solver');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.parent.mkdir(parents=True,exist_ok=True);report=run(a.solver,a.output.with_suffix('.raw.json'));a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
