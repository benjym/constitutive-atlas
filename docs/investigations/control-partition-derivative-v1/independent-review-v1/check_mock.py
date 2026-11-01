import copy,contextlib,hashlib,io,json,math,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;S=D.parent/'implementation-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();policy=json.loads((S/'cases.json').read_text());rows=[];artifact=D/'synthetic-artifact.txt';artifact.write_text('never executed\n')
for c in policy['cases']:
 x={'id':c['id'],'passed':True}
 if c['kind']=='helper':
  x.update({k:copy.deepcopy(c[k]) for k in ['ok','evaluator_calls','selected_h','parent','total','direction','initial_h']});x['value']=c['value'];x['base']={'state':[0,0,0,0,0,0,.7]};x['probes']=[]
  for k in range(c['probe_records']):
   hh=math.ldexp(c['initial_h'],-k);state=[0,78000000*hh,78000000*hh,0,0,0,.7];comparable=True;finite=True;ok=True;slope=c['value'] or 0
   if c['id'] in ['jump-recovery','protocol3-direction','exact-boundary'] and k==0:comparable=False;finite=False
   if c['id']=='exact-boundary':comparable=False;finite=False
   if c['id']=='failed-probe-reset' and k==1:comparable=False;finite=False;ok=False
   if c['id']=='overflow-slope-reset' and k==1:finite=False
   if c['id']=='nonfinite-probe-reset' and k in [1,2,3]:finite=False;state=[0,None,0,0,0,0,.7] if k==1 else [0] if k==2 else []
   v={'h':hh,'increment':[u+hh*d for u,d in zip(c['total'],c['direction'])],'representable':c['id']!='unrepresentable','comparable':comparable,'finite_slope':finite,'slope':slope,'advance':{'ok':ok,'state':state}}
   x['probes'].append(v)
  if c['id']=='unrepresentable':x['empty_base']=c['empty_base']
  if c['id']=='recovery-after-exhaustion':x['unavailable_calls']=11
 elif c['kind']=='partition':
  x.update(base={},probe={},base_total=c['base_total'],probe_total=c['probe_total'])
 elif c['kind']=='elastic':
  x.update({k:copy.deepcopy(c[k]) for k in ['parameters','settings','protocol','axial','reference','current_axial']});x.update(parent=[100000]*3+[0]*3+[.7],increment=[.001,-.00025,-.00025,0,0,0],advance={'ok':True,'state':c['state']})
  n=2 if c['id']=='analytic-rate-control' else 1
  for label in ['affine_base','affine_probe']:x[label]={'ok':True,'diagnostics':{'increment_fractions':[1/n]*n,'accepted_increments':[[0]*6 for _ in range(n)]}}
 elif c['kind']=='recovery':
  x.update({k:copy.deepcopy(c[k]) for k in ['parameters','settings','protocol','axial','reference','current_axial']});x.update(initial=c['initial'],invalid_parent=[100000]*3+[0]*3+[-1],failure={'ok':False,'state':[100000]*3+[0]*3+[-1]},recovery={'ok':True,'state':[130000,100000,100000,0,0,0,.69915]})
 rows.append(x)
fixture={'identity':policy['identity'].replace('cases','fixture'),'passed':True,'cases':rows}
# Intentionally fabricated reports test independent checking, never actual evidence.
def run(label,fixture,process_exit=0):
 outdir=D/label;outdir.mkdir();stdout=json.dumps(fixture)+'\n';calls=[{'repeat':i,'returncode':0,'stdout':stdout,'stderr':'','response':copy.deepcopy(fixture)} for i in range(2)];processes=[{'command':[str(artifact)],'returncode':process_exit,'stdout':stdout,'stderr':''} for i in range(2)];proc=outdir/'processes.json';proc.write_text(json.dumps(processes));report={'identity':{'backend':'native','manifest_sha256':h(S/'manifest.json'),'source_freeze_sha256':h(S/'source-freeze.json'),'cases_sha256':h(S/'cases.json'),'artifact_path':str(artifact),'artifact_sha256':h(artifact),'processes_sha256':h(proc)},'calls':calls,'processes':processes};inp=outdir/'report.json';inp.write_text(json.dumps(report));output=outdir/'checks.json'
 with patch.object(sys,'argv',[str(S/'check_saved.py'),str(inp),'--output',str(output)]),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(S/'check_saved.py'),run_name='__main__')
  except SystemExit as ex:code=ex.code
 return {'case':label,'exit':code,'passed':json.loads(output.read_text())['passed']}
results=[run('fabricated-audit',fixture)]
# Even obvious state/slope inconsistency passes because slopes are trusted.
f=copy.deepcopy(fixture);f['cases'][0]['probes'][-1]['advance']['state'][1]=999999999
results.append(run('inconsistent-observed-slope',f))
f=copy.deepcopy(fixture);f['cases']=[f['cases'][0]];results.append(run('missing24',f))
results.append(run('late-exit',fixture,7))
(D/'mock-checks.json').write_text(json.dumps({'compiled_calls':0,'synthetic_reports_only':True,'results':results},indent=2)+'\n');print(results)
