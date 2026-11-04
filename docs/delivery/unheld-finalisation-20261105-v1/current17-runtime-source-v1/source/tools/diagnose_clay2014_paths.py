"""Read-only decomposition of frozen clay2014 native negative evidence.
No compiled execution, report rewrite, policy changes or numerical relaxation.
"""
import hashlib,json,math
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
from tools import clay2014_path_study as study

ROOT=study.ROOT
PACKET=ROOT/'catalogue/investigations/clay2014-paths-v1'
KNOWN_INPUT_PINS={'native.json': '8f9971fd1e620f54b9fbcf1dd886ca87b7a75f572690fb0de846ed3eca2cdb11', 'native.transport.jsonl': '030a8359d68218f4c87a172ac1c3be10cf71cf9ea4a6bbd9210a789b090e8add', 'wasm.json': '8279c13961b7136756f9f1b342a0242335109ee05a584f6e28c0fce6888e9d9f', 'wasm.transport.jsonl': 'e4f39ac125b933da2bcb23f9b31b8dfee9f8e59c8f332d21b35eb2581ca45351', 'preobservation-source.json': '6c48b365ed3910373fa56da9fa81aa3b025c6401b7b52a8be54024693972e449', 'preobservation-native-build.json': '0e00d1f06bd5c9a8bec40ea6441994b07388c8c846b20abb5af28ef5dac1a6a6', 'preobservation-wasm-build.json': '02aafd56fef93b156b4c505d32df537720a4b2cd3d6db234359c4f14df5b6317', 'source-freeze.json': 'baa14f1c5387c53338eef7895a3a51d469d102218246155855014e9d2d571953'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(),parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON')))
def analyze(backend,check_artifacts=False):
 report_path=PACKET/(backend+'.json');raw_path=PACKET/(backend+'.transport.jsonl');held=report_path.read_bytes();original_pins={str(report_path.relative_to(ROOT)):hashlib.sha256(held).hexdigest(),str(raw_path.relative_to(ROOT)):sha(raw_path)}
 report=json.loads(held,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite report JSON')));study.require(report.get('backend')==backend,'backend identity');ref,cases,points=study.checked_reference();model=study.load(study.MODEL_PATH)
 checks={};checks['raw']=study.verify_transport(report,raw_path)
 for key,value in study.metadata(model,ref,backend).items():study.require(study.same(report.get(key),value),'metadata mismatch:'+key)
 study.require(study.same(report['runtime_descriptor'].get('models'),[model])and report['runtime_descriptor'].get('sha256')==study.digest([model]),'descriptor')
 for name,pin in report['source_pins'].items():study.require(sha(ROOT/name)==pin,'source:'+name)
 checks['source_metadata_descriptor']='pass; fresh pinned independent reference replay and all current source pins verified'
 study.require(report['persistent_recovery']is True,'persistent recovery assertion')
 if backend=='native':
  study.require(type(report['native_exit_status'])is int and report['native_exit_status']==0 and report['native_trailing_stdout']==''and type(report['native_stderr'])is str,'native termination contract')
  study.require(type(report['native_command'])is list and len(report['native_command'])==2 and report['native_command'][1]=='--stream','native persistent command')
 checks['process_or_instance']='pass native termination or persistent Wasm assertion and raw source-collector binding'
 receipts={}
 for name in('preobservation-source.json','preobservation-'+backend+'-build.json','source-freeze.json'):
  p=PACKET/name;r=read(p);receipts[name]={'sha256':sha(p)}
  if name=='preobservation-source.json':
   for path,pin in r['files'].items():study.require(sha(ROOT/path)==pin,'preobservation source:'+path)
  if name=='source-freeze.json':
   for row in r['files']:study.require(sha(ROOT/row['path'])==row['sha256'],'sourcefreeze:'+row['path'])
  if name=='preobservation-'+backend+'-build.json':
   for path,pin in r['files'].items():
    if check_artifacts:study.require(sha(ROOT/path)==pin,'buildartifact:'+path)
   for command in r['commands']:
    for pathkey,hashkey in(('log','log_sha256'),('command_record','command_record_sha256')):study.require(sha(ROOT/command[pathkey])==command[hashkey],'buildlog:'+pathkey)
   if backend=='native':study.require(r['files']['build/atlas_clay2014_solver']==report['native_sha256'],'native artifact report binding')
   else:
    study.require(r['files']['build-wasm/clay2014-paths.js']==report['wasm_loader_sha256']and r['files']['build-wasm/clay2014-paths.wasm']==report['wasm_binary_sha256'],'Wasm artifact report binding')
   study.require(r['preobservation_sha256']==sha(PACKET/'preobservation-source.json'),'preobservation document binding')
   receipts[name]['source_commit']=r['source_commit'];receipts[name]['artifact_files']=r['files'];receipts[name]['artifact_byte_checks']='performed'if check_artifacts else'receipt binding only; artifacts not reopened'
 rows=[];groupmap={};accuracy_failures=[]
 for group in report['records']:
  name=group['case'];tol=group['tolerance'];n=group['partitions'];study.require(type(name)is str and study.finite(tol)and type(n)is int and(name,tol,n)not in groupmap,'group label types/duplicate');case=cases[name];reference=points[name,n]['row'];targets=reference['grids'][-1]['trajectory'];groupmap[name,tol,n]=[];initial=case['initial'].copy()
  study.require(len(group['calls'])==len(targets)==3*n,'complete trajectory')
  for index,(call,target,knot,coarse,fine)in enumerate(zip(group['calls'],targets,reference['caller_points'],reference['coarse_middle'],reference['middle_fine'])):
   wanted=study.make_request(model,case,initial,knot['increment'],tol);study.require(study.request_equal(call['request'],wanted),'actual parent chain')
   study.check_response(call['response'],call['request'],model)
   state=call['response']['state'];want=target['state'];err={'stress':math.sqrt(math.fsum((a-b)**2 for a,b in zip(state[:6],want[:6]))),'e':abs(state[6]-want[6])}
   unc={'stress':max(coarse['stress_Pa'],fine['stress_Pa']),'e':max(coarse['void_ratio'],fine['void_ratio'])}
   bounds={'stress':case['stress_scale']*study.ENDPOINT_BOUNDS[tol],'e':study.VOID_BOUNDS[tol]}
   with localcontext()as ctx:
    ctx.prec=100;v=sum((study.reference.unexact(x)for x in knot['cumulative_loading_exact'][:3]),Fraction());V=Decimal(v.numerator)/Decimal(v.denominator);e_exact=float((1+Decimal.from_float(case['initial'][6]))*(-V).exp()-1)
   volume_error=abs(state[6]-e_exact)
   row=dict(case=name,tolerance=tol,partitions=n,segment=knot['segment'],caller=knot['caller'],endpoint=knot['caller']==n,state=state,reference_state=want,errors=err,scaled_stress_error=err['stress']/case['stress_scale'],bounds=bounds,reference_uncertainty=unc,volume_error=volume_error)
   rows.append(row);groupmap[name,tol,n].append(row)
   for channel in err:
    if err[channel]>bounds[channel]:accuracy_failures.append({k:row[k]for k in('case','tolerance','partitions','segment','caller')}|dict(channel=channel,error=err[channel],bound=bounds[channel]))
   if volume_error>study.VOID_BOUNDS[tol]:accuracy_failures.append(dict(case=name,tolerance=tol,partitions=n,segment=knot['segment'],channel='volume',error=volume_error,bound=study.VOID_BOUNDS[tol]))
   initial=state.copy()
 study.require(set(groupmap)=={(name,t,n)for name in cases for t,n in study.MATRIX},'complete exact matrix')
 endpoint=[];refinement_failures=[]
 for name,case in cases.items():
  for n in(1,7):
   for segment in(1,2,3):
    selected=[groupmap[name,tol,n][segment*n-1]for tol in(1e-4,1e-6,1e-8)]
    for channel in('stress','e'):
     vals=[row['errors'][channel]for row in selected];unc=max(row['reference_uncertainty'][channel]for row in selected);floor=5e-12*case['stress_scale']if channel=='stress'else 5e-13;allowance=2*(floor+unc)
     tests=[]
     for label,lhs,rhs in [('middle<=.65loose',vals[1],.65*vals[0]+allowance),('tight<=.65middle',vals[2],.65*vals[1]+allowance),('tight<=.35loose',vals[2],.35*vals[0]+allowance)]:
      test=dict(inequality=label,lhs=lhs,rhs=rhs,excess=lhs-rhs,passed=lhs<=rhs);tests.append(test)
      if not test['passed']:refinement_failures.append(dict(case=name,partitions=n,segment=segment,channel=channel,errors_loose_middle_tight=vals,reference_uncertainty=unc,floor=floor,**test))
     endpoint.append(dict(case=name,partitions=n,segment=segment,channel=channel,errors_loose_middle_tight=vals,floor=floor,reference_uncertainty=unc,checks=tests))
 partition=[];partition_failures=[]
 for name,case in cases.items():
  for channel in('stress','e'):
   diffs=[]
   for tol in(1e-4,1e-8):
    errs=[]
    for segment in(1,2,3):
     a=groupmap[name,tol,1][segment-1]['state'];b=groupmap[name,tol,7][segment*7-1]['state'];errs.append(math.sqrt(math.fsum((x-y)**2 for x,y in zip(a[:6],b[:6])))if channel=='stress'else abs(a[6]-b[6]))
    diffs.append(max(errs))
   floor=5e-12*case['stress_scale']if channel=='stress'else 5e-13;bound=.35*diffs[0]+2*floor;row=dict(case=name,channel=channel,loose=diffs[0],tight=diffs[1],bound=bound,passed=diffs[1]<=bound);partition.append(row)
   if not row['passed']:partition_failures.append(row)
 covariance=[]
 for tol,n in study.MATRIX:
  a=groupmap['oblique-reversal',tol,n];b=groupmap['rotated-oblique-reversal',tol,n];scale=cases['oblique-reversal']['stress_scale'];other=cases['rotated-oblique-reversal']['stress_scale'];ss=0.;ee=0.
  for left,right in zip(a,b):
   rotated=study.reference.source.to_mandel(study.reference.source.rotate(study.reference.source.from_mandel(left['state'][:6]),study.reference.Q));ss=max(ss,math.hypot(*(x-y for x,y in zip(rotated,right['state'][:6]))));ee=max(ee,abs(left['state'][6]-right['state'][6]))
  sb=study.ENDPOINT_BOUNDS[tol]*(scale+other)+2*5e-12*max(scale,other);eb=2*study.VOID_BOUNDS[tol]+2*5e-13;covariance.append(dict(tolerance=tol,partitions=n,stress=ss,void_ratio=ee,stress_bound=sb,void_bound=eb,passed=ss<=sb and ee<=eb))
 study.assess_probes(report['failure_probes'],report['transaction_prefix'],report['recovery_control'],report['records'],model,cases);checks['transactions']='pass frozen prefix/probe/recovery assessor independently of failed refinement gate'
 probes=[]
 for p in report['failure_probes']:
  a=p['response'];probes.append(dict(kind=p['kind'],ok=a['ok'],message=a['message'],substeps=a['diagnostics']['substeps'],coverage=math.fsum(a['diagnostics']['increment_fractions']),returned_exact_caller_parent=a['state']==p['request']['initial'],recovery_exact_control=study.same(p['recovery'],report['recovery_control'])))
 try:study.verify(report)
 except ValueError as error:
  checks['frozen_full_assessor']=str(error)
  study.require(str(error)=='global refinement unresolved at physical endpoint: stress','unexpected original-assessor failure; diagnosis invalid')
 else:raise AssertionError('expected frozen negative gate did not fail')
 for name,pin in original_pins.items():study.require(sha(ROOT/name)==pin,'original retained bytes changed during diagnosis')
 hydro=[g for g in report['records']if g['case']=='isotropic-ratios-hydro-reversal'and g['partitions']==7];bytol={g['tolerance']:g for g in hydro}
 plateau={'first_segment_loose_middle_states_identical':all(study.same(a['response']['state'],b['response']['state'])for a,b in zip(bytol[1e-4]['calls'][:7],bytol[1e-6]['calls'][:7])),'first_segment_loose_middle_diagnostics_identical':all(study.same(a['response']['diagnostics'],b['response']['diagnostics'])for a,b in zip(bytol[1e-4]['calls'][:7],bytol[1e-6]['calls'][:7])),'substeps_by_tolerance':{str(t):[c['response']['diagnostics']['substeps']for c in bytol[t]['calls']]for t in bytol}}
 summary={'maximum_stress_accuracy_budget_fraction':max(r['errors']['stress']/r['bounds']['stress']for r in rows),'maximum_void_accuracy_budget_fraction':max(r['errors']['e']/r['bounds']['e']for r in rows),'endpoint_inequalities_checked':len(endpoint)*3,'endpoint_inequalities_failed':len(refinement_failures),'covariance_all_pass':all(x['passed']for x in covariance),'all_returned_state_and_echo_checks_pass':True}
 result=dict(version='clay2014-negative-independent-backend-diagnosis-v1',backend=backend,scope='read-only decomposition, no acceptance relaxation or compiled execution',retained_files=original_pins,receipts=receipts,checks=checks,summary=summary,adaptive_plateau_evidence=plateau,trajectory_count=len(report['records']),call_count=len(rows),accuracy_failures=accuracy_failures,refinement_failures=refinement_failures,partition_failures=partition_failures,covariance=covariance,probes=probes,endpoint_metrics=endpoint,partition_metrics=partition,all_caller_metrics=rows)
 return result

def build_diagnosis(check_artifacts=False):
 for name,pin in KNOWN_INPUT_PINS.items():study.require(sha(PACKET/name)==pin,'original input receipt:'+name)
 native=analyze('native',check_artifacts);wasm=analyze('wasm',check_artifacts)
 npath=PACKET/'native.json';wpath=PACKET/'wasm.json';nbytes=npath.read_bytes();wbytes=wpath.read_bytes();n=json.loads(nbytes);w=json.loads(wbytes)
 study.require(w['native_report_sha256']==hashlib.sha256(nbytes).hexdigest(),'Wasm native report held-byte binding')
 study.require(w['native_transport_sha256']==sha(PACKET/'native.transport.jsonl'),'Wasm native raw binding')
 study.require(study.same(n['runtime_descriptor'],w['runtime_descriptor']),'cross-backend full descriptor identity')
 study.require(len(n['records'])==len(w['records'])==24,'cross-backend groups')
 maximum=0.;count=0
 for ng,wg in zip(n['records'],w['records']):
  study.require((ng['case'],ng['tolerance'],ng['partitions'])==(wg['case'],wg['tolerance'],wg['partitions']),'parity group order')
  scale=max(1.,math.hypot(*ng['calls'][0]['request']['initial'][:6]))
  study.require(len(ng['calls'])==len(wg['calls']),'parity caller count')
  for a,b in zip(ng['calls'],wg['calls']):
   for key in('model','parameters','strain','settings'):study.require(study.same(a['request'][key],b['request'][key]),'parity controls')
   for x,y in((a['request']['initial'],b['request']['initial']),(a['response']['state'],b['response']['state'])):
    study.require(study.vector(x,7)and study.vector(y,7),'finite parity state/parent')
    maximum=max(maximum,math.hypot(*(u-v for u,v in zip(x[:6],y[:6])))/scale,abs(x[6]-y[6]))
   count+=1
 study.require(count==288,'288 parity updates')
 for result in(native,wasm):
  for path,pin in result['retained_files'].items():study.require(sha(ROOT/path)==pin,'retained inputs changed after independent parity')
 # This is deliberately separate from frozen parity(), which must reject both
 # complete reports because their original numerical acceptance gate failed.
 parity=dict(state_and_parent_updates=count,scaled_maximum=maximum,bound=5e-11,passed=maximum<=5e-11,scope='state/parent comparison only; does not override failed frozen overall assessment')
 failed=any(r['accuracy_failures']or r['refinement_failures']or r['partition_failures']or not all(c['passed']for c in r['covariance'])for r in(native,wasm))or not parity['passed']
 for name,pin in KNOWN_INPUT_PINS.items():study.require(sha(PACKET/name)==pin,'original input changed during diagnosis:'+name)
 return dict(version='clay2014-independent-negative-diagnosis-v1',input_pins=KNOWN_INPUT_PINS,outcome='failed'if failed else'passed',generator_sha256=sha(__file__),frozen_assessor_sha256=sha(study.__file__),no_policy_changes=True,compiled_execution=False,backends=[native,wasm],state_parent_parity=parity)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--check-artifacts',action='store_true');a=p.parse_args();study.require(not a.output.exists(),'fresh output required; retained inputs/results are immutable');result=build_diagnosis(a.check_artifacts);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'outcome':result['outcome'],'failures':{r['backend']:r['refinement_failures']for r in result['backends']},'state_parent_parity':result['state_parent_parity']},indent=2))
