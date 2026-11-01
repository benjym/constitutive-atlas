import hashlib,importlib.util,json,pathlib,tempfile
r=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');here=r/'docs/admission/production-readiness-v1';s=importlib.util.spec_from_file_location('admission',here/'check.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);w=m.read_json(here/'work-packages.json');d=m.read_json(here/'decisions-template.json');changes=[]
with tempfile.TemporaryDirectory(prefix='mcc-review-exact-') as td:
 root=pathlib.Path(td)
 for n,h in w['inputs'].items():
  src=r/n
  if hashlib.sha256(src.read_bytes()).hexdigest()!=h:src=r/'catalogue/source-snapshots'/h/n;changes.append({'path':n,'sha256':h,'source':str(src.relative_to(r))})
  assert hashlib.sha256(src.read_bytes()).hexdigest()==h;dest=root/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes())
 result=m.assess(root,w,d)
print(json.dumps({'exact_archived_replacements':changes,'result':result,'compiled_calls':0},indent=2))
