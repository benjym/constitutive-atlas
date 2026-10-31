"""Portable synthetic-only review witnesses; no compiled native/Wasm execution."""
import argparse,copy,hashlib,importlib,json,pathlib,sys

def run(repo,require_layout_fixed=False):
 sys.path.insert(0,str(repo))
 from tests.test_research_rate_collection import CollectionEvidence
 from tools import research_rate_observations as rates
 from tools import research_rate_parity as parity
 results=[]
 def witness(name,fn):
  fixture=CollectionEvidence(methodName='test_exact_literal_journal_and_assessment');fixture.setUp()
  try:detail=fn(fixture);results.append({'id':name,'passed':True,'details':detail})
  finally:fixture.doCleanups()
 def reject(fn,phrase=None):
  try:fn()
  except (ValueError,AssertionError) as exc:
   if phrase:assert phrase in str(exc),str(exc)
   return str(exc)
  raise AssertionError('Malformed evidence accepted')
 def constructor(t):
  p=t.loader();p.write_text(p.read_text().replace("return {ccall", "throw new Error('synthetic factory failure'); return {ccall"));t.build()
  result=t.collect();assert result.returncode!=0
  _,obs,raw=t.wasm_paths();o=json.loads(obs.read_text());assert o['completed'] is False
  assert json.loads(raw.read_text())==[];assert o['transport_sha256']==rates.sha(raw)
  assert 'factory failure' in o['error']
  return {'exit_nonzero':True,'rows':0,'receipt_complete':False,'retained_error':o['error']}
 witness('factory-exception-retains-empty-journal',constructor)
 def boolrate(t):
  response=copy.deepcopy(t.response);response['values'][0]=False;t.prepare(response)
  return {'rejected':reject(lambda:rates.audit(t.folder/'protocol.json',*t.wasm_paths()),'output shape')}
 witness('boolean-rate-is-not-numeric-zero',boolrate)
 def boolecho(t):
  response=copy.deepcopy(t.response);response['increment'][0]=False;t.prepare(response)
  return {'rejected':reject(lambda:rates.audit(t.folder/'protocol.json',*t.wasm_paths()),'numeric echo')}
 witness('boolean-echo-is-not-numeric-zero',boolecho)
 def backend(t):
  t.prepare();native=t.native()
  return {'rejected':reject(lambda:parity.assess(t.folder/'protocol.json',t.wasm_paths(),native),'build binding')}
 witness('explicit-backend-bundle-role',backend)
 def intfloat(t):
  t.prepare();native=t.native();r=parity.assess(t.folder/'protocol.json',native,t.wasm_paths())
  assert r['outcome']=='passed'
  return {'outcome':'passed','note':'Opaque Python-serialized int/float echoes accepted by finite numeric identity, not JSON-text digest.'}
 witness('integer-float-serialization-identity',intfloat)
 def journal_controls(t):
  t.prepare();build,obs,raw=t.wasm_paths();rows=json.loads(raw.read_text());rows[1]['args'][2]='different literal'
  raw.write_text(json.dumps(rows)+'\n');receipt=json.loads(obs.read_text());receipt['transport_sha256']=rates.sha(raw);obs.write_text(json.dumps(receipt)+'\n')
  return {'rejected':reject(lambda:rates.audit(t.folder/'protocol.json',build,obs,raw),'literal CABI controls')}
 witness('raw-controls-rebound-hash-still-rejected',journal_controls)
 def invalid_map(t):
  # Collection is a synthetic JS stub; deliberately incorrect response rejection class.
  t.protocol['cases'][0]['expectation']={'ok':False,'parser_error':True};t.protocol['cases'][0]['args'][1]='not-a-number';t.write('protocol.json',t.protocol)
  response={'ok':False,'message':'synthetic invalid','values':None};t.loader(response=response);t.build();result=t.collect();assert result.returncode==0
  return {'rejected':reject(lambda:rates.audit(t.folder/'protocol.json',*t.wasm_paths()),'parser rejection shape')}
 witness('parser-rejection-does-not-accept-domain-shape',invalid_map)
 def duplicate(t):
  t.prepare();native=t.native();doc=json.loads(native[2].read_text());lines=doc['stdout'].splitlines()
  lines[1]=lines[1].replace('"ok": true','"ok": false, "ok": true',1);assert '"ok": false, "ok": true' in lines[1]
  doc['stdout']='\n'.join(lines)+'\n';native[2].write_text(json.dumps(doc)+'\n')
  obs=json.loads(native[1].read_text());obs['transport_sha256']=rates.sha(native[2]);native[1].write_text(json.dumps(obs)+'\n')
  result=parity.assess(t.folder/'protocol.json',native,t.wasm_paths());assert result['outcome']=='passed'
  return {'accepted':True,'classification':'Inherited response-parser limitation, not newly introduced collection regression','raw_contains_conflicting_duplicate_ok':True}
 witness('inherited-duplicate-response-key-limit',duplicate)
 def reordered(t):
  t.prepare();native=t.native();doc=json.loads(native[2].read_text());lines=doc['stdout'].splitlines();descriptor=json.loads(lines[0])
  params=descriptor['models'][0]['parameters'];old=list(params);params_reversed=dict(reversed(list(params.items())))
  assert len(old)>1 and list(params_reversed)!=old
  descriptor['models'][0]['parameters']=params_reversed;lines[0]=json.dumps(descriptor);doc['stdout']='\n'.join(lines)+'\n';native[2].write_text(json.dumps(doc)+'\n')
  obs=json.loads(native[1].read_text());obs['transport_sha256']=rates.sha(native[2]);native[1].write_text(json.dumps(obs)+'\n')
  if require_layout_fixed:
   error=reject(lambda:parity.assess(t.folder/'protocol.json',native,t.wasm_paths()))
   return {'accepted':False,'rejection':error,'expected_parameter_order':old,'descriptor_parameter_order':list(params_reversed)}
  result=parity.assess(t.folder/'protocol.json',native,t.wasm_paths());assert result['outcome']=='passed'
  return {'accepted':True,'expected_parameter_order':old,'descriptor_parameter_order':list(params_reversed),'same_canonical_model_hash':rates.digest(descriptor['models'])==t.hash,'classification':'Blocking positional parameter-layout identity gap inherited by additive wrapper'}
 witness('reversed-compiled-parameter-layout-accepted',reordered)

 pins={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in ['tools/collect_research_rates_wasm.mjs','tools/research_rate_parity.py','tools/research_rate_observations.py','tests/test_research_rate_collection.py']}
 return {'kind':'synthetic-collection-review-witnesses','compiled_execution':False,'source_sha256':pins,'count':len(results),'passed':True,'witnesses':results}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=pathlib.Path);p.add_argument('--require-layout-fixed',action='store_true');a=p.parse_args();print(json.dumps(run(a.repo,a.require_layout_fixed),indent=2,allow_nan=False))
