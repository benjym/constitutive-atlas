import copy,contextlib,hashlib,io,json,math,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parent;I=P/'implementation-v1';A=P/'coordinator-v1/audit-v2';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();policy=json.loads((I/'cases.json').read_text());rows=[]
def adv(t,f=None,retry=0,slope=78000000.):
 f=[1.] if f is None else f
 return {'ok':True,'state':[0.,slope*t[1],slope*t[1],0.,0.,0.,.7],'diagnostics':{'increment_fractions':f[:],'accepted_increments':[[q*v for v in t] for q in f],'partition_retries':retry,'substeps':len(f)}}
for c in policy['cases']:
 n=c['id'];x={'id':n,'passed':True}
 if c['kind']=='helper':
  x.update({k:copy.deepcopy(c[k]) for k in ['ok','evaluator_calls','selected_h','parent','total','direction','initial_h']});x['value']=c['value'] if c['ok'] else 0;x['base']=adv(c['total'],slope=-78e6 if n=='negative-slope' else 0 if n=='zero-slope' else 78e6);x['probes']=[]
  for k in range(c['probe_records']):
   hh=math.ldexp(c['initial_h'],-k);t=[u+hh*d for u,d in zip(c['total'],c['direction'])];rep=n!='unrepresentable';v={'h':hh,'increment':t,'representable':rep,'comparable':False,'finite_slope':False,'slope':0,'advance':{'ok':False,'state':[]}}
   if rep:
    a=adv(t)
    if n=='exact-boundary' or n in ['jump-recovery','protocol3-direction'] and k==0:
     a=adv(t,[.5,.5]);a['state'][1]-=15600;a['state'][2]-=15600
    if n=='failed-probe-reset' and k==1:a['ok']=False;a['state']=x['base']['state'][:]
    if n=='nonfinite-probe-reset' and k in [1,2,3]:
     if k==1:a['state'][1]=None
     elif k==2:a['state']=a['state'][:1]
     else:a['state']=[]
    if n=='overflow-slope-reset' and k==1:a['state'][1]=a['state'][2]=1e308
    if n=='unstable-slopes':a=adv(t,slope=78e6 if k%2==0 else 156e6)
    if n in ['negative-slope','zero-slope']:a=adv(t,slope=-78e6 if n=='negative-slope' else 0)
    if n=='protocol3-direction':
     a['state'][0]=78e6*t[0];a['state'][1]=a['state'][2]=0
     if k==0:a['diagnostics']=adv(t,[.5,.5])['diagnostics'];a['state'][0]-=15600
    comp=a['ok'] and a['diagnostics']['increment_fractions']==[1.];valid=comp and len(a['state'])==7 and all(type(z) in [int,float] and math.isfinite(z) for z in a['state']);slope=0
    if valid:
     obs=lambda z:z[0]-.5*(z[1]+z[2]) if n=='protocol3-direction' else .5*(z[1]+z[2]);slope=(obs(a['state'])-obs(x['base']['state']))/hh
    v.update(advance=a,comparable=comp,finite_slope=valid and math.isfinite(slope),slope=slope if math.isfinite(slope) else None)
   x['probes'].append(v)
  if n=='unrepresentable':x['empty_base']=c['empty_base']
  if n=='recovery-after-exhaustion':x['unavailable_calls']=11
 elif c['kind']=='partition':
  a=c['base_total'];b=c['probe_total'];f=[1/3,1-1/3];base=adv(a,f,1);base['diagnostics']['accepted_increments']=[[v/3 for v in a],[v-v/3 for v in a]];probe=copy.deepcopy(base);probe['diagnostics']['accepted_increments']=[[base['diagnostics']['accepted_increments'][i][j]+f[i]*(b[j]-a[j])for j in range(6)]for i in range(2)];diag=probe['diagnostics']
  if n=='reject-counts':diag['increment_fractions'].append(.1)
  if n=='reject-order':diag['increment_fractions'].reverse()
  if n=='reject-retry':diag['partition_retries']=0
  if n=='reject-missing-increments':diag['accepted_increments']=[]
  if n=='reject-tensor-length':diag['accepted_increments'][0].pop()
  if n=='reject-nonfinite-fraction':diag['increment_fractions'][0]=None
  if n=='reject-coverage':base['diagnostics']['increment_fractions']=[.4,.4];diag['increment_fractions']=[.4,.4]
  if n=='reject-affine-defect':diag['accepted_increments'][0][1]+=1e-10
  if n=='reject-unchanged-channel':diag['accepted_increments'][0][5]=float.fromhex('0x0.0000000000001p-1022')
  x.update(base=base,probe=probe,base_total=a,probe_total=b)
 elif c['kind']=='elastic':
  x.update({k:copy.deepcopy(c[k]) for k in ['parameters','settings','protocol','axial','reference','current_axial']});de=[.001,-.00025,-.00025,0,0,0];x.update(parent=c['initial'],increment=de,advance={'ok':True,'state':c['state']});f=[.5,.5] if n=='analytic-rate-control' else [1.];probe=de[:];probe[1]+=1e-6;probe[2]+=1e-6
  for label,t in [('affine_base',de),('affine_probe',probe)]:
   z=adv(t,f);tr=sum(t[:3]);z['state']=[100000+12e6*tr+24e6*t[j] for j in range(3)]+[24e6*t[j] for j in range(3,6)]+[.7-1.7*tr];x[label]=z
 elif c['kind']=='recovery':
  x.update({k:copy.deepcopy(c[k]) for k in ['parameters','settings','protocol','axial','reference','current_axial']});invalid=c['initial'][:6]+[-1.];x.update(initial=c['initial'],invalid_parent=invalid,failure={'ok':False,'state':invalid},recovery={'ok':True,'state':[130000,100000,100000,0,0,0,.69915]})
 rows.append(x)
fixture={'identity':policy['identity'].replace('cases','fixture'),'passed':True,'cases':rows};(D/'synthetic-full25.json').write_text(json.dumps(fixture,indent=2)+'\n')
art=D/'synthetic-engine.mjs';art.write_text('synthetic text; never imported or executed\n');payload=art.with_suffix('.wasm');payload.write_text('synthetic payload; never loaded\n')
def report(label,fixture,backend='native',command_override=None):
 d=D/label;d.mkdir();text=json.dumps(fixture)+'\n';calls=[{'repeat':i,'returncode':0,'stdout':text,'stderr':'','response':fixture} for i in range(2)]
 cmd=[str(art)] if backend=='native' else ['node',str(I/'collect_wasm.mjs'),str(art)]
 if command_override:cmd=command_override
 processes=[{'command':cmd,'returncode':0,'stdout':text,'stderr':''} for _ in range(2)] if backend=='native' else [{'command':cmd,'returncode':0,'stdout':'\n'.join(json.dumps({k:v for k,v in call.items() if k!='response'})for call in calls)+'\n','stderr':''}]
 proc=d/'processes.json';proc.write_text(json.dumps(processes));identity={'backend':backend,'manifest_sha256':h(I/'manifest.json'),'source_freeze_sha256':h(I/'source-freeze.json'),'cases_sha256':h(I/'cases.json'),'artifact_path':str(art),'artifact_sha256':h(art),'processes_sha256':h(proc)}
 if backend=='wasm':identity.update(wasm_path=str(payload),wasm_sha256=h(payload))
 p=d/'report.json';p.write_text(json.dumps({'identity':identity,'calls':calls,'processes':processes}));return p
results=[]
def check(label,paths,expected,audit=True):
 script=A/'check_audit.py' if audit else I/'check_saved.py';out=D/(label+'-checks.json')
 with patch.object(sys,'argv',[str(script)]+[str(p) for p in paths]+['--output',str(out)]),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:code=ex.code
 r=json.loads(out.read_text());results.append({'case':label,'expected_pass':expected,'passed':r['passed'],'exit':code});assert r['passed']==expected,label
native=report('valid-native',fixture);wasm=report('valid-wasm',fixture,'wasm');check('valid-native-original',[native],True,False);check('valid-pair-original',[native,wasm],True,False);check('valid-native-audit',[native],True);check('valid-pair-audit',[native,wasm],True)
for name in ['fabricated-audit','inconsistent-observed-slope']:check('old-'+name,[P/'independent-review-v1'/name/'report.json'],False)
byid={c['id']:i for i,c in enumerate(rows)}
def mutate(name,fn):
 f=copy.deepcopy(fixture);fn(f);p=report(name,f);check(name,[p],False)
mutate('bad-slope',lambda f:f['cases'][0]['probes'][-1].update(slope=79e6))
mutate('bad-observer-state',lambda f:f['cases'][0]['probes'][-1]['advance']['state'].__setitem__(1,999999999))
mutate('empty-partition',lambda f:f['cases'][byid['non-dyadic-affine']].update(base={},probe={}))
mutate('retry-lie',lambda f:f['cases'][0]['probes'][-1]['advance']['diagnostics'].update(partition_retries=1))
mutate('zero-actual-increments',lambda f:f['cases'][byid['analytic-rate-control']]['affine_base']['diagnostics'].update(accepted_increments=[[0]*6,[0]*6]))
mutate('wrong-representability',lambda f:f['cases'][byid['unrepresentable']]['probes'][0].update(representable=True))
mutate('selection-lie',lambda f:f['cases'][0].update(selected_h=.0001))
mutate('nonfinite-literal',lambda f:f['cases'][0]['base']['state'].__setitem__(1,float('nan')))
p=report('bad-command',fixture,command_override=['unrelated']);check('bad-command',[p],False)
p=report('overflow',fixture);j=json.loads(p.read_text());j['calls'][0]['stdout']='{"cases":[],"overflow":1e999}';p.write_text(json.dumps(j));check('overflow',[p],False)
(D/'checks.json').write_text(json.dumps({'compiled_calls':0,'supplement_manifest_sha256':h(A/'manifest.json'),'results':results},indent=2)+'\n');print(results)
