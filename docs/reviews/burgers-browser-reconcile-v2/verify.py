"""Verify pinned review and optional exact local package; no compiled calls."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(package=None,source=None):
    for name,digest in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(HERE/name)==digest,name
    for name,digest in json.loads((HERE/'reviewed-inputs.json').read_text())['files'].items():assert sha(ROOT/name)==digest,name
    decision=json.loads((HERE/'decision.json').read_text())
    assert decision['verdict']=='accepted-local-coexistence' and not decision['blocking_findings']
    assert not decision['live_delivery_verified']
    tests=subprocess.run(['node','--test','tests/test_timed_route.mjs','tests/test_web_package.mjs','tests/test_description_context.mjs'],cwd=ROOT,capture_output=True,text=True)
    assert tests.returncode==0,tests.stderr+tests.stdout
    contract=subprocess.run(['node','docs/reviews/burgers-browser-v1/check_contract.mjs'],cwd=ROOT,capture_output=True,text=True)
    assert contract.returncode==0,contract.stderr
    assert json.loads(contract.stdout)==json.loads((HERE/'contract-results.json').read_text())
    refresh=subprocess.run(['node',str(HERE/'check_refresh.mjs')],cwd=ROOT,capture_output=True,text=True)
    assert refresh.returncode==0,refresh.stderr
    assert json.loads(refresh.stdout)==json.loads((HERE/'refresh-results.json').read_text())
    if package is not None:
        assert source is not None,'--source required with --package'
        for name,digest in json.loads((HERE/'package-inputs.json').read_text())['files'].items():assert sha(Path(package)/name)==digest,name
        for name,digest in json.loads((HERE/'source-inputs.json').read_text())['files'].items():assert sha(Path(source)/name)==digest,name
        p=subprocess.run([sys.executable,'-B',str(HERE/'check.py'),'--source',source,'--package',package],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert json.loads(p.stdout)==json.loads((HERE/'check-results.json').read_text())
    return dict(verdict=decision['verdict'],pure_route_package_description_tests=16,pure_contract_assertions=70,burgers_selected_refresh_checks=4,package_checked=package is not None,compiled_calls=0,live_verified=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package');p.add_argument('--source');a=p.parse_args()
    print(json.dumps(run(a.package,a.source),indent=2))
