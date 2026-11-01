"""Portable review integrity/reproduction, never builds/calls compiled software."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(path):
    p = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT,
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, (str(path), p.stdout, p.stderr)
    return p.stdout

def verify(private=False):
    manifest=json.loads((HERE/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert digest(HERE/name)==expected, ('review file changed',name)
    inventory=json.loads((HERE/'reviewed-inputs.json').read_text())
    context_drift=[]
    for item in inventory['files']:
        matches=(ROOT/item['path']).exists() and digest(ROOT/item['path'])==item['sha256']
        if item['required_current_match']:
            assert matches, ('scientific input changed',item['path'])
        elif not matches:
            context_drift.append(item['path'])
    checked_private=0
    if private:
        for item in inventory['private_sources']:
            assert digest(Path(item['private_path']))==item['sha256'], item['id']
            checked_private+=1
    evidence=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'
    for archive,index in [('frozen-source.tar.gz','source-files.json'),
                          ('execution-logs.tar.gz','execution-log-files.json')]:
        expected=json.loads((evidence/index).read_text())
        with tarfile.open(evidence/archive) as t:
            entries={m.name:m for m in t if m.isfile()}
            assert set(entries)==set(expected)
            for name, wanted in expected.items():
                assert hashlib.sha256(t.extractfile(entries[name]).read()).hexdigest()==wanted,name
    original=ROOT/'docs/ingestion/burgers-itasca900'
    independent=json.loads(run(HERE/'independent_check.py'))
    assert independent==json.loads((HERE/'independent-results.json').read_text())
    replay=json.loads(run(evidence/'verify.py'))
    assert replay==json.loads((HERE/'integration-replay.json').read_text())
    assert run(original/'verify.py')==(HERE/'ingestion-replay.json').read_text()
    return dict(identity='REV-burgers-scientific-v1',ok=True,
                independent_reference_scalars=independent['references']['scalars'],
                exact_rational_cases=independent['exact']['exact_cartesian_energy_sign_stability_cases'],
                saved_native_calls=replay['native']['calls'],saved_wasm_calls=replay['wasm']['calls'],
                private_source_hashes_checked=checked_private,context_only_drift=context_drift,
                compiled_calls=0,admission_changed=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--private-sources',action='store_true')
    print(json.dumps(verify(parser.parse_args().private_sources),indent=2))
