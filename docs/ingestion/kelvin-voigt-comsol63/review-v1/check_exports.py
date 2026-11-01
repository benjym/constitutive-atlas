"""Independent saved browser-export/package audit. No engine, browser or production imports."""
import argparse,hashlib,json,math,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent.parent
MODEL='kelvin-voigt-comsol63-deviatoric-zero-spin-ode'
MODEL_SHA='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
D=[.001,-.0005,-.0005,.0004,-.0002,.0003]
SOLVER=dict(method='backward-euler-step-doubling',relative_tolerance=3e-11,absolute_scale_fraction=3e-14,minimum_step=1e-12,maximum_step=1e6,maximum_substeps=1000000,nonlinear_tolerance=1e-10,maximum_iterations=40,maximum_depth=40)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 def unique(pairs):
  d={}
  for k,v in pairs:
   if k in d:raise ValueError('Duplicate JSON key '+k)
   d[k]=v
  return d
 return json.loads(p.read_text(),object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+s)))
def finite6(a):return isinstance(a,list)and len(a)==6 and all(type(x)in(int,float)and math.isfinite(x)for x in a)
def exports(directory):
 modes={};identity=None;comparisons=0;artifacts={};docs={}
 for mode in ['creep','rate','hold']:
  p=directory/(mode+'.json');doc=read(p);docs[mode]=doc;artifacts[str(p)]=sha(p)
  assert doc['kind']=='atlas-kelvin-voigt-laboratory-v1','Wrong export kind'
  c=doc['controls'];expected=dict(mode=mode,duration=8,samples=8,start=0,parameters=[20e6,12e6,2],initial=[0]*6,initialRates=D,rates=D)
  assert c==expected,'Unexpected named-preset controls '+mode
  v=doc['provenance'];assert v['model']==MODEL and v['model_sha256']==MODEL_SHA
  assert v['review_sha256']=='7dc232c311541aea981981e1efcfc97448509fbc31d9602b9cead4a7890223c4'
  receipt=read(B/'build-v2/build-receipt.json')
  assert v['module_sha256']==receipt['files']['wasm-release/kv.mjs'] and v['wasm_sha256']==receipt['files']['wasm-release/kv.wasm']
  assert v['approval_sha256']==sha(B/'approval-v1.json')
  assert v['source_sha256']=='cf019ac6a6900d3fd6af91023cd806530d500812b100086062a91bfb1723cfcf'
  assert re.fullmatch('[a-f0-9]{40}',v['release_revision'])
  interface=read(B/'interface-v4/freeze.json')
  for name in ['kelvin-voigt-laboratory.mjs','kelvin-voigt-contract.mjs','kelvin-voigt-worker.mjs']:assert v['component_sha256'][name]==interface['files']['web/'+name]
  if identity is None:identity=v
  else:assert identity==v,'Mixed package identities across exports'
  quantity=int(mode=='creep');kind=int(mode=='rate');values=D if mode=='rate'else[0]*6
  wire=[8,8]
  for x in values:wire.extend([quantity,kind,x])
  req=doc['request'];args=req['args'];assert req['function']=='atlas_run_schedule'and len(args)==15
  assert args[0]==MODEL and list(map(float,args[1].split(',')))==[20e6,12e6,2]
  assert all(list(map(float,args[j].split(',')))==([0]*6 if j in[2,3]else D)for j in[2,3,4])
  assert list(map(float,args[5].split(',')))==wire and args[6]==('relaxation'if mode=='hold'else mode)
  assert args[7:]==[0,3e-11,3e-14,1e-12,1e6,1000000,1e-10,40]
  r=doc['result'];assert r['ok']and r['model']==MODEL and r['catalogue_hash']==v['catalogue_hash']
  assert r['units']=='SI'and r['schema_version']=='0.2'and r['solver']==SOLVER and r['start_time']==0
  assert r['parameters']==[20e6,12e6,2]and r['initial']==r['initial_strain']==[0]*6 and r['initial_strain_rate']==D
  assert len(r['points'])==10
  maxe=maxs=0.;nulls=0
  for i,pt in enumerate(r['points']):
   t=0 if i<2 else i-1
   assert pt['time']==t and pt['side']==('right'if i==1 else'left')and pt['segment']==(-1 if i==0 else 0)
   assert finite6(pt['state'])and finite6(pt['strain'])and finite6(pt['observables'])
   assert all(abs(x-y)<=64*sys.float_info.epsilon*max(1,abs(x),abs(y))for x,y in zip(pt['state'],pt['strain']))
   if i==1 and mode=='creep':assert pt['strain_rate']==[None]*6;nulls+=6
   else:assert finite6(pt['strain_rate'])
   # Parallel spring/dashpot: scalar integrating-factor creep, affine loading,
   # zero-rate hold. All default vectors are deviatoric; elastic bulk is zero.
   if i==0:e=[0]*6;s=[2*12e6*2*x for x in D]
   elif mode=='creep':e=[2*x*(-math.expm1(-t/2))for x in D];s=[2*12e6*2*x for x in D]
   elif mode=='rate':e=[t*x for x in D];s=[2*12e6*(t+2)*x for x in D]
   else:e=[0]*6;s=[0]*6
   maxe=max(maxe,max(abs(x-y)for x,y in zip(pt['state'],e)));maxs=max(maxs,max(abs(x-y)for x,y in zip(pt['observables'],s)));comparisons+=12
   assert all(abs(x-y)<=3e-8 for x,y in zip(pt['state'],e)),mode+' state error'
   assert all(abs(x-y)<=1 for x,y in zip(pt['observables'],s)),mode+' stress error'
  modes[mode]=dict(comparisons=120,max_strain_error=maxe,max_stress_error_Pa=maxs,null_rate_entries=nulls,export_sha256=sha(p))
 prior=read(directory/'physical-checks.json');assert prior['passed']and prior['comparisons']==comparisons==360
 for mode,row in modes.items():assert prior['modes'][mode]['export_sha256']==row['export_sha256']
 tampered=read(directory/'tampered-creep.json');assert tampered['controls']==docs['creep']['controls']and tampered['provenance']==identity
 assert tampered['result']!=docs['creep']['result'],'Tamper fixture is unchanged'
 assert abs(tampered['result']['points'][2]['state'][3]-docs['creep']['result']['points'][2]['state'][3]-.01)<1e-15
 assert tampered['result']['points'][2]['state'][3]==tampered['result']['points'][2]['strain'][3]
 assert tampered['result']['points'][2]['observables'][3]-docs['creep']['result']['points'][2]['observables'][3]==100
 return dict(comparisons=comparisons,modes=modes,provenance=identity,artifacts=artifacts,tamper_fixture='coherent transport but changed state/stress; exact replay comparison must reject; actual UI rejection is separate evidence')
def package(packet,package,identity):
 log=(packet/'build.log').read_text();assert 'Packaged 'in log and'"fullStateStressComparisons": 360'in log and MODEL in log
 assert '"exactReplay": true'in log and'"failedRequestRecovery": true'in log
 supported=read(packet/'supported-package.json');assert supported['status']=='passed'and len(supported['ordinary'])==14 and len(supported['named'])==1
 result=dict(normal_build_completed=True,kelvin_package_comparisons=360,supported_ordinary_models=14,supported_named_examples=1,supported_policy=supported['policy_id'],build_log_sha256=sha(packet/'build.log'),supported_report_sha256=sha(packet/'supported-package.json'))
 if package:
  assert read(package/'engine-kelvin-voigt/identity.json')==identity,'Export package identity differs'
  manifest=read(package/'engine-kelvin-voigt/package-manifest.json')
  for path,h in manifest['files'].items():assert sha(package/path)==h,path
  assert not(package/'kelvin-voigt.html').exists(),'Standalone page unexpected'
  result['package_assets_verified']=len(manifest['files']);result['identity_matches_exports']=True
 else:result['package_assets_verified']='not requested; report/log evidence only'
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--exports',type=Path,default=B/'browser-v2');p.add_argument('--packet',type=Path,default=B/'package-v2');p.add_argument('--package',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists(),'Refuse replacing evidence'
 required=[a.exports/(m+'.json')for m in['creep','rate','hold']]+[a.exports/'physical-checks.json',a.exports/'tampered-creep.json',a.packet/'build.log',a.packet/'supported-package.json']
 missing=[str(x)for x in required if not x.is_file()];report=dict(identity='kelvin-independent-browser-export-audit-v1',reviewer='/root/kelvin_scientific_review',compiled_or_browser_calls=0,passed=False,missing_files=missing,blocking_findings=[])
 if missing:report['blocking_findings'].append('Required saved evidence missing; no pass inferred')
 else:
  try:
   report['exports']=exports(a.exports);report['package']=package(a.packet,a.package,report['exports']['provenance']);report['passed']=True
  except(AssertionError,ValueError,KeyError,OSError)as e:report['blocking_findings'].append(type(e).__name__+': '+str(e))
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if report['passed']else 1
if __name__=='__main__':sys.exit(main())
