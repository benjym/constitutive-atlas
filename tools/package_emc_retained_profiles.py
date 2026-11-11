"""Run unchanged retained-profile guards on their exact independently reviewed source."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from atlas.compiler import generate
from atlas.controlled_time_compiler import generate as generate_controlled_time

ROOT = Path(__file__).resolve().parents[1]
BASE = '7c9954254fe89fe7fcd45d1a64549f8e837c99c4'
PACKET = ROOT/'docs/ingestion/extended-mohr-coulomb-2013/release-norsand-v1'
SOURCE_PROOF = 'ba01a2bcb62f48beea197954a80ba62f2967a588c33bdadf8613b8198a79c4df'
PROFILES = {
    'interface2016': ('web/engines/current17-baseline-compatible/interface2016',
                      'tools/build_interface2016_baseline_web.py',
                      ('path-engine.mjs', 'path-worker.mjs', 'interface2016-laboratory.mjs')),
    'maxwell': ('web/engines/current17-compatible/maxwell', 'tools/build_maxwell_laboratory.py',
                ('maxwell-atlas-contract.mjs', 'maxwell-atlas-engine.mjs', 'maxwell-atlas-runner.mjs',
                 'maxwell-atlas-worker.mjs', 'maxwell-laboratory.mjs', 'laboratory-controller-router.mjs')),
    'controlled_time': ('web/engines/controlled-time', 'tools/build_controlled_time_web.py',
                        ('controlled-time-engine.mjs', 'controlled-time-worker.mjs', 'controlled-time-laboratory.mjs')),
}
INTERFACE_RESTORE = 'docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/restore_interface_request.py'
INTERFACE_WITNESS = '.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json'
DELTA = {'atlas/compiler.py', 'atlas/model.py', 'schemas/model-v0.3.schema.json'}
# HvWE's historical closure includes this test driver. The new test asserts
# that only the separate certified engine may run a definition with postsolve checks.
FORMULATION_TEST = 'tests/test_formulation.py'
TEST_DELTA = {'predecessor_sha256':'e87904ecfbc1f694878b037bbacaf324b7e2ba9636e30c809c53f3e2c9e12c31',
              'current_sha256':'feb5e997a43d25d4014fe0248db317796a08dcacbe47ed503f7caa564f84e98f'}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError('Retained profile source equivalence: '+message)


def regular(root, name):
    path = root/name
    require(path.resolve() == path and path.is_file() and path.is_relative_to(root), 'unsafe file '+str(name))
    return path


def git(*args, capture=False):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def namespace(root):
    include = ('atlas', 'schemas', 'cpp', 'cmake', 'models', 'tests/fixtures',
               'initialization', 'catalogue/path-examples')
    return {p.relative_to(root).as_posix() for d in include for p in (root/d).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('.')
            and not p.is_relative_to(root/'models/research/certified-return')}


def check_source(base, proof, key):
    directory, builder, components = PROFILES[key]
    row = proof['profiles'][key]
    entries = namespace(base)
    require(entries == namespace(ROOT), 'compiled source namespace changed')
    source = set(entries) | {builder, *('web/'+name for name in components)}
    if key == 'interface2016':
        closure = json.loads(regular(base,directory+'/source-compatibility.json').read_text())['source_files']
    elif key == 'maxwell':
        closure = json.loads(regular(base,directory+'/source-compatibility.json').read_text())['source_files']
    else:
        closure = [p['path'] for p in json.loads(regular(base,directory+'/public-qualification.json').read_text())['source_files']]
    source.update(closure)
    source.update(row['definitions'])
    source.update(row['retained_artifacts_and_receipts_exact_to_base'])
    source.update(row['generated_exact'])
    before = {name:digest(regular(base,name)) for name in sorted(source)}
    after = {name:digest(regular(ROOT,name)) for name in sorted(source)}
    approved_delta = dict(proof['source_delta'])
    require(set(approved_delta)==DELTA, 'unexpected scientific source proof inventory')
    if key=='interface2016':
        approved_delta[FORMULATION_TEST] = TEST_DELTA
    require({name for name in before if before[name]!=after[name]} == set(approved_delta), 'unreviewed source delta')
    for name, binding in approved_delta.items():
        require(binding == {'current_sha256':after[name], 'predecessor_sha256':before[name]},
                'changed reviewed delta '+name)
    for field in ('definitions','retained_artifacts_and_receipts_exact_to_base','generated_exact'):
        require(all(after[name]==h for name,h in row[field].items()), 'changed '+field)
    old_registry=json.loads(regular(base,'catalogue/approved-models.json').read_text())['models']
    new_registry=json.loads(regular(ROOT,'catalogue/approved-models.json').read_text())['models']
    require([r for r in new_registry if r['model_id']!='extended-mohr-coulomb-2013-exact-generalized-work-be-exact-domain-v3']==old_registry,
            'existing approvals differ')
    return after


def regenerate(proof, key):
    row = proof['profiles'][key]
    compiler = generate_controlled_time if key=='controlled_time' else generate
    with TemporaryDirectory(prefix='emc-generated-') as tmp:
        compiler(tmp,[ROOT/name for name in row['definitions']])
        expected = {Path(name).name:h for name,h in row['generated_exact'].items()}
        require({p.name:digest(p) for p in Path(tmp).iterdir() if p.is_file()} == expected,
                'generated bytes changed for '+key)


@contextmanager
def retained_profiles():
    proof_path = PACKET/'independent-source-review.json'
    require(digest(proof_path)==SOURCE_PROOF, 'independent source proof changed')
    proof = json.loads(proof_path.read_text())
    require(proof['source_commit']==BASE and proof['decision']=='accepted' and
            proof['reviewer_run']!=proof['author_run'] and not proof['blocking_findings'], 'independent proof is incomplete')
    decision = json.loads((PACKET/'retained-packaging-review.json').read_text())
    reviewer = decision.get('reviewer_run')
    require(decision['status']=='accepted' and isinstance(reviewer,str) and reviewer.strip() and reviewer!='/root' and
            decision['source_proof_sha256']==SOURCE_PROOF and not decision['blocking_findings'] and
            decision['implementation']=={name:digest(ROOT/name) for name in
                ('tools/package_emc_retained_profiles.py','tools/build_web.py','.github/workflows/pages.yml')},
            'exact bridge implementation requires independent approval')
    with TemporaryDirectory(prefix='emc-retained-release-') as tmp:
        base = Path(tmp).resolve()/'source'
        git('worktree','add','--quiet','--detach',str(base),BASE)
        try:
            require(git('-C',str(base),'rev-parse','HEAD',capture=True).strip()==BASE, 'incorrect release predecessor')
            def bundle(key, destination, artifacts):
                directory, builder, _ = PROFILES[key]
                require(artifacts.resolve()==ROOT/directory, 'only the exact reviewed engine may use this route')
                before = check_source(base, proof, key)
                regenerate(proof, key)
                witness = base/INTERFACE_WITNESS
                restored = key=='interface2016' and not witness.exists()
                try:
                    if restored:
                        subprocess.run(['python3','-B',str(base/INTERFACE_RESTORE)], cwd=base, check=True)
                    subprocess.run(['python3','-B',str(base/builder),str(destination.resolve()),str(base/directory)],
                                   cwd=base,check=True)
                finally:
                    if restored:
                        witness.unlink(missing_ok=True)
                require(check_source(base, proof, key)==before, 'source changed during packaging')
                regenerate(proof, key)
            yield bundle
        finally:
            git('worktree','remove',str(base))
