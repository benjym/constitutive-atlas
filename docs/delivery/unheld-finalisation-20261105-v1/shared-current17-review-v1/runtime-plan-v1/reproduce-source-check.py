"""Pure source and manufactured file-binding witnesses. No processes or model evaluation."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,tempfile
Q=Path(__file__).resolve().parent;P=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/current17-runtime-reuse-plan-v1')
OLD=P.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5'
checks=[]
def check(name,value):
 assert value,name;checks.append(name)
def reject(name,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,StopIteration):checks.append(name);return
 raise AssertionError('accepted corruption '+name)
a=ast.parse((OLD/'collector.py').read_text());b=ast.parse((P/'collector-reuse.py').read_text())
def first(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
for name in ['sha','write','csv','pin','verify','source_files','Transport','load_gate','interface_cases','collect','Replay']:
 check('unchanged AST '+name,ast.dump(first(a,name),include_attributes=False)==ast.dump(first(b,name),include_attributes=False))
old_pair=ast.unparse(first(a,'assess_pair')).replace('baseline-five-prospective-execution-freeze-v1','baseline-five-current17-reused-execution-freeze-v1')
check('pair differs only provenance identity',old_pair==ast.unparse(first(b,'assess_pair')))
for n in ['policy.json','wasm-cli.mjs']:check('exact original '+n,(P/n).read_bytes()==(OLD/n).read_bytes())
for path in P.glob('*.py'):ast.parse(path.read_text());checks.append('parse '+path.name)
spec=importlib.util.spec_from_file_location('prospective_reuse',P/'collector-reuse.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='manufactured-reuse-',dir=Q) as tmp:
 root=Path(tmp);repo=root/'source';(repo/'models').mkdir(parents=True)
 candidates=json.loads((P/'policy.json').read_text())['candidate_sha256']
 models=[]
 for model in candidates:
  payload=(P.parents[1]/'unheld-finalisation-20261102-v1/baseline-migration/proposals'/f'{model}.json').read_bytes()
  (repo/'models'/f'{model}.json').write_bytes(payload);models.append(json.loads(payload))
 models.extend({'id':'manufactured-only-'+str(i)} for i in range(12))
 blob=root/'inert-not-executable';blob.write_text('manufactured-only\n')
 generated=root/'models.json';generated.write_text(json.dumps({'models':models}))
 record=root/'raw-proof.json';record.write_text('{"manufactured":true}')
 h={'identity':'baseline-five-current17-existing-build-handoff-v1','revision':m.REVISION,'source_sha256':{'manufactured':'only'},'artifacts':{k:m.pin(blob) for k in ['native','module','wasm','node']},'build_tools':{k:m.pin(blob) for k in ['cmake','native_cxx','emcmake','emcc']},'raw_provenance':[m.pin(record)],'builds':{},'generated':{}}
 for backend in ['native','wasm']:
  h['builds'][backend]={'returncode':0,'argv':['cmake','--build','manufactured','--target','atlas_solver','--parallel','1'],'configure_returncode':0,'logs':[m.pin(record)],'compiler_version_logs':[m.pin(record)],'resolved_compiler':m.pin(blob)}
  h['generated'][backend]={'header':m.pin(blob),'json':m.pin(generated)}
 hp=root/'handoff.json';rp=root/'review.json'
 r={'decision':'accepted','author_run':'manufactured-A','reviewer_run':'manufactured-B','unresolved_blockers':[],'existing_build_provenance_accepted':True}
 m.source_map=lambda ignored:{'manufactured':'only'}
 def run(hh=None,rr=None):
  hh=copy.deepcopy(h if hh is None else hh);rr=copy.deepcopy(r if rr is None else rr)
  hp.write_text(json.dumps(hh));rr['handoff_sha256']=m.sha(hp);rp.write_text(json.dumps(rr));return m.validate_handoff(repo,m.pin(hp),m.pin(rp))
 check('manufactured complete binding accepted',run()==h)
 for name,change in [
  ('wrong revision',lambda x:x.update(revision='0'*40)),('missing source member',lambda x:x.update(source_sha256={})),('missing artifact',lambda x:x['artifacts'].pop('wasm')),('missing generated backend',lambda x:x['generated'].pop('wasm')),('nonserial build',lambda x:x['builds']['wasm']['argv'].__setitem__(-1,'2')),('wrong target',lambda x:x['builds']['native']['argv'].__setitem__(5,'other')),('build failed',lambda x:x['builds']['native'].update(returncode=1)),('configure failed',lambda x:x['builds']['wasm'].update(configure_returncode=1)),('no raw provenance',lambda x:x.update(raw_provenance=[])),('wrong artifact hash',lambda x:x['artifacts']['native'].update(sha256='0'*64))]:
  hh=copy.deepcopy(h);change(hh);reject(name,lambda hh=hh:run(hh))
 for name,change in [('self review',lambda x:x.update(reviewer_run=x['author_run'])),('missing author',lambda x:x.pop('author_run')),('review pending',lambda x:x.update(decision='pending')),('unresolved blocker',lambda x:x.update(unresolved_blockers=['x'])),('provenance not accepted',lambda x:x.update(existing_build_provenance_accepted=False))]:
  rr=copy.deepcopy(r);change(rr);reject(name,lambda rr=rr:run(rr=rr))
 generated.write_text(json.dumps({'models':models[:-1]}));reject('truncated catalogue',run)
 generated.write_text(json.dumps({'models':models}));h['generated']={k:{'header':m.pin(blob),'json':m.pin(generated)} for k in ['native','wasm']}
 altered=copy.deepcopy(models);altered[0]['schema_version']='0.1';generated.write_text(json.dumps({'models':altered}))
 h['generated']={k:{'header':m.pin(blob),'json':m.pin(generated)} for k in ['native','wasm']};reject('altered embedded candidate',run)
 # Exercise exact production per-call adapter with an inert manufactured transport.
 class FakeOriginal:
  def run(self,command,**kw):
   self.calls.append({'sequence':0});
   if kw.get('mutate'):blob.write_text(blob.read_text()+'-changed')
   if kw.get('primary'):raise KeyboardInterrupt('original-primary')
   return 'manufactured'
 env={'Transport':FakeOriginal,'verify':m.verify,'write':m.write}
 exec(compile((P/'per-call-bindings.py.txt').read_text(),'per-call-bindings.py.txt','exec'),env)
 t=env['Transport']();t.freeze={'artifacts':{'inert':m.pin(blob)},'python':m.pin(blob)};t.out=root;t.calls=[]
 check('per-call inert success',t.run([])=='manufactured')
 reject('pre-call changed hash',lambda:(blob.write_text('prechanged'),t.run([])))
 t.freeze={'artifacts':{'inert':m.pin(blob)},'python':m.pin(blob)}
 reject('post-call mutation',lambda:t.run([],mutate=True))
 t.freeze={'artifacts':{'inert':m.pin(blob)},'python':m.pin(blob)}
 try:t.run([],mutate=True,primary=True)
 except KeyboardInterrupt as e:check('primary retained with post error',str(e)=='original-primary' and len(e.artifact_post_errors)==1)
 else:raise AssertionError('primary lost')
check('manufactured scratch removed',not list(Q.glob('manufactured-reuse-*')))
(Q/'manufactured-checks.json').write_text(json.dumps({'identity':'current17-runtime-reuse-source-checks-v1','passed':True,'checks':checks,'count':len(checks),'actual_tool_or_material_calls':0},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'actual_tool_or_material_calls':0}))
