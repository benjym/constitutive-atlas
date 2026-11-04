"""Run only synthetic Python tests and existing+new pure Node checks."""
from pathlib import Path
import importlib.util, json, os, subprocess, sys, tempfile, unittest
HERE=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
sys.dont_write_bytecode=True
sys.path[:0]=[str(SOURCE),str(SOURCE/'tests')]
import tools.build_experiments
original_builder=tools.build_experiments
spec=importlib.util.spec_from_file_location('tools.build_experiments',HERE/'proposed/tools/build_experiments.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
spec=importlib.util.spec_from_file_location('candidate_test_web_experiments',HERE/'proposed/tests/test_web_experiments.py')
tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
if not result.wasSuccessful():raise SystemExit(1)
# Direct original-versus-candidate synthetic output comparison freezes byte identity,
# all non-transport metadata, row data and rights independently of new manifest hashes.
case=tests.BrowserBundleTests();case.setUp()
try:
    case.grant()
    old=original_builder.bundle(case.root/'old',root=case.root)
    new=module.bundle(case.root/'new',root=case.root)
    import gzip
    for before,after in zip(old['experiments'],new['experiments'],strict=True):
        assert before=={k:v for k,v in after.items() if k not in ('content_encoding','transport')}
        assert (case.root/'old'/before['path']).read_bytes()==gzip.decompress((case.root/'new'/after['transport']['path']).read_bytes())
    assert {x.name for x in (case.root/'new').iterdir()}=={'index.json',*[e['transport']['path'] for e in new['experiments']]}
finally:case.doCleanups()
# Only two existing test dependencies, no generated assets or runtime modules.
with tempfile.TemporaryDirectory(prefix='pure-fixture-',dir=HERE) as name:
    fixture=Path(name)
    for relative in ['tools/test_experiments.mjs','web/experiments.mjs','models/linear-elastic.json']:
        target=fixture/relative;target.parent.mkdir(parents=True,exist_ok=True)
        candidate=HERE/'proposed'/relative
        target.write_bytes((candidate if candidate.exists() else SOURCE/relative).read_bytes())
    completed=subprocess.run(['node',str(fixture/'tools/test_experiments.mjs')],capture_output=True,text=True,check=False)
    print(completed.stdout,end='');print(completed.stderr,end='',file=sys.stderr)
    if completed.returncode:raise SystemExit(completed.returncode)
print(json.dumps({'status':'passed','python_synthetic_tests':result.testsRun,'node':'all existing plus gzip synthetic checks','actual_corpus':False}))
