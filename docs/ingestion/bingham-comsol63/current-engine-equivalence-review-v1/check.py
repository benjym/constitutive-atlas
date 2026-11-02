"""Saved-only equivalence review; Python source generation, no compiled execution."""
from pathlib import Path
import hashlib,json,tarfile,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];P=OUT.parent/'current-engine-equivalence-v1';sys.path.insert(0,str(ROOT));from atlas.compiler import generate
sha=lambda b:hashlib.sha256(b).hexdigest();pin={}
def read(p):
 p=Path(p);b=p.read_bytes();pin[str(p.relative_to(ROOT))]=sha(b);return b
def load(p):return json.loads(read(p))
manifest=load(P/'MANIFEST.json');assert all(sha(read(ROOT/n))==h for n,h in manifest['files'].items())
old=load(P/'maxwell-prior-source.json');cur=load(P/'maxwell-current-source.json');assert set(old['files'])==set(cur['files']);changes={n for n in old['files'] if old['files'][n]!=cur['files'][n]};assert changes=={'atlas/measurement_units.py'}
for n,h in cur['files'].items():assert sha(read(ROOT/n))==h
for obj in [old,cur]:assert obj['sha256']==sha(json.dumps(obj['files'],sort_keys=True,separators=(',',':')).encode())
M=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/maxwell-rebind-v1';q=load(M/'maxwell-qualification.json');review=load(M/'independent-review/build-review.json');assert sha(read(M/'independent-review/build-review.json'))==q['independent_review']['sha256'];assert q['binding']==review['binding'] and q['gates']==review['gates'];assert review['status']=='accepted' and q['status']=='passed' and review['reviewer_run']!=q['implementation_run'];assert q['binding']['source_manifest_sha256']==old['sha256']
archive=read(M/'compiled-closure-v1.tar.gz');assert sha(archive)=='2ae27721254cabed74b289c9692d0286fda71bd9eab92933d736d74904f4c9dd'
with tarfile.open(M/'compiled-closure-v1.tar.gz') as t:
 for name,key in [('wasm/maxwell.js','module_sha256'),('wasm/maxwell.wasm','wasm_sha256'),('wasm/generated/models.json','catalogue_file_sha256')]:assert sha(t.extractfile(name).read())==q['binding'][key]
assert sha(read(ROOT/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'))==q['binding']['model_sha256'];assert sha(read(ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json'))==q['binding']['reference_policy_sha256']
generate(OUT/'generated-maxwell',[ROOT/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'])
for n in ['models.hpp','models.json']:
 assert read(OUT/'generated-maxwell'/n)==read(P/'generated-maxwell'/n);assert read(OUT/'generated-maxwell'/n)==read(M/'independent-review/generated'/n)
N=ROOT/'docs/ingestion/duncan-chang-1970/release-v1/qualified-norsand';nq=load(N/'controlled-path-qualification.json');nr=load(N/'build-review.json');assert sha(read(N/'build-review.json'))==nq['independent_review']['sha256'];assert nq['binding']==nr['binding'] and nq['gates']==nr['gates'];assert nr['status']=='accepted' and nq['status']=='passed' and nr['reviewer_run']!=nq['implementation_run'];ns=load(P/'norsand-prior-source.json');assert ns==nq['binding']['sources'];assert {n for n,h in ns.items() if sha(read(ROOT/n))!=h}==changes
for n,h in nq['binding']['artifacts'].items():assert sha(read(N/n))==h
models=[ROOT/'models/research/norsand/norsand-jefferies-1993-active-axial.json',ROOT/'tests/fixtures/controlled-path/synthetic-curved.json',ROOT/'tests/fixtures/controlled-path/synthetic-model.json'];generate(OUT/'generated-norsand',models)
for n,h in nq['binding']['generated'].items():assert sha(read(OUT/'generated-norsand'/n))==h;assert read(OUT/'generated-norsand'/n)==read(N/'generated'/n)==read(P/'generated-norsand'/n)
for name in ['atlas/compiler.py','atlas/model.py','atlas/path_compiler.py','tools/generate_controlled_path.py','cmake/maxwell/CMakeLists.txt','cmake/controlled-path/CMakeLists.txt','tools/build_maxwell_laboratory.py','tools/build_controlled_path_web.py','tools/provision_maxwell_assets.py','docs/reviews/common-scalar-functions-v1/dependent-independent-review/FINAL_REVIEW_V1.md',str((M/'independent-review/REVIEW.md').relative_to(ROOT))]:read(ROOT/name)
result=dict(compiled_execution=False,builds=0,maxwell_source_entries=len(old['files']),norsand_source_entries=len(ns),only_changed_source=sorted(changes),all_actual_artifact_and_review_bindings_pass=True,normal_generation_exact=True,maxwell_old_binding=q['binding'],norsand_artifacts=nq['binding']['artifacts'],original_qualification_and_review_files={str(p.relative_to(ROOT)):sha(read(p)) for p in [M/'maxwell-qualification.json',M/'independent-review/build-review.json',N/'controlled-path-qualification.json',N/'build-review.json']})
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'BINDINGS.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',files=pin),indent=2)+'\n');print(json.dumps(result,indent=2))
