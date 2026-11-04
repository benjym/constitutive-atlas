from pathlib import Path
import hashlib,json,copy,tempfile,importlib.util
O=Path(__file__).resolve().parent;A=O.parents[1]/'rate-restoration-browser-plan-v1';checks=[]
def ok(v,label):
 assert v,label
 checks.append(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ok(sha(A/'manifest.json')=='635c328e530bf7638945f4404ebc0c2d11fd78dd95e2ca61c2b03da497a2b82d','exact dispatched frozen source')
m=json.loads((A/'manifest.json').read_text())
for name,row in m['files'].items():
 p=A/name;ok(p.is_file()and not p.is_symlink()and sha(p)==row['sha256']and p.stat().st_size==row['size_bytes'],'frozen member '+name)
p=json.loads((A/'plan.json').read_text());g=json.loads((A/'GATES.json').read_text())
ok(m['author_run']!='/root/publication_operations_review','distinct author')
ok(p['ready_for_actual'] is False and 'PENDING'in p['source_revision']and'PENDING'in p['runtime_regression_binding']and'PENDING'in p['actual_origin_package_API_binding'],'future exact provenance remains pending')
ok(p['named_count']==9 and p['model_count']==17,'strict9 and17 membership')
ok('0292c075'not in json.dumps(p)+json.dumps(g),'no candidateB hardcoded authorization')
ok(p['execution_order'][-3:]==['measurement-precondition.js','compression-live-v1.js','cycles-current17.js'],'measurement precondition then unchanged compression then cycles')
spec=importlib.util.spec_from_file_location('review_install',A/'install.py');i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i)
with tempfile.TemporaryDirectory(dir=O,prefix='fixture-')as d:
 t=Path(d);base=copy.deepcopy(p)
 def relocate(plan,root):
  plan['output_directory']=str(root)
  for r in plan['scripts']+plan['input_fixtures']:r['install_path']=str(root/Path(r['install_path']).name)
 relocate(base,t/'new');root,rows=i.validate(base);ok(len(rows)==11 and not root.exists(),'validator never installs11 payloads')
 cases=[]
 occupied=t/'occupied';occupied.mkdir();x=copy.deepcopy(base);relocate(x,occupied);cases.append(('existing output',x))
 link=t/'link';link.symlink_to(t,target_is_directory=True);x=copy.deepcopy(base);relocate(x,link/'new');cases.append(('symlink output ancestry',x))
 src=t/'source.js';src.symlink_to(Path(base['scripts'][0]['path']));x=copy.deepcopy(base);x['scripts'][0]['path']=str(src);cases.append(('symlink source',x))
 x=copy.deepcopy(base);x['scripts'][0]['sha256']='0'*64;cases.append(('script drift',x))
 x=copy.deepcopy(base);x['input_fixtures'][0]['install_path']=x['scripts'][0]['install_path'];cases.append(('fixture collision',x))
 x=copy.deepcopy(base);x['execution_order']+=x['execution_order'][:1];cases.append(('duplicate order',x))
 for name,bad in cases:
  try:i.validate(bad)
  except ValueError:ok(True,'reject '+name)
  else:raise AssertionError(name)
 ok(not (t/'new').exists(),'negative fixtures made no install directory')
script=(A/'scripts/measurement-precondition.js').read_text()
for text in ["#reset",'export-run','hypoplastic-sand-igs97','Experimental test','experiment-select','30000','measurement precondition failed']:
 ok(text in script,'new setup has explicit gate '+text)
for text in ['.download(','.fill(',"selectOption(",'evaluate(async','atlas.wasm']:
 ok(text not in script,'setup cannot replace results/settings '+text)
ok(json.loads((O/'check.stdout.json').read_text())['checks']==94,'replayed complete author94 including original579 and6negatives')
(O/'independent-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'actual_browser_build_material_network':False,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks)}))
