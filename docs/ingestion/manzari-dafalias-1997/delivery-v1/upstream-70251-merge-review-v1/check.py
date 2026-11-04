from pathlib import Path
import sys,json,hashlib,subprocess,importlib.util,math,ast
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent;UP='70251ec7ab4d18029d9a5e6ad30114acd31a662f';sys.dont_write_bytecode=True
sha=lambda b:hashlib.sha256(b).hexdigest()
transport=['tools/build_experiments.py','web/experiments.mjs','tools/test_experiments.mjs','tests/test_web_experiments.py','tests/test_public_data.py'];names=transport+['tools/build_web.py','tools/check_native_fixture_contracts.py'];bindings={}
for n in names:
 data=(ROOT/n).read_bytes();old=subprocess.check_output(['git','show',UP+':'+n],cwd=ROOT);bindings[n]={'current_sha256':sha(data),'upstream_sha256':sha(old),'byte_exact_upstream':data==old}
for n in transport:assert bindings[n]['byte_exact_upstream']
assert b'compressed=True' not in (ROOT/'tools/build_web.py').read_bytes()
assert b'def write_payload' not in (ROOT/'tools/build_experiments.py').read_bytes()
assert (ROOT/'tools/build_web.py').read_bytes()==subprocess.check_output(['git','show','aecfa1890:tools/build_web.py'],cwd=ROOT)
n='tools/check_native_fixture_contracts.py';current=(ROOT/n).read_text();old=subprocess.check_output(['git','show',UP+':'+n],cwd=ROOT).decode()
reversed=current.replace("MD='manzari-dafalias-1997-constant-m-be-v1'\nMD_HASH='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'\n",'')
start=reversed.index('    if MD in definitions:');end=reversed.index('    elif SCLAY in definitions:',start)
reversed=reversed[:start]+'    if SCLAY in definitions:'+reversed[end+len('    elif SCLAY in definitions:'):]
reversed=reversed.replace("'current-seventeen MD/SCLAY1/Ramberg/Duncan/OCC' if MD in definitions else ",'');assert reversed==old
spec=importlib.util.spec_from_file_location('contracts',ROOT/n);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for k,v in m.BASELINE_FIVE_V03.items():assert sha((ROOT/'models'/f'{k}.json').read_bytes())==v
assert sha((ROOT/'models'/f'{m.MD}.json').read_bytes())==m.MD_HASH
model=json.loads((ROOT/'models'/f'{m.OCC}.json').read_text());p={k:v['default'] for k,v in model['parameters'].items()};volume=model['state'][1]['initial']/1.0001;pressure=p['pref']*math.exp((p['Gamma']+p['lambda_c']-p['kappa']-volume)/p['lambda_c']);residual=abs(pressure-100000)/100000;message=f'failed knot 1 residual {residual} trials 1 de0 0.0001 de1 0\ndrained replay failed: {m.OCC} singular mixed-control system; last committed knot retained\n'
old16={**m.PRIOR_THIRTEEN,m.DUNCAN:m.DUNCAN_HASH,m.RAMBERG:m.RAMBERG_HASH,m.SCLAY:m.SCLAY_HASH};new16={**old16,**m.BASELINE_FIVE_V03};positive=[]
for label,definitions in [('old16',old16),('migrated16',new16),('old17',{**old16,m.MD:m.MD_HASH}),('migrated17',{**new16,m.MD:m.MD_HASH})]:
 m.check_recorded_failure(message,definitions,root=ROOT);positive.append(label)
refusals=[]
for label,definitions in [('old17',{**old16,m.MD:m.MD_HASH}),('migrated17',{**new16,m.MD:m.MD_HASH})]:
 badmaps=[]
 for k in definitions:
  d=dict(definitions);d[k]='0'*64;badmaps.append(d)
 for k in [m.SCLAY,m.DUNCAN,m.RAMBERG]:
  d=dict(definitions);d.pop(k);badmaps.append(d)
 badmaps.append({**definitions,'unexpected-model':'0'*64})
 mixed={**definitions,'linear-elastic':m.BASELINE_FIVE_V03['linear-elastic'] if label=='old17' else m.PRIOR_THIRTEEN['linear-elastic']};badmaps.append(mixed)
 for i,d in enumerate(badmaps):
  try:m.check_recorded_failure(message,d,root=ROOT)
  except AssertionError:refusals.append(label+'/'+str(i))
  else:raise AssertionError('admitted unqualified set '+label+'/'+str(i))
 for bad in [message.replace('trials 1','trials 2'),message.replace('de0 0.0001','de0 0.0002'),message.replace(str(residual),str(residual+0.1))]:
  try:m.check_recorded_failure(bad,definitions,root=ROOT)
  except AssertionError:refusals.append(label+'/signature')
  else:raise AssertionError('admitted changed signature')
report={'identity':'upstream-70251-md1997-merge-source-review-v1','status':'accepted','reviewer_run':'/root/md1997_upstream_merge_review','scope':'seven source files; pure data and exact contract-map checks; no compiled builds/material execution','upstream_commit':UP,'source_bindings':bindings,'positive_exact_maps':positive,'strict_refusal_count':len(refusals),'checks':['five transport files byte-exact upstream: single implementation','build_web byte-exact aecfa1890; obsolete compressed argument absent','native helper exactly reverses to upstream by removing only MD identity, exact17 branch and label','upstream historical16 branches, strict failure signature, residual bound and subprocess checks byte-preserved','all5 currentbaseline and MD hashes match actual model files','full old/migrated16 and17 exact maps accepted; altered membership/hash/partialmigration/signature refused','legacy experiment decode and bounded streamed gzip positive/negative suite passes','ensemble measurements still route through fetchExperiment'],'test_results':{'test_web_experiments':'PASS4','node_test_experiments':'PASS','pure_map_refusals':len(refusals)},'retained_incomplete_check':'Reviewer began full test_public_data; interrupted own process during corpus setup to avoid duplicate coordinator actual994 work. No completed full-suite claim.','blocking_findings':[],'remaining_coordinator_checks':['actual994 new upstream transport byte identity and size','final compiled CI, package and live browser qualification']}
(OUT/'decision.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'accepted','decision_sha256':sha((OUT/'decision.json').read_bytes()),'refusals':len(refusals)}))
