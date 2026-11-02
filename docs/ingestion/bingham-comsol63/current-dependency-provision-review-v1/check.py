"""Source/archive reads only; never imports/runs provisioner or scientific guards."""
from pathlib import Path
import ast,hashlib,json,stat,zipfile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];P=OUT.parent/'current-dependency-provision-v1';pins={};sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();pins[str(p.relative_to(ROOT))]=sha(b);return b
def load(p):return json.loads(read(p))
for p in [P/'MANIFEST.json',P/'INPUTS-v2.json']:
 for n,h in load(p)['files'].items():assert sha(read(ROOT/n))==h
source=read(ROOT/'tools/provision_bingham_dependency_assets.py');assert sha(source)=='330f5a3c0308bf290651f7293e7de30b2e5ba947bab3c59f587e53b122b4c120';tree=ast.parse(source);constants={}
for node in tree.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:constants[node.targets[0].id]=ast.literal_eval(node.value)
  except (ValueError,TypeError):pass
packet='docs/ingestion/bingham-comsol63/current-engine-equivalence-v1/qualified-packaging-v1/';index=load(ROOT/packet/'INDEX.json');archive=ROOT/packet/'qualified-engines.zip';assert sha(read(archive))==constants['ARCHIVE_SHA256'];assert sha(read(ROOT/packet/'INDEX.json'))==constants['INDEX_SHA256']
assert set(index['files'])==set(constants['MEMBERS'])
with zipfile.ZipFile(archive) as z:
 entries=z.infolist();assert len(entries)==len(set(x.filename for x in entries))==12;assert set(x.filename for x in entries)==set(constants['MEMBERS'])
 for e in entries:
  mode=e.external_attr>>16;assert e.orig_filename==e.filename and e.create_system==3 and stat.S_ISREG(mode) and not(mode&0o7000);assert e.file_size==constants['MEMBERS'][e.filename];assert sha(z.read(e))==index['files'][e.filename]
  if e.filename.endswith('build-review.json'):
   authored=OUT.parent/'current-engine-equivalence-review-v1'/('maxwell-build-review.json' if e.filename.startswith('maxwell/') else 'norsand-build-review.json');assert z.read(e)==read(authored)
read(ROOT/'.github/workflows/verify.yml');read(ROOT/'tests/test_provision_maxwell_assets.py');checks=load(P/'CHECKS.json');assert checks['synthetic_security_tests']==13 and checks['real_provision_performed'] is False and checks['real_bundle_guards_executed'] is False
r=dict(reviewer='/root/bingham_review',source_only=True,provisioner_executed=False,material_calls=0,builds=0,manifest_and_input_pins_exact=True,fixed_archive_members_verified=12,review_bodies_exact_to_prior_authored_decisions=True,security_evidence_tests=13,actual_E5_and_real_provision_still_required=True,files=pins);(OUT/'BINDINGS.json').write_text(json.dumps(r,indent=2)+'\n');print('Verified manifest/input pins and12actual archive members, including exact previously authored reviews; no provisioner/guard/material execution.')
