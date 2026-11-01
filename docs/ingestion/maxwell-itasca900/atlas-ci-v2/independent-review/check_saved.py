"""Python/source-only restoration review; never executes generated JS or Wasm."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tarfile,tempfile
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(ROOT))
from tools.build_maxwell_laboratory import bundle,source_manifest
from atlas.evidence import checked_receipt
P=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if (Path(__file__).parent/'inputs.json').exists():
 for p,h in load(Path(__file__).parent/'inputs.json').items():assert sha(ROOT/p)==h,p
for p,h in load(P/'review-inputs-v1.json').items():assert sha(ROOT/p)==h,p
prior=load(P/'prior-source.json');assert sha(ROOT/prior['archive'])==prior['sha256']=='28510e071e5790ffbce270d79acd9a67043e9f5c51f750b621e28e0e8bcf1955'
names={'PACKET','ARCHIVE_SHA256','QUALIFICATION_SHA256','REVIEW_SHA256'}
def filter_ast(path):
 tree=ast.parse(Path(path).read_text());constants={}
 body=[]
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets):
   constants[n.targets[0].id]=ast.dump(n.value,include_attributes=False)
  else:body.append(n)
 return ast.dump(ast.Module(body=body,type_ignores=[]),include_attributes=False),constants
old,oldconstants=filter_ast(ROOT/prior['archive']);new,newconstants=filter_ast(ROOT/'tools/provision_maxwell_assets.py')
assert old==new and set(oldconstants)==set(newconstants)==names and all(oldconstants[k]!=newconstants[k] for k in names)
q=load(P/'maxwell-qualification.json');review=load(P/'independent-review/final-v1/build-review.json');prov=load(P/'provenance.json')
assert (P/'maxwell-qualification.json').read_bytes()==(ROOT/prov['origin_qualification']).read_bytes()
assert (P/'independent-review/final-v1/build-review.json').read_bytes()==(ROOT/prov['origin_review']).read_bytes()
assert review['reviewer_run']=='/root/duncan_complete_review' and review['status']=='accepted' and review['binding']==q['binding'] and review['gates']==q['gates']
assert q['independent_review']['sha256']==sha(P/'independent-review/final-v1/build-review.json')
assert q['binding']['source_manifest_sha256']==source_manifest()['sha256']==prov['source_manifest_sha256']=='af8a045962d73bef332222ae3b91139a53cd05078b9987444780635ef29bd493'
for value in review['evidence'].values():assert sha(ROOT/value['path'])==value['sha256'],value['path']
assert sha(ROOT/prov['consumer_artifact_receipt'])==prov['consumer_artifact_receipt_sha256'];consumer=load(ROOT/prov['consumer_artifact_receipt'])
for path,h in prov['durable_artifacts'].items():assert sha(ROOT/path)==h==consumer['artifacts'][path]
with tarfile.open(P/'compiled-closure-v1.tar.gz') as t:
 assert len(t.getmembers())==3 and set(t.getnames())==set(prov['archive_members'])
 for m in t.getmembers():assert m.isfile() and hashlib.sha256(t.extractfile(m).read()).hexdigest()==prov['archive_members'][m.name]
restored=Path('/private/tmp/atlas-maxwell-ci-assets-common-v2');checks=load(P/'checks-v1.json')
assert checks['restoration']['returncode']==0 and checks['focused_tests']['tests']==5
assert {p.relative_to(restored).as_posix() for p in restored.rglob('*') if p.is_file()}==set(checks['restoration']['files'])
for name,h in checks['restoration']['files'].items():assert sha(restored/name)==h
with tempfile.TemporaryDirectory(prefix='maxwell-ci-v2-pure-review-') as tmp:
 identity=bundle(Path(tmp)/'package',restored)
 assert identity['wasm_sha256']==q['binding']['wasm_sha256']
 assert (Path(tmp)/'package/engine-maxwell/build-review.json').read_bytes()==(P/'independent-review/final-v1/build-review.json').read_bytes()
r=subprocess.run(['python3','-B','-m','unittest','tests.test_provision_maxwell_assets','-v'],cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);print(r.stdout+r.stderr)
for doc in ['docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1/independent-review/inputs.json','docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1/independent-review/final-v1/inputs.json']:
 checked_receipt(ROOT,doc,'tools/provision_maxwell_assets.py',prior['sha256'])
print('PASS: sole four constant changes; exact old helper preserved and own earlier receipt bindings resolve.')
print('PASS: exact accepted common-scalar qualification/review/durable assets, selective three-member archive and five restored files.')
print('PASS: current149-path af8a... manifest and real unchanged guard accept exact restored engine via Python-only generation. No compiled calls/builds.')

preservation=load(P/'preservation-v2.json');assert sha(ROOT/preservation['helper_archive'])==prior['sha256']
for row in preservation['changed_sidecars']:
 archive=ROOT/'catalogue/source-snapshots'/row['before_sha256']/row['sidecar']
 assert sha(archive)==row['before_sha256'] and sha(ROOT/row['sidecar'])==row['after_sha256']
 oldmap=load(archive);newmap=load(ROOT/row['sidecar'])
 assert all(newmap['documents'].get(k)==v for k,v in oldmap['documents'].items())
 assert all(item in newmap['entries'] for item in oldmap['entries'])
 for document in row['documents']:assert sha(ROOT/document)==newmap['documents'][document]
for document in preservation['checked_receipt_passes']:
 checked_receipt(ROOT,document,'tools/provision_maxwell_assets.py',prior['sha256'])
doc='docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1/independent-review/final-v1/inputs.json'
for path,h in load(ROOT/doc).items():checked_receipt(ROOT,doc,path,h)
print('PASS: five prior sidecar archives preserve every old document/entry; seven helper receipt bindings plus all46 earlier final inputs resolve.')
