"""Independent synthetic protocol/raw witnesses; no loader or compiled code is executed."""
import argparse,copy,json,sys,tempfile,hashlib
from pathlib import Path


def run(root):
 sys.path.insert(0,str(root))
 from tools import research_rate_observations_v3 as rates
 from tools import research_rate_parity_v3 as wrapper
 name='docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/model.json';model=json.loads((root/name).read_text());digest=rates.digest([model])
 parameters=[p['default'] for p in model['parameters'].values()];state=[100000.]*3+[0.]*3+[.8];increment=[.001,0.,0.,0.,0.,0.]
 csv=lambda v:','.join(format(x,'.17g')for x in v)
 args=[model['id'],csv(parameters),csv(state),csv(increment)]
 base={'id':'baseline','args':list(args),'expectation':{'kind':'accuracy','ok':True,'values':[1.]*7,'absolute_budgets':[.01]*7,'parity_budgets':[.01]*7}}
 finite={'id':'finite','args':list(args),'expectation':{'kind':'finite_only','ok':True}}
 negative={'id':'negative','args':[args[0],args[1],csv(state[:-1]+[-.1]),args[3]],'expectation':{'kind':'reject','ok':False}}
 recovery=copy.deepcopy(base);recovery.update(id='recovery',recovery_of='baseline',after_rejection='negative')
 protocol={'version':'research-instantaneous-rate-protocol-0.3','files':{name:rates.sha(root/name)},'model_file':name,'model_definition':model,'finite_only_parity':{'norm':'scaled_component_max','budget':1e-10},'cases':[base,finite,negative,recovery]}
 descriptor={'models':[model],'sha256':digest}
 rows=[]
 def success(c,value=None):
  return {'ok':c['expectation']['ok'],'model':model['id'],'catalogue_hash':digest,'parameters':[float(x) for x in c['args'][1].split(',')],'state':[float(x) for x in c['args'][2].split(',')],'increment':[float(x)for x in c['args'][3].split(',')],'values':([1.]*7 if value is None else value) if c['expectation']['ok'] else None,'message':'' if c['expectation']['ok']else'unsupported research rate request'}
 with tempfile.TemporaryDirectory(prefix='tagged-v3-independent-') as td:
  folder=Path(td)
  def write(name,value,raw=False):
   p=folder/name;p.write_text(value if raw else json.dumps(value,allow_nan=False)+'\n');return p
  pp=write('protocol.json',protocol)
  def checked(doc):
   write('protocol.json',doc)
   try:rates.checked_protocol(pp)
   except Exception as exc:return {'accepted':False,'exception':type(exc).__name__,'message':str(exc)}
   return {'accepted':True}
  def mutation(name,change,expected=False):
   d=copy.deepcopy(protocol);change(d);out=checked(d);rows.append({'name':name,'expected_accepted':expected,'observed':out,'matches_expected':out['accepted']==expected})
  mutation('genuine-tagged-protocol',lambda d:None,True)
  mutation('missing-explicit-tag',lambda d:d['cases'][1]['expectation'].pop('kind'))
  mutation('unknown-explicit-tag',lambda d:d['cases'][1]['expectation'].update(kind='support'))
  mutation('tag-status-mismatch',lambda d:d['cases'][1]['expectation'].update(ok=False))
  mutation('accuracy-missing-source-budgets',lambda d:d['cases'][0]['expectation'].pop('absolute_budgets'))
  mutation('reject-forged-source-values',lambda d:d['cases'][2]['expectation'].update(values=[0.]*7))
  mutation('material-leading-whitespace-CSV',lambda d:d['cases'][1]['args'].__setitem__(3,' 10,0,0,0,0,0'))
  mutation('material-unicode-digit-CSV',lambda d:d['cases'][1]['args'].__setitem__(3,'١,0,0,0,0,0'))
  mutation('finite-forged-source-values',lambda d:d['cases'][1]['expectation'].update(values=[0.]*7))
  mutation('finite-forged-source-budgets',lambda d:d['cases'][1]['expectation'].update(absolute_budgets=[1e300]*7))
  mutation('finite-missing-global-parity',lambda d:d.pop('finite_only_parity'))
  mutation('finite-bool-global-budget',lambda d:d['finite_only_parity'].update(budget=True))
  mutation('finite-negative-global-budget',lambda d:d['finite_only_parity'].update(budget=-1))
  mutation('material-wrong-parameter-arity',lambda d:d['cases'][0]['args'].__setitem__(1,'1,2,3'))
  mutation('material-wrong-state-arity',lambda d:d['cases'][0]['args'].__setitem__(2,'1,2'))
  mutation('material-wrong-increment-arity',lambda d:d['cases'][0]['args'].__setitem__(3,'1,2'))
  mutation('nonfinite-input-token',lambda d:d['cases'][1]['args'].__setitem__(3,'1e999,0,0,0,0,0'))
  mutation('bool-accuracy-output',lambda d:d['cases'][0]['expectation']['values'].__setitem__(0,True))
  mutation('recovery-different-source-expectation',lambda d:d['cases'][3]['expectation']['values'].__setitem__(0,2))
  mutation('recovery-rejected-baseline',lambda d:d['cases'][3].update(recovery_of='negative'))
  mutation('recovery-nonimmediate-explicit-reject',lambda d:d['cases'].insert(3,dict(copy.deepcopy(finite),id='inserted')))
  # Deliberately expected to reject under the review requirement of immediate recovery relations.
  mutation('recovery-relation-removed',lambda d:(d['cases'][3].pop('after_rejection'),d['cases'].insert(3,dict(copy.deepcopy(finite),id='inserted'))))
  # Python float accepts these; literal C++ driver uses stod and consumes the full token.
  mutation('material-underscore-CSV',lambda d:d['cases'][1]['args'].__setitem__(3,'1_0,0,0,0,0,0'))
  mutation('material-trailing-whitespace-CSV',lambda d:d['cases'][1]['args'].__setitem__(3,'10 ,0,0,0,0,0'))
  write('protocol.json',protocol)
  # All bundles below are fabricated test documents; artifact paths are never executed/reopened.
  def bundle(backend,responses):
   build=write(backend+'-build.json',{'backend':backend,'protocol_sha256':rates.sha(pp),'all_commands_succeeded':True,'artifacts':({'native':{'path':'/nonexecuted-synthetic','sha256':'0'*64}} if backend=='native'else{'loader':{'path':'/nonexecuted-synthetic.mjs','sha256':'0'*64},'wasm':{'path':'/nonexecuted-synthetic.wasm','sha256':'0'*64}})})
   lines=[json.dumps(descriptor)]+[json.dumps(r)for r in responses]
   if backend=='native':rawdoc={'argv':['/nonexecuted-synthetic','--stream'],'stdin':rates.stream_text(protocol),'stdout':'\n'.join(lines)+'\n','stderr':'','returncode':0}
   else:rawdoc=[{'name':'atlas_describe'if i==0 else'atlas_research_rate','types':[]if i==0 else['string']*4,'args':[]if i==0 else protocol['cases'][i-1]['args'],'raw':line}for i,line in enumerate(lines)]
   raw=write(backend+'-raw.json',rawdoc)
   collector='tools/research_rate_observations_v3.py'if backend=='native'else'tools/collect_research_rates_wasm_v3.mjs'
   receipt=write(backend+'-observation.json',{'version':'research-instantaneous-rate-observation-0.3','backend':backend,'completed':True,'protocol_sha256':rates.sha(pp),'build_receipt_sha256':rates.sha(build),'build_receipt':json.loads(build.read_text()),'collector_sha256':rates.sha(root/collector),'transport_sha256':rates.sha(raw)})
   return build,receipt,raw
  def compare(name,change=None,expected='passed'):
   responses=[success(c)for c in protocol['cases']];n=copy.deepcopy(responses);w=copy.deepcopy(responses)
   if change:change(n,w)
   np,wp=bundle('native',n),bundle('wasm',w)
   try:r=wrapper.assess(pp,np,wp);out={'outcome':r['outcome'],'parity_passed':r['parity']['passed'],'finite_only_source_accuracy':r['parity']['finite_only_is_source_accuracy']}
   except Exception as exc:out={'outcome':'rejected','exception':type(exc).__name__,'message':str(exc)}
   rows.append({'name':name,'expected_outcome':expected,'observed':out,'matches_expected':out['outcome']==expected})
  compare('genuine-authenticated-synthetic-bundles')
  compare('same-wrong-accuracy-fails-source-gate',lambda n,w:(n[0].update(values=[2.]*7),n[3].update(values=[2.]*7),w[0].update(values=[2.]*7),w[3].update(values=[2.]*7)),expected='failed')
  compare('finite-only-huge-matching-values-allowed',lambda n,w:(n[1].update(values=[1e308]*7),w[1].update(values=[1e308]*7)))
  compare('finite-only-opposite-extreme-signs-fail',lambda n,w:(n[1].update(values=[1e308]*7),w[1].update(values=[-1e308]*7)),expected='failed')
  compare('material-parser-message-substitution',lambda n,w:n[2].update(message='invalid research CSV'),expected='rejected')
  compare('finite-only-bool-output-rejects',lambda n,w:n[1].update(values=[True]*7),expected='rejected')
  compare('full-decoded-recovery-not-values-only',lambda n,w:n[3].update(values=[1.005]+[1.]*6),expected='rejected')
  compare('echo-truncation-rejects',lambda n,w:n[1].update(parameters=[1.]),expected='rejected')
  def mutate_bundle(name,backend,mutate,expected='rejected',rehash=True):
   responses=[success(c)for c in protocol['cases']];np,wp=bundle('native',responses),bundle('wasm',responses);paths=np if backend=='native'else wp
   raw=json.loads(paths[2].read_text());mutate(raw);write(paths[2].name,raw)
   if rehash:
    receipt=json.loads(paths[1].read_text());receipt['transport_sha256']=rates.sha(paths[2]);write(paths[1].name,receipt)
   try:r=wrapper.assess(pp,np,wp);out={'outcome':r['outcome']}
   except Exception as exc:out={'outcome':'rejected','exception':type(exc).__name__,'message':str(exc)}
   rows.append({'name':name,'expected_outcome':expected,'observed':out,'matches_expected':out['outcome']==expected})
  def mutate_lines(raw,backend,mutate):
   lines=raw['stdout'].splitlines()if backend=='native'else[r['raw']for r in raw];mutate(lines)
   if backend=='native':raw['stdout']='\n'.join(lines)+'\n'
   else:
    for row,line in zip(raw,lines):row['raw']=line
  for backend in ('native','wasm'):
   for index in (0,1):
    def duplicate(raw,backend=backend,index=index):
     def change(lines):lines[index]=('{"sha256":"bad",' if index==0 else '{"ok":false,')+lines[index][1:]
     mutate_lines(raw,backend,change)
    mutate_bundle(backend+'-duplicate-'+str(index),backend,duplicate)
   def order(raw,backend=backend):
    def change(lines):
     d=json.loads(lines[0]);pars=d['models'][0]['parameters'];d['models'][0]['parameters']=dict(reversed(list(pars.items())));lines[0]=json.dumps(d)
    mutate_lines(raw,backend,change)
   mutate_bundle(backend+'-descriptor-parameter-order',backend,order)
  mutate_bundle('native-forged-command-with-rebound-raw-hash','native',lambda raw:raw.update(stdin='changed'))
  mutate_bundle('wasm-forged-call-with-rebound-raw-hash','wasm',lambda raw:raw[1].update(args=['changed']*4))
  mutate_bundle('wasm-exception-row-with-otherwise-genuine-raw','wasm',lambda raw:raw[1].update(exception='synthetic trapped call but raw retained'))
  mutate_bundle('native-exception-with-genuine-completed-output','native',lambda raw:raw.update(exception='synthetic trap'))
  for backend in ('native','wasm'):
   responses=[success(c)for c in protocol['cases']];np,wp=bundle('native',responses),bundle('wasm',responses);paths=np if backend=='native'else wp
   receipt=json.loads(paths[1].read_text());receipt['error']='synthetic failed collection';write(paths[1].name,receipt)
   try:r=wrapper.assess(pp,np,wp);out={'outcome':r['outcome']}
   except Exception as exc:out={'outcome':'rejected','exception':type(exc).__name__,'message':str(exc)}
   rows.append({'name':backend+'-completed-receipt-with-error','expected_outcome':'rejected','observed':out,'matches_expected':out['outcome']=='rejected'})
  # Explicitly retained subnormal tokens in planned corpus; no platform execution attempted.
  source=json.loads((root/'docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/corpus.json').read_text());sub=[]
  for c in source['cases']:
   if any(0<abs(float(t))<sys.float_info.min for a in c['args'][1:]for t in a.split(',')):sub.append(c['id'])
 return {'version':'tagged-rate-transport-v3-independent-review','rows':rows,'all_expected_observations':all(r['matches_expected']for r in rows),'unexpected_rows':[r['name']for r in rows if not r['matches_expected']],'clay2005_subnormal_request_ids':sub,'subnormal_driver_status':'distinct v3 source uses strict ASCII decimal + finite/full-consumption strtod; actual native/Wasm subnormal behavior untested','reviewed_hashes':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['tools/research_rate_observations_v3.py','tools/research_rate_parity_v3.py','tools/collect_research_rates_wasm_v3.mjs','tests/research_rate_driver.cpp','tests/research_rate_driver_v3.cpp']},'compiled_calls':0,'loader_execution':False,'model_oracle_calls':0}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',required=True,type=Path);a.add_argument('--output',type=Path);v=a.parse_args();r=run(v.root);s=json.dumps(r,indent=2,allow_nan=False)+'\n'
 if v.output:
  if v.output.exists():raise FileExistsError(v.output)
  v.output.write_text(s)
 print(s,end='')
