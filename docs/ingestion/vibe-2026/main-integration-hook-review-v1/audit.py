"""Independent source-only audit. No real bundler or compiled invocation."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PACKET = ROOT/'docs/ingestion/vibe-2026/main-integration-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
freeze = PACKET/'hook-source-manifest-v1.json'
assert sha(freeze) == '7dfd505062faf02bf89481a70cffe21414bb1d696824fe2c1382a6d740953b13'
manifest = json.loads(freeze.read_text())
for row in manifest['files']:
    p = ROOT/row['path']
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['path']

# Reconstruct each changed live file independently from the retained beforebytes.
norsand = 'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine'
interface = 'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine'
maxwell = 'docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine'
flags = f'--controlled-path-wasm-dir {norsand} --interface2016-wasm-dir {interface} --maxwell-wasm-dir {maxwell}'
before = PACKET/'hook-preimages'
expected = (before/'tools/build_web.py').read_text()
expected = expected.replace('controlled-path-refresh-v1/execution-v1/norsand/engine', 'controlled-path-refresh-v1/execution-v2/norsand/engine')
expected = expected.replace('controlled-path-refresh-v1/execution-v1/interface2016/engine', 'controlled-path-refresh-v1/execution-v2/interface2016/engine')
expected = expected.replace("ROOT/'build-maxwell-wasm'", "ROOT/'"+maxwell+"'")
assert expected == (ROOT/'tools/build_web.py').read_text()
artifact = '''    - name: Retain current dependency guards and Maxwell regression
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: current-dependency-guards-${{ runner.os }}
        path: |-
          ${{ runner.temp }}/current-dependency-guards/
          ${{ runner.temp }}/maxwell-ci-regression/
'''
for name, count in [('qualification', 2), ('pages', 1)]:
    p = '.github/workflows/'+name+'.yml'
    expected = (before/p).read_text()
    assert expected.count('tools/provision_bingham_dependency_assets.py') == count
    expected = expected.replace('tools/provision_bingham_dependency_assets.py', 'tools/check_current_dependency_assets.py --output "$RUNNER_TEMP/current-dependency-guards"')
    old = '--controlled-path-wasm-dir docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1/norsand/engine'
    assert expected.count(old) == count
    expected = expected.replace(old, flags)
    if name == 'qualification':
        assert expected.count('tools/check_maxwell_ci.py --output') == 2
        expected = expected.replace('tools/check_maxwell_ci.py --output', 'tools/check_maxwell_ci.py --build '+maxwell+' --output')
        # Insert only the two failure-retention steps before the exact job endings.
        for successor in ('wasm-linux', 'controlled-path'):
            boundary = '    timeout-minutes: 180\n  '+successor+':\n'
            assert expected.count(boundary) == 1
            expected = expected.replace(boundary, artifact+boundary)
    else:
        expected = expected.replace('        path: "${{ runner.temp }}/packaged-laboratory.json"', '        path: |-\n          ${{ runner.temp }}/packaged-laboratory.json\n          ${{ runner.temp }}/current-dependency-guards/')
    assert expected == (ROOT/p).read_text(), p
for name in ['tools/provision_bingham_dependency_assets.py', 'tools/provision_maxwell_assets.py', 'tests/test_provision_maxwell_assets.py']:
    assert (ROOT/name).read_bytes() == (before/name).read_bytes()

for name in ['tools/check_current_dependency_assets.py','tests/test_current_dependency_assets.py','tools/build_web.py']:
    tree = ast.parse((ROOT/name).read_text())
    if name.endswith('check_current_dependency_assets.py'):
        imports = [x for x in ast.walk(tree) if isinstance(x,(ast.Import,ast.ImportFrom))]
        assert not any(isinstance(x,ast.Import) and any(a.name in ('subprocess','ctypes') for a in x.names) for x in imports)
        assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('system','popen','run','check_output','CDLL') for x in ast.walk(tree))

# Only mocked unit tests are executed. They replace bundlers and source_snapshot.
result = subprocess.run([sys.executable,'-B','-m','unittest','tests.test_current_dependency_assets','-v'], cwd=ROOT, capture_output=True, text=True)
(OUT/'pure-tests.log').write_text(result.stdout+result.stderr)
assert result.returncode == 0
ruby = subprocess.run(['ruby','-rpsych','-e', 'ARGV.each { |p| Psych.safe_load(File.read(p), permitted_classes: [], permitted_symbols: [], aliases: true); puts p }', '.github/workflows/qualification.yml','.github/workflows/pages.yml'], cwd=ROOT,capture_output=True,text=True)
(OUT/'yaml-parse.log').write_text(ruby.stdout+ruby.stderr)
assert ruby.returncode == 0
for row in manifest['files']:
    assert sha(ROOT/row['path']) == row['sha256']
report = dict(status='accepted-source-only', reviewer_run='/root/vibe_scientific_review', implementation_run='/root/vibe_capability', source_manifest=dict(path=freeze.relative_to(ROOT).as_posix(),sha256=sha(freeze)), verified_pins=len(manifest['files']), exact_forward_reconstructions=3,historical_files_unchanged=3,mocked_tests=14,workflow_yaml_documents=2,compiled_calls=0,real_bundler_calls=0,blocking_findings=[],limitations=['No actual current engine or material execution; all three separate actual build acceptances and real guard execution remain coordinator gates.'])
(OUT/'audit-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
