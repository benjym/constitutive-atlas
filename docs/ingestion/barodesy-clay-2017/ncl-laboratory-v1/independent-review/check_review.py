"""Independent saved-only interface/reference audit; no compiled calls.

The general rounded-initial isotropic Bernoulli solution below is derived from
bodyEqs1-10 and does not import the production/reference integration code.
"""
from pathlib import Path
from decimal import Decimal,localcontext
import argparse,copy,hashlib,importlib.util,json,math,struct,sys
HERE=Path(__file__).resolve().parent;PACKET=HERE.parent;ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unique(pairs):
 d={}
 for k,v in pairs:
  assert k not in d,'duplicate key '+k
  d[k]=v
 return d
def read(p):return json.loads(Path(p).read_text(),object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def bits(x):return struct.pack('>d',float(x)).hex()
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def exact(a,b):
 if isinstance(b,bool):return type(a)is bool and a==b
 if isinstance(b,dict):return type(a)is dict and set(a)==set(b) and all(exact(a[k],v)for k,v in b.items())
 if isinstance(b,list):return type(a)is list and len(a)==len(b)and all(exact(u,v)for u,v in zip(a,b))
 if type(b)in(int,float):return finite(a)and a==b
 return type(a)is type(b)and a==b
def vector(v,n):assert type(v)is list and len(v)==n and all(finite(x)for x in v)
def sine(x):
 term=total=x
 for k in range(1,100):
  term*=-x*x/Decimal((2*k)*(2*k+1));total+=term
  if abs(term)<Decimal('1e-105'):return total
 raise AssertionError('sine convergence')
def rounded_pressure(parameters,initial,volume):
 with localcontext()as ctx:
  ctx.prec=100
  phi,N,lam,kap,ss=map(Decimal.from_float,map(float,parameters));p0=Decimal.from_float(float(initial[0]));v0=1+Decimal.from_float(float(initial[6]));x=volume if isinstance(volume,Decimal)else Decimal.from_float(float(volume));c5=(1+sine(phi))/(1-sine(phi));t=c5*lam;B=(t*Decimal(2).ln()).exp()
  c3=Decimal(3).sqrt()*(1/kap-1/lam)/(B+(-t*Decimal(500).ln()).exp()-2)
  z0=(c5*(v0.ln()-N+lam*(2*p0/ss).ln())).exp()
  correction=1+(1-z0/B)*((t*c3/Decimal(3).sqrt()*B*x).exp()-1)
  assert correction>0
  p=p0*(x/lam-correction.ln()/t).exp()
  # Parent oracle chooses decimal .11; quantify both parameter and initial-rounding effects.
  ideal=p0*(x/Decimal('.11')).exp()
  return float(p),float(abs(p-ideal)/ideal),float((1+Decimal.from_float(float(initial[6])))*(-x).exp()-1)
def validate_rows(requests,rows,policy,catalogue,model):
 ids=[c['id']for c in policy['cases']];assert len(ids)==7 and len(set(ids))==7
 assert len(requests)==7 and [r['id']for r in requests]==ids
 example=read(PACKET.parent/'ncl-example-v1/example.json');params=list(example['parameters'].values());default=[v for f in model['state']for v in(f['initial']if f['shape']=='sym'else[f['initial']])]
 expected_stress={'source':'state','name':'sigma','measure':'cauchy','scope':'effective','tensor_representation':'mandel','sign':'compression_positive'}
 allmetrics={};correction_max=0.;parity=0.;counts={}
 for req,case in zip(requests,policy['cases']):
  s=req['specification'];assert set(req)=={'id','specification'}
  initial=default if case['initial']=='unchanged-model-default'else[0]*6+[example['state']['e']]if case['initial']=='zero-stress-invalid'else example['state']['sigma']+[example['state']['e']]
  expected_settings=policy['settings']|({'rate_tolerance':case['rate_tolerance']}if 'rate_tolerance'in case else{})
  assert s['model']==model['id'] and exact(s['parameters'],params)and exact(s['initial'],initial)
  assert (s['protocol'],s['target'],s['steps'],s['cycles'])==(case['protocol'],case['target'],case['steps'],0)
  assert exact(s['integration_settings'],expected_settings) and s['response_contract']=='stress-scope-0.1'and s['stress_scope']=='effective'
  controls=[0. if i==0 or s['target']==0 else s['target']if i==s['steps']else(s['target']*i)/s['steps']for i in range(s['steps']+1)]
  assert s['loading']['controls_bits']==[bits(x)for x in controls]
 for backend,entries in rows.items():
  assert len(entries)==7 and [row['id']for row in entries]==ids
  total=0;metrics={};allmetrics[backend]=metrics
  for req,row in zip(requests,entries):
   s=req['specification'];r=row['result'];name=req['id'];invalid=name=='invalid-initial'
   if backend=='native':assert type(row['exit_code'])is int and row['exit_code']==int(invalid)and row['stderr']==''
   assert type(r['ok'])is bool and r['ok']is(not invalid)
   assert r['catalogue_hash']==catalogue['sha256']and r['model']==s['model']
   assert r['schema_version']=='0.1'and r['api_version']=='experimental-laboratory-scope-0.1'
   assert exact(r['parameters'],s['parameters'])and exact(r['initial'],s['initial'])
   assert exact(r['integration_settings'],s['integration_settings'])and r['protocol']==s['protocol']and r['steps']==s['steps']
   assert r['stress']==expected_stress and r['pore_pressure']=={'quantity':'change','availability':'unavailable','reason':'not_reconstructed_for_protocol'}
   assert finite(r['elapsed_ms'])and r['elapsed_ms']>=0
   assert r['loading']['controls_bits']==s['loading']['controls_bits']
   assert len(r['loading']['controls'])==s['steps']+1
   assert [bits(x)for x in r['loading']['controls']]==s['loading']['controls_bits']
   assert len(r['points'])==(0 if invalid else s['steps']+1)
   if invalid:assert r['message']=='invalid run specification';continue
   assert r['message']=='';total+=len(r['points'])
   assert r['points'][0]['state']==s['initial']and r['points'][0]['strain']==[0]*6
   metric={'pressure_relative_error':0.,'void_ratio_absolute_error':0.,'rounded_initial_pressure_relative_error':0.,'volume_closure_error':0.,'radial_stress_relative_error':0.,'deviatoric_relative':0.}
   for i,pt in enumerate(r['points']):
    vector(pt['state'],7);vector(pt['strain'],6)
    assert bits(pt['control'])==s['loading']['controls_bits'][i]
    assert all(finite(pt[k])for k in ['control','p','q','q_signed','error'])and pt['u']is None
    assert all(type(pt[k])is int and pt[k]>=0 for k in ['iterations','substeps','rejected'])
    assert pt['state'][6]>=0 and min(pt['state'][:3])>0 and pt['state'][3:6]==[0]*3
    scale=max(abs(x)for x in pt['state'][:6]);mean=sum(pt['state'][:3])/3
    q=math.sqrt(1.5*sum((x-mean)**2 for x in pt['state'][:3]))
    assert abs(pt['p']-mean)/max(1,scale)<1e-12
    assert abs(pt['q']-q)/max(1,scale)<1e-12
    assert abs(pt['q_signed']-(pt['state'][0]-(pt['state'][1]+pt['state'][2])/2))/max(1,scale)<1e-12
    assert pt['strain'][3:]==[0]*3 and pt['strain'][0]==pt['control']
    if s['protocol']==4:assert pt['strain'][:3]==[pt['control']]*3
    if s['protocol']==1:
     radial=max(abs(pt['state'][j]-s['initial'][j])/s['initial'][j]for j in [1,2]);metric['radial_stress_relative_error']=max(metric['radial_stress_relative_error'],radial);assert radial<1e-8 # frozen controlled_step radial-stress stopping criterion
    volume=sum(pt['strain'][:3])
    with localcontext()as ctx:
     ctx.prec=100
     ev=sum((Decimal.from_float(x)for x in pt['strain'][:3]),Decimal(0));v0=1+Decimal.from_float(float(s['initial'][6]));refe=float(v0*(-ev).exp()-1)
     ideal=float(Decimal(100000)*(ev/Decimal('.11')).exp())
    ve=abs(pt['state'][6]-refe);metric['volume_closure_error']=max(metric['volume_closure_error'],ve);assert ve<=policy['gates']['maximum_void_ratio_absolute_error']
    if name in ['ncl-isotropic','ncl-isotropic-refined','ncl-recovery']:
     error=max(abs(x-ideal)/ideal for x in pt['state'][:3]);metric['pressure_relative_error']=max(metric['pressure_relative_error'],error)
     metric['void_ratio_absolute_error']=max(metric['void_ratio_absolute_error'],ve)
     # Preserve the exact sum of actual binary64 caller strains in Decimal.
     corrected,correction,_=rounded_pressure(s['parameters'],s['initial'],ev)
     correction_max=max(correction_max,correction)
     metric['rounded_initial_pressure_relative_error']=max(metric['rounded_initial_pressure_relative_error'],max(abs(x-corrected)/corrected for x in pt['state'][:3]))
     assert error<=policy['gates']['maximum_pressure_relative_error']
     assert pt['state'][0]==pt['state'][1]==pt['state'][2]and pt['q']==0
    if name=='ncl-zero':assert pt['state']==s['initial']and pt['strain']==[0]*6
   metrics[name]=metric
  counts[backend]=total
  ordinary=metrics['ncl-isotropic'];fine=metrics['ncl-isotropic-refined']
  assert all(fine[k]<=ordinary[k]+1e-10 for k in ['pressure_relative_error','void_ratio_absolute_error'])
  clean=lambda x:{k:v for k,v in x.items()if k!='elapsed_ms'}
  assert clean(entries[-1]['result'])==clean(entries[0]['result'])
 for n,w in zip(rows['native'],rows['wasm']):
  assert n['id']==w['id'];rn=n['result'];rw=w['result']
  assert len(rn['points'])==len(rw['points'])
  for a,b in zip(rn['points'],rw['points']):
   for x,y in zip(a['state']+a['strain']+[a['p'],a['q'],a['q_signed']],b['state']+b['strain']+[b['p'],b['q'],b['q_signed']]):
    d=abs(x-y)/max(1,abs(x),abs(y));parity=max(parity,d);assert d<policy['gates']['backend_full_state_normalized_difference']
 return {'successful_caller_points':counts,'backends':allmetrics,'maximum_rounded_initial_and_parameter_oracle_relative_correction':correction_max,'maximum_state_strain_invariant_backend_difference':parity}
def assess():
 policy=read(PACKET/'policy.json');manifest=read(PACKET/'manifest.json')
 for p,h in manifest['files'].items():
  selected=checked_receipt(ROOT,str((PACKET/'manifest.json').relative_to(ROOT)),p,h);assert sha(selected)==h,p
 source=read(PACKET/'source-manifest.json');snapshot=ROOT/source['snapshot']
 for p,h in source['files'].items():assert sha(snapshot/p)==h,p
 retained=read(PACKET/'retained-artifact-receipts.json')
 for p,item in retained.items():assert sha(ROOT/p)==item['sha256']and(ROOT/p).stat().st_size==item['bytes']
 freeze=read(PACKET/'execution-freeze.json')
 known={v['sha256'] for v in retained.values()}
 for p,h in freeze['files'].items():
  if p.startswith(str(PACKET)+'/'):assert sha(p)==h,p
  else:assert h in known,p
 catalogue=read(ROOT/'.local/barodesy2017-ncl-lab-v1/artifacts/native/generated/models.json')
 assert catalogue==read(ROOT/'.local/barodesy2017-ncl-lab-v1/artifacts/wasm/generated/models.json')
 assert len(catalogue['models'])==13
 for model in catalogue['models']:assert model==read(snapshot/'models'/f"{model['id']}.json")
 model=next(m for m in catalogue['models']if m['id']=='barodesy-clay-2017')
 requests=read(PACKET/'results/requests.json');rows={b:read(PACKET/f'results/{b}.json')for b in ['native','wasm']}
 metrics=validate_rows(requests,rows,policy,catalogue,model)
 mutations=[('duplicate backend ID',lambda q,z:z['native'].append(copy.deepcopy(z['native'][0]))),('missing point',lambda q,z:z['wasm'][0]['result']['points'].pop()),('wrong parameter echo',lambda q,z:z['wasm'][0]['result']['parameters'].__setitem__(0,.5)),('wrong CLI exit',lambda q,z:z['native'][0].__setitem__('exit_code',1)),('wrong loading bits',lambda q,z:z['wasm'][0]['result']['loading']['controls_bits'].__setitem__(1,'0000000000000000')),('wrong stress invariant',lambda q,z:z['wasm'][0]['result']['points'][2].__setitem__('p',5.)),('unpreserved zero state',lambda q,z:z['wasm'][4]['result']['points'][1]['state'].__setitem__(6,1.)),('false invalid success',lambda q,z:z['wasm'][5]['result'].__setitem__('ok',True)),('missing request',lambda q,z:q.pop()),('non-isotropic strain',lambda q,z:z['wasm'][0]['result']['points'][2]['strain'].__setitem__(1,.1))]
 rejected=[]
 for label,mutate in mutations:
  q,z=copy.deepcopy(requests),copy.deepcopy(rows);mutate(q,z)
  try:validate_rows(q,z,policy,catalogue,model)
  except (AssertionError,ValueError,IndexError,KeyError):rejected.append(label)
  else:raise AssertionError('mutation admitted '+label)
 spec=importlib.util.spec_from_file_location('frozen_ncl_assessor',PACKET/'check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assert module.assess(PACKET/'results')==read(PACKET/'results/assessment.json')
 doc=read(PACKET/'laboratory-document.json');assert doc['specification']==requests[0]['specification']and doc['result']==rows['wasm'][0]['result']and doc['catalogue_hash']==catalogue['sha256']
 return {'version':'barodesy2017-ncl-independent-interface-review-v1','pass':True,'reviewer_run_id':'/root/barodesy2017_agent_review','source_snapshot_files':len(source['files']),'durable_artifacts_verified':len(retained),'compiled_catalogue_models':13,'metrics':metrics,'rejected_mutations':rejected,'frozen_parent_assessment_reproduced':True,'proposed_document_exact_first_wasm_result':True,'opaque_wire_retention':False,'compiled_calls':0,'builds':0,'browser_live_qualification':False,'root_registration_reviewed_as_installed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(assess(),indent=2)+'\n')
