"""Pure source/receipt rejection checks; fake bytes never represent a backend pass."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[4]
PACKET = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('refresh_source_checks', ROOT/'tools/qualify_controlled_path_refresh.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
checks = []
def check(value, label):
    assert value, label
    checks.append(label)

def rejected(action, label):
    try:
        action()
    except (ValueError, KeyError, OSError, StopIteration):
        checks.append(label)
    else:
        raise AssertionError('Expected rejection: '+label)

for name in ('tools/qualify_controlled_path_refresh.py', 'tools/build_controlled_path_web.py', 'tools/build_interface2016_web.py'):
    ast.parse((ROOT/name).read_text())
    check(True, 'AST '+name)
old = (PACKET/'preimages/tools/build_interface2016_web.py').read_text()
new = (ROOT/'tools/build_interface2016_web.py').read_text()
a = old.index("    receipt = json.loads((ROOT/BUILD_RECEIPT).read_text())")
b = old.index('    with tempfile.TemporaryDirectory()', a)
c = new.index("        receipt = json.loads((ROOT/BUILD_RECEIPT).read_text())")
d = new.index('    with tempfile.TemporaryDirectory()', c)
check(textwrap.dedent(old[a:b]) == textwrap.dedent(new[c:d]), 'Historical interface compiled guard body exact after indentation')
old_js = (PACKET/'preimages/tools/test_interface2016_package.mjs').read_text()
new_js = (ROOT/'tools/test_interface2016_package.mjs').read_text()
a = old_js.index('const pins=new Map(review.artifacts')
b = old_js.index('for(const [extension,name]', a)
check(old_js[a:b] in new_js, 'Historical interface JS guard exact')
old_nor = (PACKET/'preimages/tools/build_controlled_path_web.py').read_text()
new_nor = (ROOT/'tools/build_controlled_path_web.py').read_text()
a = old_nor.index('        qualification_path = current_receipt')
b = old_nor.index("    engine = destination/'engine-path'", a)
check(old_nor[a:b] in new_nor, 'Historical NorSand compiled branches exact')
rows = helper.commands('libatlas_path_capability.so')
builds = [r for r in rows if r['id'].endswith('-build')]
check(len(builds)==4 and all(r['argv'][-4:]==['--target','atlas_path_capability','--parallel','1'] for r in builds), 'Four serial explicit target builds')
check(max(i for i,r in enumerate(rows) if '-native-' in r['id']) < min(i for i,r in enumerate(rows) if '-wasm-' in r['id']), 'Both native groups before Wasm')
rejected(lambda: helper.relative('../outside'), 'Reject traversal')
rejected(lambda: helper.relative('/outside'), 'Reject absolute execution path')
with tempfile.TemporaryDirectory(prefix='controlled-path-refresh-pure-') as temporary:
    root = Path(temporary)
    original_root = helper.ROOT
    original_load = helper.load_plan
    helper.ROOT = root
    build = root/'engine'
    build.mkdir()
    check(helper.validate_refresh(build, helper.MODELS['norsand']) is None, 'Missing fresh receipt preserves historical dispatch')
    source = root/helper.MODEL_PATHS['norsand'][0]
    source.parent.mkdir(parents=True)
    source.write_bytes(b'fake definition for pure receipt test only')
    plan_path = root/helper.PLAN
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text('{}\n')
    library = 'libatlas_path_capability.so'
    plan = dict(source_closure={'fake-source':'fake-hash'},native_library=library,commands=helper.commands(library))
    helper.load_plan = lambda: plan
    artifacts={}
    for name in ['native/'+library,'atlas_path_capability.mjs','atlas_path_capability.wasm']:
        p=build/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('fake artifact '+name).encode());artifacts[name]=helper.sha(p)
    generated={}
    for name in helper.GENERATED:
        p=build/'generated'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(('fake generated '+name).encode());generated[name]=helper.sha(p)
    commands={}
    for row in plan['commands']:
        base=root/helper.PACKET/'execution-v1';base.mkdir(parents=True,exist_ok=True)
        p=base/(row['id']+'.log');p.write_text('pure fake command: NOT EXECUTED\n');commands[p.relative_to(root).as_posix()]=helper.sha(p)
        p=base/(row['id']+'.receipt.json');p.write_text(json.dumps(dict(returncode=0,plan_sha256=helper.sha(plan_path),repository_root=str(root),argv=[a.replace('$ROOT',str(root)) for a in row['argv']])));commands[p.relative_to(root).as_posix()]=helper.sha(p)
    req=root/(helper.NORSAND+'backend-requests-v2.json');req.parent.mkdir(parents=True,exist_ok=True);req.write_text('{}\n')
    reports=[dict(library_sha256=artifacts['native/'+library],request_sha256=helper.sha(req)),dict(module_sha256=artifacts['atlas_path_capability.mjs'],wasm_sha256=artifacts['atlas_path_capability.wasm'],request_sha256=helper.sha(req))]
    results={}
    for name,report in zip(['native.json','wasm.json'],reports):
        p=root/helper.PACKET/'execution-v1/norsand'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report));results[p.relative_to(root).as_posix()]=helper.sha(p)
    metadata={}
    for backend in ['native','wasm']:
        for name in ['CMakeCache.txt','compile_commands.json']:
            p=build/'build-metadata'/backend/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fake metadata');metadata[p.relative_to(build).as_posix()]=helper.sha(p)
    binding=dict(model=helper.MODELS['norsand'],model_sha256=helper.sha(source),plan=dict(path=helper.PLAN.as_posix(),sha256=helper.sha(plan_path)),source_closure=plan['source_closure'],artifacts=artifacts,generated=generated,native_generated=generated,commands=commands,results=results,build_metadata=metadata)
    qualification=dict(schema_version='controlled-path-refresh-1',status='passed',model=helper.MODELS['norsand'],implementation_run='pure-fake-implementer',binding=binding,gates=helper.GATES['norsand'])
    review=dict(schema_version='controlled-path-refresh-review-1',status='accepted',binding=binding,gates=helper.GATES['norsand'],reviewer_run='pure-fake-independent-reviewer',blocking_findings=[])
    pending=deepcopy(qualification);pending['status']='passed-original-backend-gates-pending-independent-review'
    (build/'qualification-pending.json').write_text(json.dumps(pending))
    review['qualification_pending_sha256']=helper.sha(build/'qualification-pending.json')
    def save(q=qualification,r=review):
        (build/'build-review.json').write_text(json.dumps(r))
        data=deepcopy(q);data['independent_review']=dict(path='build-review.json',sha256=helper.sha(build/'build-review.json'));(build/'refresh-qualification.json').write_text(json.dumps(data))
    save()
    check(helper.validate_refresh(build, helper.MODELS['norsand']) is not None, 'Complete synthetic receipt shape accepted, zero backend calls')
    bad=deepcopy(review);bad['reviewer_run']=qualification['implementation_run'];save(r=bad)
    rejected(lambda:helper.validate_refresh(build,helper.MODELS['norsand']), 'Self-review rejected despite updated pin')
    save();bad=deepcopy(qualification);bad['gates']['native_requests']=57;save(q=bad)
    rejected(lambda:helper.validate_refresh(build,helper.MODELS['norsand']), 'Changed original gate rejected')
    save();p=build/'atlas_path_capability.wasm';p.write_bytes(b'changed fake artifact')
    rejected(lambda:helper.validate_refresh(build,helper.MODELS['norsand']), 'Changed engine rejected')
    helper.ROOT=original_root;helper.load_plan=original_load
print(json.dumps(dict(status='pass-pure-source-and-rejection-checks',checks=len(checks),details=checks,compiled_calls=0),indent=2))
