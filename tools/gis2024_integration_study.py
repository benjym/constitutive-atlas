"""Bounded full14 GIS finite-path study against independent Cartesian RK4 grids.

No material kernel: all native calls use the existing schema-generated solver.
Declared endpoint budgets precede the production study; raw parsed responses are
retained before numerical assessment. A tolerance is not an error certificate.
"""
import argparse,hashlib,json,math,subprocess,copy
from pathlib import Path
from atlas.model import ROOT,load
from atlas.initialization import canonical_hash as digest
from tools.clay2013_integration_study import request,native_call
from tools.gis2024_rate_study import MODEL_PATH
from tools import gis2024_path_reference as reference

MATRIX=((1e-4,1),(1e-6,1),(1e-8,1),(1e-4,7),(1e-8,7))
# Global dimensionless study budgets, distinct from local error settings.
ENDPOINT_BOUNDS={1e-4:5e-3,1e-6:3e-4,1e-8:2e-5}
REFERENCE_BUDGET=dict(stress=1e-4,e=1e-12,h=1e-13,Omega=1e-10)
SOURCE_SHA256='39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3'
PINNED_DEPENDENCIES={'tools/gis2024_path_reference.py': '4e143ac7f457b060d1761c8d2797be7ac66e1b6c5e869980680aeadef230c17e', 'tools/reference_gis2024_coupled.py': 'ecfdaeba7ca363eb10f9177f8b8af5e279ffb05ae8bbf9aa8eb063a69bdfc502', 'tools/reference_gis2024_hp_host.py': '298ee15ae9c2e95601111841e8f12e2a90872024ba66c1a6af9e76c7aa1273d0'}

def finite(x):return type(x)in(int,float)and math.isfinite(x)
def vector(x,n):return type(x)is list and len(x)==n and all(finite(v)for v in x)
def split_increment(d,n):
 used=[0.]*6;out=[]
 for j in range(n):
  part=[x-u if j==n-1 else x/n for x,u in zip(d,used)]
  out.append(part);used=[u+x for u,x in zip(used,part)]
 return out

def make_request(model,case,initial,strain,tolerance,budget=20000):
 scale=sum(case['initial'][:3])/3
 r=request(model,initial,strain,tolerance,budget=budget,stress_scale=scale)
 r['parameters']=[scale if name=='p_scale'else case['parameters'][name]for name in model['parameters']]
 return r

def checked_reference(ref):
 if ref.get('dependency_sha256')!=PINNED_DEPENDENCIES:raise ValueError('reference dependency receipt mismatch')
 for name,expected in PINNED_DEPENDENCIES.items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError('current reference dependency differs from reviewed pin')
 if ref.get('source_sha256')!=SOURCE_SHA256 or ref.get('contract')!='gis2024-independent-cartesian-path-reference-v1':raise ValueError('reference identity mismatch')
 # Fresh finite canonical replay binds all metadata, inputs, grid rows, stage
 # margins and statistics. This is local provenance, not bitwise portability.
 if digest(ref)!=digest(reference.study()):raise ValueError('reference differs from fresh independent replay')
 for case in ref['cases']:
  if case['input_sha256']!=digest(case['input']):raise ValueError('reference input receipt mismatch')
  for channel,budget in REFERENCE_BUDGET.items():
   v=case['fine_difference'][channel]
   if not finite(v)or v>budget/4:raise ValueError('reference uncertainty budget unresolved: '+channel)
  for grid in case['grids']:
   if any(s['branch_crossing_observed']for s in grid['stage_diagnostics']['segments']):raise ValueError('selected smooth-segment reference crosses branch')
 return {c['input']['id']:c for c in ref['cases']}

def check_response(a,r,model):
 if a.get('ok')is not True:raise ValueError('finite trajectory failed')
 for key in ('model','parameters','initial','strain'):
  if a.get(key)!=r[key]:raise ValueError('response echo mismatch: '+key)
 for key,n in [('parameters',len(model['parameters'])),('initial',14),('strain',6)]:
  if not vector(a.get(key),n):raise ValueError('invalid response echo vector')
 if a.get('catalogue_hash')!=digest([model]):raise ValueError('catalogue identity mismatch')
 settings=dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
 if a.get('integration_settings')!=settings:raise ValueError('integration settings mismatch')
 if not vector(a.get('state'),14):raise ValueError('finite14 state required')
 d=a.get('diagnostics',{})
 if any(type(d.get(k))is not int or d[k]<0 for k in ('substeps','rejected','iterations')):raise ValueError('invalid diagnostic counter')
 fractions=d.get('increment_fractions')
 if not isinstance(fractions,list)or len(fractions)!=d['substeps']or not fractions or any(not finite(x)or not 0<x<=1 for x in fractions)or abs(math.fsum(fractions)-1)>1e-12:raise ValueError('invalid increment coverage')
 if 'error'in d and(not finite(d['error'])or d['error']<0):raise ValueError('invalid optional local error')

def errors(actual,target):
 return {name:max(abs(x-y)for x,y in zip(actual[lo:hi],target[lo:hi]))for name,lo,hi in [('stress',0,6),('e',6,7),('h',7,13),('Omega',13,14)]}

def validate_model(model,refs):
 expected=[('sigma','sym','Pa','p_scale'),('e','scalar','1','1'),('h','sym','1','R'),('Omega','scalar','1','1')]
 if model.get('id')!='hp-extracted-asbs-gis-2024-research'or model.get('integration')!='rate'or [(f['name'],f['shape'],f['unit'],f['scale'])for f in model['state']]!=expected:
  raise ValueError('wrong selected GIS model contract')
 if set(model['parameters'])!=set(reference.PARAMETERS)|{'p_scale'}:raise ValueError('wrong GIS parameter layout')
 for c in refs.values():
  case=c['input']
  if set(case['parameters'])!=set(reference.PARAMETERS)or not vector(case['initial'],14):raise ValueError('invalid reference input layout')
  for name,value in case['parameters'].items():
   spec=model['parameters'][name]
   if not finite(value)or not spec['min']<=value<=spec['max']:raise ValueError('reference parameter outside model bounds')
  p=sum(case['initial'][:3])/3;scale=model['parameters']['p_scale']
  if not scale['min']<=p<=scale['max']:raise ValueError('numerical stress scale outside bounds')

def assess(records,model,ref):
 refs=checked_reference(ref);validate_model(model,refs);expected={(name,t,n)for name in refs for t,n in MATRIX};seen={};summary=[]
 for group in records:
  if not finite(group.get('tolerance'))or type(group.get('partitions'))is not int:raise ValueError('invalid trajectory matrix labels')
  key=(group['case'],group['tolerance'],group['partitions'])
  if key not in expected or key in seen:raise ValueError('unexpected/duplicate trajectory')
  seen[key]=group;case=refs[key[0]]['input'];tol,n=key[1:];initial=case['initial'][:]
  strains=[(j,part)for j,d in enumerate(case['increments'],1)for part in split_increment(d,n)]
  if len(group['calls'])!=len(strains):raise ValueError('incomplete caller matrix')
  endpoint_errors=[];cumulative=0.;volume_max=0.
  for i,(record,(segment,strain))in enumerate(zip(group['calls'],strains),1):
   r,a=record['request'],record['response']
   if not all(vector(r.get(k),size)for k,size in [('initial',14),('strain',6),('parameters',len(model['parameters'])),('settings',6)]):raise ValueError('invalid request vectors')
   if r!=make_request(model,case,initial,strain,tol):raise ValueError('request chain/protocol mismatch')
   check_response(a,r,model);z=a['state']
   try:reference.reference.coupled_rates(reference.state_dict(z),[0.]*6,case['parameters'])
   except (ValueError,ArithmeticError)as exc:raise ValueError('returned state outside independent selected domain')from exc
   cumulative+=math.fsum(strain[:3])
   volume=abs(z[6]-((1+case['initial'][6])*math.exp(-cumulative)-1));volume_max=max(volume_max,volume)
   if volume>max(1e-10,ENDPOINT_BOUNDS[tol]*.01):raise ValueError('exact volume relation mismatch')
   if i%n==0:
    target=refs[key[0]]['grids'][-1]['trajectory'][segment]['state'];err=errors(z,target)
    scales=dict(stress=sum(case['initial'][:3])/3,e=1.,h=case['parameters']['R'],Omega=1.)
    if any(err[k]>scales[k]*ENDPOINT_BOUNDS[tol]+REFERENCE_BUDGET[k]for k in err):raise ValueError('endpoint study budget exceeded')
    endpoint_errors.append(dict(segment=segment,component_absolute=[abs(x-y)for x,y in zip(z,target)],errors=err))
   initial=z[:]
  summary.append(dict(case=key[0],tolerance=tol,partitions=n,endpoints=endpoint_errors,maximum={k:max(x['errors'][k]for x in endpoint_errors)for k in REFERENCE_BUDGET},volume_max=volume_max))
 if set(seen)!=expected:raise ValueError('incomplete trajectory matrix')
 # Stress, h and Omega errors must refine beyond the declared reference budget;
 # e is roundoff limited and separately checked through the volume identity.
 for name in refs:
  rows=[next(s for s in summary if(s['case'],s['tolerance'],s['partitions'])==(name,t,1))for t in (1e-4,1e-6,1e-8)]
  for k in ('stress','h','Omega'):
   v=[s['maximum'][k]for s in rows]
   if v[1]>.65*v[0]+2*REFERENCE_BUDGET[k]or v[2]>.35*v[0]+2*REFERENCE_BUDGET[k]or v[2]>.65*v[1]+2*REFERENCE_BUDGET[k]:raise ValueError('global refinement unresolved: '+k)
 # Caller partition differences are measured at identical original endpoints.
 partition=[]
 for name in refs:
  bytol=[]
  for tol in (1e-4,1e-8):
   a=seen[name,tol,1]['calls'];b=seen[name,tol,7]['calls']
   errs=[errors(a[j]['response']['state'],b[(j+1)*7-1]['response']['state'])for j in range(3)]
   bytol.append({k:max(e[k]for e in errs)for k in REFERENCE_BUDGET})
  if any(bytol[1][k]>.35*bytol[0][k]+2*REFERENCE_BUDGET[k]for k in ('stress','h','Omega')):raise ValueError('caller partition refinement unresolved')
  partition.append(dict(case=name,tolerances=[1e-4,1e-8],maximum_differences=bytol))
 return dict(trajectories=summary,caller_partitions=partition)

def probe_requests(records,model):
 base=next(g for g in records if g['partitions']==1 and g['tolerance']==1e-8)['calls'][0]['request']
 result=[]
 for kind in ('budget','domain','zero'):
  r=copy.deepcopy(base)
  if kind=='budget':r['settings'][4]=3
  if kind=='domain':
   R=r['parameters'][list(model['parameters']).index('R')];r['initial'][7:13]=[1.01*R,0.,0.,0.,0.,0.]
  if kind=='zero':r['strain']=[0.]*6
  result.append(dict(kind=kind,request=r))
 return result

def assess_probes(probes,records,model):
 expected=probe_requests(records,model)
 if len(probes)!=len(expected):raise ValueError('incomplete failure/zero probes')
 for probe,want in zip(probes,expected):
  if probe['kind']!=want['kind']or probe['request']!=want['request']:raise ValueError('probe request mismatch')
  r,a=probe['request'],probe['response'];zero=probe['kind']=='zero'
  if a.get('ok')is not zero or not vector(a.get('state'),14)or a['state']!=r['initial']:raise ValueError('probe rollback/zero state mismatch')
  for key in ('model','parameters','initial','strain'):
   if a.get(key)!=r[key]:raise ValueError('probe echo mismatch')
  for key,n in [('parameters',len(model['parameters'])),('initial',14),('strain',6)]:
   if not vector(r.get(key),n)or not vector(a.get(key),n):raise ValueError('invalid probe echo vector')
  settings=dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
  if a.get('integration_settings')!=settings:raise ValueError('probe integration settings mismatch')
  d=a.get('diagnostics',{})
  if any(type(d.get(k))is not int or d[k]<0 for k in ('substeps','iterations','rejected')):raise ValueError('invalid probe diagnostics')
  fractions=d.get('increment_fractions')
  if not isinstance(fractions,list)or len(fractions)!=d['substeps']or any(not finite(x)or not 0<x<=1 for x in fractions)or not 0<=math.fsum(fractions)<=1+1e-12:raise ValueError('invalid partial probe coverage')
  if 'error'in d and(not finite(d['error'])or d['error']<0):raise ValueError('invalid optional probe error')
  if a.get('catalogue_hash')!=digest([model]):raise ValueError('probe catalogue mismatch')
  if zero:check_response(a,r,model)
  if probe['kind']=='budget'and not(type(a.get('diagnostics',{}).get('substeps'))is int and a['diagnostics']['substeps']>0):raise ValueError('budget probe did not fail after progress')

def run(solver,raw_output,ref=None):
 model=load(MODEL_PATH);ref=reference.study()if ref is None else ref;refs=checked_reference(ref);validate_model(model,refs)
 descriptor=json.loads(subprocess.run([str(solver),'--describe'],capture_output=True,text=True,check=True,timeout=30).stdout)
 if descriptor.get('models')!=[model]or descriptor.get('sha256')!=digest([model]):raise ValueError('runtime catalogue mismatch')
 raw_output=Path(raw_output);raw_output.parent.mkdir(parents=True,exist_ok=True);records=[]
 for name,refcase in refs.items():
  case=refcase['input']
  for tol,n in MATRIX:
   initial=case['initial'][:];group=dict(case=name,tolerance=tol,partitions=n,calls=[]);records.append(group)
   for d in case['increments']:
    for part in split_increment(d,n):
     r=make_request(model,case,initial,part,tol);a=native_call(solver,r);group['calls'].append(dict(request=r,response=a));raw_output.write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
     check_response(a,r,model);initial=a['state'][:]
 probes=[]
 for wanted in probe_requests(records,model):
  probes.append(wanted|dict(response=native_call(solver,wanted['request'])))
  raw_output.with_suffix('.probes.json').write_text(json.dumps(probes,indent=2,allow_nan=False)+'\n')
 assess_probes(probes,records,model)
 return dict(failure_probes=probes,version='gis2024-coupled-integration-0.1',scope='Strictly interior zero-spin numerical paths; no source preparation/experimental/scientific admission',model_sha256=digest(model),catalogue_hash=digest([model]),native_sha256=hashlib.sha256(Path(solver).read_bytes()).hexdigest(),reference_sha256=digest(ref),reference_budget=REFERENCE_BUDGET,endpoint_budgets=ENDPOINT_BOUNDS,records=records,assessment=assess(records,model,ref))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--solver',type=Path,default=ROOT/'build/atlas_gis2024_solver');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
 report=run(a.solver,a.output.with_suffix('.raw.json'));a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(f"Verified {len(report['records'])} finite trajectories and caller partitions")
