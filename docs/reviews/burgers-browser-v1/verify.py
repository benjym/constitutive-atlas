"""Verify exact delivery-review bindings and pure contracts; no compiled calls."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(package=None,source=None):
    for name,digest in json.loads((HERE/'manifest.json').read_text())['files'].items():
        assert sha(HERE/name)==digest,name
    inputs=json.loads((HERE/'reviewed-inputs.json').read_text())
    for row in inputs['files']:
        assert sha(ROOT/row['path'])==row['sha256'],row['path']
    decision=json.loads((HERE/'decision.json').read_text())
    assert decision['verdict']=='accepted-local-interface' and not decision['blocking_findings']
    assert not decision['live_delivery_verified']
    p=subprocess.run(['node',str(HERE/'check_contract.mjs')],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)==json.loads((HERE/'contract-results.json').read_text())
    if package is not None:
        assert source is not None,'--source is required with --package'
        p=subprocess.run([sys.executable,'-B',str(HERE/'check_saved.py'),package,'--source',source],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert json.loads(p.stdout)==json.loads((HERE/'saved-results.json').read_text())
        for name,digest in json.loads((HERE/'package-inputs.json').read_text())['files'].items():
            assert sha(Path(package)/name)==digest,name
    return dict(verdict=decision['verdict'],input_files=len(inputs['files']),
                pure_contract_assertions=json.loads((HERE/'contract-results.json').read_text())['pure_contract_assertions'],
                package_bytes_rechecked=package is not None,compiled_calls=0,live_delivery_verified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package');p.add_argument('--source');a=p.parse_args()
    print(json.dumps(run(a.package,a.source),indent=2))
