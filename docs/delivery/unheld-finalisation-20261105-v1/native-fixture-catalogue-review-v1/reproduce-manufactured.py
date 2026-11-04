from pathlib import Path
import json,hashlib,importlib.util,math,ast,itertools,sys,tempfile,types,os
P=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/native-fixture-catalogue-fix-v1');OWN=Path(__file__).resolve().parent;checks=[]
def ck(n,b=True):assert b,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except AssertionError:ck(n)
 else:raise AssertionError('Accepted '+n)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=(P/'original/tools/check_native_fixture_contracts.py').read_text();new=(P/'proposed/tools/check_native_fixture_contracts.py').read_text();patch=json.loads((P/'patch-proof.json').read_text());ck('Exact reverse byte proof',new.replace(patch['addition'],'').replace(patch['new_expression'],patch['old_expression'])==old)
prior=load('original_native',P/'original/tools/check_native_fixture_contracts.py');candidate=load('candidate_native',P/'proposed/tools/check_native_fixture_contracts.py')
def func(s,n):return next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef)and x.name==n)
ck('Entire main lifecycle/assertions unchanged',ast.dump(func(old,'main'))==ast.dump(func(new,'main')))
ck('All original assertion expressions retained except catalogue expansion',ast.dump(func(old,'check_recorded_failure'))==ast.dump(func(new.replace(patch['new_expression'],patch['old_expression']),'check_recorded_failure')))
ck('Historical mapping exact',prior.PRIOR_THIRTEEN==candidate.PRIOR_THIRTEEN)
map=json.loads((P/'definition-map.json').read_text());ck('Only exact frozen five admitted',candidate.BASELINE_FIVE_V03==map['five_v03'])
for mid,digest in map['current16'].items():ck('Source definition '+mid,hashlib.sha256((P/f'evidence/models/{mid}.json').read_bytes()).hexdigest()==digest)
root=P/'evidence';model=json.loads((root/f'models/{candidate.OCC}.json').read_text());params={k:v['default']for k,v in model['parameters'].items()};axial=1e-4;volume=model['state'][1]['initial']/(1+axial);pressure=params['pref']*math.exp((params['Gamma']+params['lambda_c']-params['kappa']-volume)/params['lambda_c']);residual=abs(pressure-100000)/100000
message=f'failed knot 1 residual {residual!r} trials 1 de0 {axial!r} de1 0\ndrained replay failed: {candidate.OCC} singular mixed-control system; last committed knot retained\n'
current=map['current16'];legacy={**candidate.PRIOR_THIRTEEN,candidate.DUNCAN:candidate.DUNCAN_HASH,candidate.RAMBERG:candidate.RAMBERG_HASH,candidate.SCLAY:candidate.SCLAY_HASH}
ck('Current16 exact algebraic failure admitted',candidate.check_recorded_failure(message,current,root=root).startswith('current-sixteen'))
reject('Original source rejects current16 actual gap',lambda:prior.check_recorded_failure(message,current,root=root))
for count,defs in [(13,candidate.PRIOR_THIRTEEN),(14,{**candidate.PRIOR_THIRTEEN,candidate.DUNCAN:candidate.DUNCAN_HASH}),(15,{**candidate.PRIOR_THIRTEEN,candidate.DUNCAN:candidate.DUNCAN_HASH,candidate.RAMBERG:candidate.RAMBERG_HASH}),(16,legacy)]:ck('Historical'+str(count)+' preserved',candidate.check_recorded_failure(message,defs,root=root)==prior.check_recorded_failure(message,defs,root=root))
ck('Historical12 GIS branch preserved',candidate.check_recorded_failure(candidate.GIS_FAILURE,{k:v for k,v in candidate.PRIOR_THIRTEEN.items()if k!=candidate.OCC},root=root)==prior.check_recorded_failure(candidate.GIS_FAILURE,{k:v for k,v in candidate.PRIOR_THIRTEEN.items()if k!=candidate.OCC},root=root))
ids=list(candidate.BASELINE_FIVE_V03)
for flags in itertools.product([False,True],repeat=5):
 definitions=dict(legacy)
 for mid,use in zip(ids,flags):
  if use:definitions[mid]=current[mid]
 if all(flags)or not any(flags):ck('Complete old/current map accepted '+str(flags),bool(candidate.check_recorded_failure(message,definitions,root=root)))
 else:reject('Mixed map rejected '+str(flags),lambda definitions=definitions:candidate.check_recorded_failure(message,definitions,root=root))
for label,defs in [('extra',{**current,'unknown':'a'*64}),('missing',{k:v for k,v in current.items()if k!='linear-elastic'}),('wronghash',{**current,'linear-elastic':'a'*64})]:reject('Catalogue '+label,lambda defs=defs:candidate.check_recorded_failure(message,defs,root=root))
for label,bad in [('residual',message.replace(repr(residual),repr(residual+1e-6))),('axial',message.replace('de0 0.0001','de0 0.0002')),('trials',message.replace('trials 1','trials 2')),('signature',message.replace('singular mixed-control system','different failure')),('nan',message.replace(repr(residual),'nan'))]:reject('OCC '+label+' original gate',lambda bad=bad:candidate.check_recorded_failure(bad,current,root=root))
# Actual unchanged main with four manufactured subprocess results; no executable is launched.
with tempfile.TemporaryDirectory(prefix='owned-main-',dir=OWN)as tmp:
 output=Path(tmp)/'report.json';savedargv=sys.argv;candidate.ROOT=root;candidate.check_recorded_failure.__kwdefaults__['root']=root;calls=[]
 def fake_run(argv,**kwargs):
  target=Path(argv[0]).name;profile=kwargs['env'].get('ATLAS_NATIVE_FIXTURES');calls.append((target,profile));stderr='unknown native fixture profile\n'if profile else message if target=='atlas_recorded_tests'else'FD test outside domain\n';return types.SimpleNamespace(returncode=1,stdout=''if profile else'Strict original default fixtures; models=16\n',stderr=stderr)
 candidate.subprocess.run=fake_run;sys.argv=['candidate','--output',str(output)]
 try:candidate.main()
 finally:sys.argv=savedargv
 report=json.loads(output.read_text());ck('Unchanged four main paths',calls==[('atlas_numerical_tests',None),('atlas_numerical_tests','unknown'),('atlas_recorded_tests',None),('atlas_recorded_tests','unknown')]);ck('Manufactured main exact gates passed',report['status']=='passed'and len(report['processes'])==4)
ck('Own fixture removed',not output.parent.exists())
print(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','count':len(checks),'checks':checks,'compiled_browser_network_or_material_calls':0,'manufactured_subprocess_results':4,'temporary_resources_remaining':0},indent=2))
