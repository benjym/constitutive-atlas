"""Portable independent release identity audit; never executes compiled artifacts."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked={}
def bind(p,expected=None):
    p=Path(p); value=sha(p)
    if expected is not None:assert value==expected,str(p)
    checked[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=value
    return value
occ='original-cam-clay-sw-electronic-log-recovery-v1'
model=ROOT/'models'/f'{occ}.json'
bind(model,'637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34')
from atlas.agent_review import validate_review,approval_entry
review=ROOT/'catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json'
bind(review,'a02f6524ee34d98d293453973aec3598251c34adc5ffd9b18082d19edfe0b790')
validate_review(review,ROOT,for_approval=True)
registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
record=next(r for r in registry['models'] if r['model_id']==occ)
assert record==approval_entry(review,ROOT)
# Unrelated approval records preserve semantic content despite JSON Unicode formatting.
old_registry=json.loads(subprocess.check_output(['git','show','HEAD:catalogue/approved-models.json'],cwd=ROOT))
assert [r for r in registry['models'] if r['model_id']!=occ]==old_registry['models']
fixture=json.loads((ROOT/'tests/fixtures/current-thirteen-occ-v1.json').read_text())
assert len(fixture['models'])==13
assert {ROOT/x['path'] for x in fixture['models']}==set((ROOT/'models').glob('*.json'))
for x in fixture['models']:
    bind(ROOT/x['path'],x['sha256'])
    if x['path']!=str(model.relative_to(ROOT)):
        assert subprocess.check_output(['git','show','HEAD:'+x['path']],cwd=ROOT)==(ROOT/x['path']).read_bytes()
bind(ROOT/fixture['catalogue']['path'],fixture['catalogue']['sha256'])
# Generate through the ordinary compiler; compare exact full 13-model artifacts.
from atlas.compiler import generate
from atlas.model import all_models
from tempfile import TemporaryDirectory
with TemporaryDirectory(prefix='occ-review-generation-') as temp:
    generate(Path(temp))
    eq=json.loads((HERE.parent/'release-host-fixes-v1/generated-equivalence.json').read_text())
    for name,item in eq.items():
        assert item['equal'] and item['release_sha256']==item['qualified_sha256']
        assert sha(Path(temp)/name)==item['qualified_sha256']
        bind(Path('/private/tmp/atlas-occ-integration-v1/build-native/generated')/name,item['qualified_sha256'])
        bind(Path('/private/tmp/atlas-occ-integration-v1/build-wasm/generated')/name,item['qualified_sha256'])
# Every immutable archive entry resolves to exact stored bytes; map additions keep old entries.
maps=[ROOT/'catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json',ROOT/'docs/ingestion/power-creep-itasca900/checklist-audit-v1/source-archive-map.json']
for p in maps:
    m=json.loads(p.read_text());bind(p)
    for entry in m['entries']:bind(ROOT/entry['archived_path'],entry['sha256'])
    for name,digest in m['documents'].items():bind(ROOT/name,digest)
    try:old=json.loads(subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT,stderr=subprocess.DEVNULL))
    except subprocess.CalledProcessError:continue
    assert all(e in m['entries'] for e in old['entries'])
    assert m['documents']==old['documents']
# Reassess saved negative observations without executing either test binary.
from tools.check_native_fixture_contracts import check_contract,check_observation
from types import SimpleNamespace
contract_path=ROOT/'catalogue/native-fixture-contracts-thirteen-occ-v1.json'
contract=json.loads(contract_path.read_text())
bind(contract_path,'de6794587d11d1722756afd53744032358707ad66e95f61c0557dcc17bc545c0')
policy=json.loads((ROOT/'catalogue/laboratory-package-policy.json').read_text())
assert set(policy['models'])=={json.loads((ROOT/x['path']).read_text())['id'] for x in fixture['models']}
cases=check_contract(contract,policy)
observed_path=HERE.parent/'release-host-fixes-v1/current13-native-fixtures.json'
observed=json.loads(observed_path.read_text());bind(observed_path)
assert observed['fixture_contract_sha256']==sha(contract_path) and observed['status']=='passed'
assert len(observed['processes'])==4
assert {(c['target'],c['profile']) for c in observed['processes']}==set(cases)
for c in observed['processes']:
    check_observation(cases[c['target'],c['profile']],SimpleNamespace(**c))
old_checker=HERE.parent/'release-host-fixes-v1/before/check_native_fixture_contracts.py'
assert old_checker.read_bytes()==subprocess.check_output(['git','show','HEAD:tools/check_native_fixture_contracts.py'],cwd=ROOT)
bind(old_checker)
companion_path=HERE.parent/'release-host-fixes-v1/recorded-companion-result.json'
companion=json.loads(companion_path.read_text());bind(companion_path)
assert companion['returncode']==0 and companion['stderr']==''
assert companion['stdout']=='Explicit valid-domain/GIS-depth20 fixtures; models=13\n'+json.dumps({'ok':True,'cases':83,'checks':2472},separators=(',',':'))+'\n'
bind(Path('/private/tmp/atlas-occ-integration-v1/build-native/atlas_recorded_tests'),companion['executable_sha256'])
freeze_path=ROOT/'docs/ingestion/original-cam-clay/integration-v1/prospective-freeze.json'
freeze=json.loads(freeze_path.read_text());bind(freeze_path)
equalities=[]; differences=[]
for name,digest in freeze['files'].items():
    if '/source-snapshot/' not in name:continue
    rel=name.split('/source-snapshot/',1)[1]
    if not (rel.startswith(('models/','cpp/')) or rel in ('atlas/compiler.py','atlas/dsl.py','atlas/model.py','CMakeLists.txt')):continue
    bind(ROOT/name,digest)
    current=ROOT/rel
    if current.is_file() and current.read_bytes()==(ROOT/name).read_bytes():equalities.append(rel)
    else:
        differences.append(rel)
        if current.is_file():bind(current)
assert len(equalities)==53
assert set(differences)=={'atlas/compiler.py','atlas/dsl.py','cpp/include/atlas/checked_spectral_multiplicity.hpp'}
for header in ('/private/tmp/atlas-occ-integration-v1/build-native/generated/models.hpp','/private/tmp/atlas-occ-integration-v1/build-wasm/generated/models.hpp'):
    assert not any(token in Path(header).read_text() for token in ('principal_max_repeated','principal_min_repeated','checked_spectral_multiplicity'))
(HERE/'source-equivalence.json').write_text(json.dumps({'equal':equalities,'different_from_initial_snapshot':differences,'assessment':'Only unrelated experimental repeated-principal predicates absent from release HEAD; all13 generated artifacts identical; no claim of blanket compiler identity'},indent=2)+'\n')
# No production model/engine/compiler mutation relative to isolated base.
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
assert not any(p.startswith(('atlas/','cpp/','schemas/','models/')) for p in changed)
for name in changed:
    bind(ROOT/name)
for name in ['catalogue/laboratory-control-support.json','web/laboratory-support.mjs','tests/test_laboratory_support.mjs','tests/fixtures/current-thirteen-occ-v1.json','protocols/gis2024-small-drained-thirteen-occ-v1.json','docs/models/'+occ+'.md','release-host-fixes-v1/generated-equivalence.json','tests/test_native_fixture_contracts.py','catalogue/native-fixture-contracts-thirteen-occ-v1.json','release-host-fixes-v1/NATIVE-CONTRACT-PLAN.md','release-host-fixes-v1/original-native-fixtures.json','release-host-fixes-v1/portable-ci-v1.json']:
    p=ROOT/name if not name.startswith('release-host') else HERE.parent/name
    bind(p)
out={'status':'pass','reviewer':'/root/occ_e1_e2_closeout_review','base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'model':occ,'E5_record_valid':True,'approval_exact_generated_entry':True,'existing_12_model_bytes_unchanged':True,'all_13_generated_artifacts_identical_to_qualified':True,'historical_archive_entries_preserved':True,'compiled_calls':0,'builds':0,'bindings':checked}
(HERE/'identity-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='bindings'},indent=2))
