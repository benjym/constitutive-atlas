"""Original saved Burgers verification plus every original installed assertion."""
from pathlib import Path
import hashlib, importlib.util, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
R=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'
def verify():
    context=json.loads((ROOT/'docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/historical-routing-v1.json').read_text())
    for name,digest in context['pins'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    sys.path.insert(0,str(R))
    spec=importlib.util.spec_from_file_location('_original_burgers_verify',R/'verify.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    result=original.verify(installed=False)
    manifest=json.loads((R/'manifest.json').read_text())
    freeze=json.loads((R/'freeze.json').read_text())
    for name,digest in manifest['installed_files'].items():
        checked_receipt(ROOT,(R/'manifest.json').relative_to(ROOT),name,digest)
    assert (ROOT/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_bytes()==(R/'model.json').read_bytes()
    assert (R/'target.cmake').read_text() in (ROOT/'CMakeLists.txt').read_text()
    for name,digest in freeze['prior_models'].items():
        checked_receipt(ROOT,(R/'freeze.json').relative_to(ROOT),name,digest)
    return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
