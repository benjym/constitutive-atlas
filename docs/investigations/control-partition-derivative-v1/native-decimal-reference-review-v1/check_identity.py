"""Final author identity and unchanged source audit. No author mains."""
import hashlib,json,ast,sys,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
D=Path(__file__).resolve().parent;C=D.parent;A=C/'native-decimal-reference-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
ck('final exact manifest',sha(A/'manifest.json')=='0fe21547956a8db5ccd3974688e9d4633fd93b26bfcd340c0707642bffd20ba9');manifest=read(A/'manifest.json')
for n,v in manifest['files'].items():ck('author file '+n,sha(A/n)==v)
ck('complete authored inventory',{str(x.relative_to(A))for x in A.rglob('*')if x.is_file()and x.name!='manifest.json'}==set(manifest['files']))
f=read(A/'source-freeze.json');root=Path(f['directory']);ck('594 source files',len(f['files'])==594);ck('complete source inventory',{str(x.relative_to(root))for x in root.rglob('*')if x.is_file()}==set(f['files']))
for n,v in read(A/'inputs.json').items():ck('input '+n,sha(Path(n))==v)
for n,v in f['files'].items():ck('source '+n,sha(root/n)==v)
old=read(C/'native-ci-fixture-composition-v3/source-freeze.json');ck('accepted source unchanged',f['files']==old['files'])
ck('author115 syntheticchecks',read(A/'synthetic-results.json')['passed']is True and read(A/'synthetic-results.json')['checks']==115)
tests=read(A/'assessor-test-results.json');ck('author51 transportmocks',tests['passed']is True and tests['cases']==51 and all(x['expected_pass']==x['observed_pass']for x in tests['records']))
for name in ['decimal_dsl.py','generate.py','assess_saved.py']:
 code=(A/name).read_text();tree=ast.parse(code)
 ck('no production imports '+name,all(not((x.module or '').startswith('atlas'))if isinstance(x,ast.ImportFrom)else all(not y.name.startswith('atlas')for y in x.names)for x in ast.walk(tree)if isinstance(x,(ast.Import,ast.ImportFrom))))
 ck('no dynamic expression execution '+name,not any(isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id in ['eval','exec']for x in ast.walk(tree)))
 try:exec(compile(code,str(A/name),'exec',optimize=1),{'__name__':'review_optimized_guard'})
 except RuntimeError as e:ck('optimized module rejected '+name,'Unoptimized'in str(e))
 else:raise RuntimeError('optimized module accepted '+name)
sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('frozen_assessor',A/'assess_saved.py');assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
for kind,file in [('direct','process.json'),('ctest','ctest-process.json')]:
 M=A/'synthetic-transport';result=assessor.assess(A/'requests.json',A/'reference.json',M/file,M/'binding.json',sha(M/'binding.json'))
 ck('frozen synthetic '+kind,result['passed']is True and result['purpose']=='synthetic-test-only'and result['comparisons']==588 and len(result['results'])==588 and result['failures']==[])
 expected=[]
 for col in range(14):
  expected.extend(('AD/FD',col,level,row)for level in range(2)for row in range(14));expected.extend(('h/h2',col,None,row)for row in range(14))
 ck('full result coverage '+kind,[(x['gate'],x['column'],x.get('level'),x['row'])for x in result['results']]==expected and all(x['passed']is True for x in result['results']))
 ck('saved replay results exact '+kind,result==read(A/('synthetic-'+kind+'-assessment.json')))
print(json.dumps({'identity':'independent-final-decimal-reference-binding-review','author_manifest_sha256':sha(A/'manifest.json'),'checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0},indent=2))
