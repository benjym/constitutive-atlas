"""Independent source-only witnesses. No original checkout, cache, or engine access."""
from pathlib import Path
import hashlib, importlib.util, json, sys, tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1] / 'rate-restoration-qualification-plan-v2'
EXPECTED = 'b2dcc31f42dc87bc1cefaa0ab952608bff74bf362f0092495dd6237bccdebe08'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
def ok(value, label):
    assert value, label
    checks.append(label)
ok(sha(PLAN/'manifest.json') == EXPECTED, 'exact author manifest')
manifest = json.loads((PLAN/'manifest.json').read_text())
for row in manifest['files']:
    path = PLAN/row['path']
    ok(path.is_file() and not path.is_symlink() and sha(path)==row['sha256'] and path.stat().st_size==row['size_bytes'], 'member '+row['path'])
for row in json.loads((PLAN/'external-pins.json').read_text()):
    path=Path(row['path'])
    ok(sha(path)==row['sha256'] and path.stat().st_size==row['bytes'], 'external '+str(path))
spec=importlib.util.spec_from_file_location('independent_C_plan', PLAN/'collector.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for name in ('source_files','source_freeze','freeze','collect','assess_pair','interface_cases'):
    fn=getattr(m.M,name)
    ok(Path(fn.__code__.co_filename)==m.OLD/'collector.py', 'original scientific implementation '+name)
witnesses=[]
with tempfile.TemporaryDirectory(prefix='source-only-', dir=HERE) as td:
    root=Path(td); m.SOURCE=root
    source=root/'fixture.txt'; source.write_text('unchanged')
    receipt=root/'receipt.json'; receipt.write_text('{}')
    review=root/'review.json'; launch=root/'launch.json'
    def make(author, reviewer):
        review.write_text(json.dumps({'accepted':True,'author_run':author,'reviewer_run':reviewer,'proposal_manifest_sha256':EXPECTED}))
        value={'identity':'control-restoration-C-reviewed-launch-binding-v2','plan_manifest_sha256':EXPECTED,'plan_review':m.pin(review),'solver_sha256':'3278b22140ca2057a9a2e415654f5213b8183f398df79a7f5c56628756e8dc99','installations':{role:{'receipt':m.pin(receipt),'review':m.pin(review),'source_pins':[m.pin(source)]} for role in ('compatibility','fixtures')}}
        launch.write_text(json.dumps(value)); return m.pin(launch)
    ok(bool(m.verify_launch(make('author','reviewer'))), 'manufactured positive launch')
    for author, reviewer in [('', 'reviewer'), ('author',''), (None,'reviewer'), ('author',None), ([], 'reviewer'), ('author',{})]:
        m.verify_launch(make(author,reviewer))
        witnesses.append({'finding':'R1','author_run':author,'reviewer_run':reviewer,'incorrectly_accepted':True})
    ok(len(witnesses)==6,'six invalid independent identities accepted by frozen plan')
    # Exercise actual main's first-phase lifecycle with only inert fixture operations.
    pin=make('author','reviewer'); m.ACTUAL=root/'actual'
    calls=[]; original=RuntimeError('manufactured source-freeze failure')
    def plan_check(_): calls.append('verify_plan')
    def source_check(_): calls.append('assert_source')
    def failed_freeze(_):
        source.write_text('manufactured changed input')
        raise original
    m.verify_plan=plan_check; m.assert_source=source_check; m.M.source_freeze=failed_freeze
    argv=sys.argv
    sys.argv=['collector.py','source-freeze','--plan-manifest-sha256',EXPECTED,'--launch-binding',pin['path'],'--node',str(root/'inert-node'),'--tool','inert=fixture']
    try:
        try: m.main()
        except RuntimeError as error: ok(error is original,'first-phase original exception preserved')
        else: raise AssertionError('expected fixture failure')
    finally: sys.argv=argv
    ok(calls==['verify_plan','assert_source'], 'source-freeze error performs no finally source/plan guard')
    ok(source.read_text()=='manufactured changed input','fixture mutation survived unobserved postguard')
    witnesses.append({'finding':'R2','calls':calls,'post_guard_calls':0,'original_exception_preserved':True})
ok(not list(HERE.glob('source-only-*')), 'owned fixtures cleaned')
report={'status':'PASS-witnesses-confirmed','checks':len(checks),'labels':checks,'findings':witnesses,'actual_compiled_or_source_operations':False}
(HERE/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'findings':['R1','R2']}))
