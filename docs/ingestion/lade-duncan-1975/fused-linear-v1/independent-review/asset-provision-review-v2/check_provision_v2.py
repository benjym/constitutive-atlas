"""Pure synthetic corrected provisioner tests; output only in reviewer directory."""
from pathlib import Path
import hashlib,importlib.util,io,json,sys,unittest
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
BASE=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1'
sys.path.insert(0,str(ROOT));pins={}
def pin(path,expected=None):
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    if expected:assert h==expected,str(path)
    pins[str(path.relative_to(ROOT))]=h
for name in ['SOURCE_FREEZE-v2.json','POLICY-v2.json','source-pins.json']:
    p=BASE/name;pin(p)
    for name,h in json.loads(p.read_bytes()).get('files',{}).items():pin(ROOT/name,h)
for row in json.loads((BASE/'preservation-v1.json').read_bytes())['originals']:pin(ROOT/row['saved_copy'],row['old_sha256'])
spec=importlib.util.spec_from_file_location('review_provision_tests_v2',BASE/'test_provision.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.HERE=OUT
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(module.ProvisionTests))
(OUT/'synthetic-test-log.txt').write_text(stream.getvalue());assert result.wasSuccessful()
saved=json.loads((BASE/'pure-results.json').read_bytes());assert saved['tests']==result.testsRun and saved['passed']
(OUT/'source-check-results.json').write_text(json.dumps({'passed':True,'tests':result.testsRun,'scope':'Synthetic bytes/mock approval and generic package guard; no real asset, native/Wasm/material or build calls','pins':pins},indent=2)+'\n')
print(json.dumps({'passed':True,'tests':result.testsRun,'pins':len(pins)}))
