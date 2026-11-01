import json,hashlib,tempfile,subprocess,copy
from pathlib import Path
D=Path(__file__).resolve().parent;E=D.parents[1]/'execution-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(E/'manifest.json')=='5e746cc6f472db3396866ecb5f36019f6764b2189fd95c7eb03d50b9c2450da4'
for f,h in json.loads((E/'manifest.json').read_text()).items():assert sha(E/f)==h
p=json.loads((E/'requests.json').read_text())
for f,h in p['source_inputs'].items():assert sha(E.parent/f)==h
z=p['special']['initial'];cases={}
for c in p['cases']:
 coords=c.get('coordinates',c.get('controls',[c.get('target',.01)*i/c.get('steps',100) for i in range(c.get('steps',100)+1)]))
 points=[]
 for coord in coords:
  cp=next((x for x in c.get('checkpoints',[]) if x.get('axial_strain',x.get('t'))==coord),None)
  state=cp['sigma_Pa']+[cp['e']]+cp['alpha']+[0.] if cp else c['initial']
  strain=[coord,0.,0.,0.,0.,0.]
  if cp:strain=cp.get('strain',[coord,cp.get('radial_strain',0),cp.get('radial_strain',0),0,0,0])
  points.append({'coordinate':coord,'state':state,'strain':strain})
 if 'expected_state' in c:points[-1]['state']=c['expected_state']
 r={'ok':True,'points':points}
 if c['kind']=='controls':r['response_metadata']={'loading':{'controls_bits':c['controls_bits']}}
 if c['group']=='restart':r['restart_receipt']={'index':256,'all_persistent_state':points[255]['state'][:13]}
 cases[c['id']]=r
special={}
for name in ['zero','hold','clean-valid','recovery-negative-pressure','recovery-alpha','recovery-nan-parameter','rollback-recovery']:special[name]={'ok':True,'state':z}
for name in ['invalid-negative-pressure','invalid-alpha','invalid-nan-parameter','forced-rollback']:special[name]={'ok':False,'state':z,'diagnostics':{'partition_committed':False}}
linstate=z.copy();linstate[13]=1e-5
special['linearize']={'ok':True,'tangent_ok':True,'state':linstate,'state_tangent':[[0.]*6 for i in range(14)],'api_version':'experimental-update-linearization-0.1','partition_policy':'accepted_fixed','branch_policy':'selected_fixed','diagnostics':{'increment_fractions':[1.]}}
for j in range(6):
 for sign in [-1,1]:special[f'fd-{j}-{sign}']={'ok':True,'state':linstate,'diagnostics':{'increment_fractions':[1.]}}
report={'synthetic_DO_NOT_USE_AS_BACKEND_EVIDENCE':True,'identity':{'backend':'synthetic-only','model_sha256':p['model_sha256'],**{k:sha(E/f) for k,f in [('requests_sha256','requests.json'),('policy_sha256','POLICY.md'),('manifest_sha256','manifest.json')]}},'cases':cases,'special':special}
first=p['cases'][0]['id'];inter=next(c['id'] for c in p['cases'] if c['group']=='interior')
tests=[]
def run(name,mutate,expected):
 r=copy.deepcopy(report);mutate(r)
 with tempfile.TemporaryDirectory(dir=D) as tmp:
  inp=Path(tmp)/'SYNTHETIC.json';out=Path(tmp)/'checks.json';inp.write_text(json.dumps(r))
  proc=subprocess.run(['python3','-B',str(E/'check_reports.py'),str(inp),'--output',str(out)],capture_output=True,text=True)
  res=json.loads(out.read_text()) if out.exists() else None;passed=bool(res and res['passed'])
  tests.append({'test':name,'checker_accepted':passed,'expected':expected,'expectation_met':passed==expected,'exit_code':proc.returncode,'failed_checks':res['failures'] if res else None,'stderr':proc.stderr[:600]})
run('synthetic ideal baseline',lambda r:None,True)
run('missing case',lambda r:r['cases'].pop(first),False)
run('missing reference checkpoint',lambda r:r['cases'][first]['points'].pop(1),False)
run('wrong alpha source',lambda r:r['cases'][inter]['points'][-1]['state'].__setitem__(7,3.),False)
run('wrong control bits',lambda r:r['cases'][first]['response_metadata']['loading']['controls_bits'].__setitem__(0,'bad'),False)
run('wrong identity hash',lambda r:r['identity'].__setitem__('model_sha256','0'*64),False)
run('invalid input accepted',lambda r:r['special']['invalid-alpha'].__setitem__('ok',True),False)
run('missing rollback state',lambda r:r['special']['forced-rollback'].pop('state'),False)
run('unavailable tangent',lambda r:r['special']['linearize'].__setitem__('tangent_ok',False),False)
run('FD changed partition',lambda r:r['special']['fd-0-1']['diagnostics'].__setitem__('increment_fractions',[.5,.5]),False)
run('missing restart receipt',lambda r:r['cases']['restart-replay'].pop('restart_receipt'),False)
run('corrupt restart receipt values',lambda r:r['cases']['restart-replay'].__setitem__('restart_receipt',{'index':-1,'all_persistent_state':[]}),False)
run('wrong noncheckpoint coordinate',lambda r:r['cases'][inter]['points'][1].__setitem__('coordinate',-99),False)
run('unrecognized backend label',lambda r:r['identity'].__setitem__('backend','other-backend'),False)
(D/'checks.json').write_text(json.dumps({'scope':'synthetic checker corruption study, not backend evidence','manifest_sha256':sha(E/'manifest.json'),'tests':tests},indent=2)+'\n')
print(json.dumps(tests,indent=2))
