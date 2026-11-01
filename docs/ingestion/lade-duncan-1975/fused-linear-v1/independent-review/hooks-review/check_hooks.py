"""Source-only hook closure/structural and prospective F-binding checks."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/ingestion/lade-duncan-1975/atlas-integration-v1'
HOOKS = BASE / 'hooks-proposed-v1'
MODEL = 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
checks=[]
def test(name, passed):
    assert passed, name
    checks.append({'name': name, 'passed': True})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
proposal_path=HOOKS/'PROPOSAL-v4.json'
proposal=json.loads(proposal_path.read_bytes())
for group in ['before','proposed']:
    for name,pin in proposal[group].items():
        test(group+' exact '+name, sha(HOOKS/group/name)==pin)
        if group=='before':test('current uninstalled '+name,sha(ROOT/name)==pin)
before=json.loads((HOOKS/'before/catalogue/manifest.json').read_bytes())
after=json.loads((HOOKS/'proposed/catalogue/manifest.json').read_bytes())
old={r['id']:r for r in before['models']}; new={r['id']:r for r in after['models']}
test('one exact added discovery ID',set(new)-set(old)=={MODEL} and not(set(old)-set(new)))
test('other discovery rows unchanged',all(new[k]==v for k,v in old.items() if k!='lade-duncan-1975'))
test('special route and ordinary exclusion',new[MODEL]['implicit_path_laboratory']=='index.html' and new[MODEL]['executable'] is False)
before=json.loads((HOOKS/'before/catalogue/publications.json').read_bytes())
after=json.loads((HOOKS/'proposed/catalogue/publications.json').read_bytes())
# Reversing the one prospective mapping must restore the complete original object.
def remove_mapping(value):
    if isinstance(value,dict):
        return {k:([x for x in v if x!=MODEL] if k=='model_ids' else remove_mapping(v)) for k,v in value.items()}
    if isinstance(value,list):return [remove_mapping(v) for v in value]
    return value
test('publication identity preserved; mapping only',remove_mapping(after)==before and json.dumps(after).count(MODEL)==1)
app=(HOOKS/'proposed/web/app.js').read_text()
test('all existing routers preserved',all('setup'+n+'Laboratory({chart,cancelOrdinary:' in app for n in ['Timed','Sls','Path','Maxwell','ImplicitPath']))
test('hide ordinary import after select',"const active=timedView.select(id);\n    $('import-run').hidden=active;\n    return active;" in app)
test('JavaScript syntax',subprocess.run(['node','--check',str(HOOKS/'proposed/web/app.js')],capture_output=True,timeout=10).returncode==0)
builder=(HOOKS/'proposed/tools/build_web.py').read_text();ast.parse(builder)
test('builder syntax',True)
test('Maxwell bundle retained', 'bundle_maxwell(dest,args.maxwell_wasm_dir)' in builder)
test('guarded profile bundle plus package gate', 'bundle_implicit_path(dest,args.implicit_path_wasm_dir)' in builder and "tools/test_implicit_path_package.py" in builder and 'check=True' in builder)
test('fresh retained package report directory', 'tempfile.mkdtemp(' in builder and 'implicit-path-package-checks' in builder)
binding=json.loads((BASE/'EXPECTED_F_BINDING.json').read_bytes())
manifest=binding['expected_runtime']
test('prospective runtime map digest',hashlib.sha256(json.dumps(manifest['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==manifest['sha256']==binding['binding']['runtime_sha256'])
test('29 generic runtime files',len(manifest['files'])==29)
changes=[]
for name,pin in manifest['files'].items():
    test('F exact runtime '+name,sha(ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/proposed-native-source'/name)==pin)
    if sha(ROOT/'cpp/profiles/implicit-path-v1'/name)!=pin:changes.append(name)
test('only profile solver pending install',changes==binding['changed_installed_paths']==['include/atlas/solver.hpp'])
for row in binding['binding']['ordered_inputs']:test('canonical input '+row['path'],sha(ROOT/row['path'])==row['sha256'])
for name,pin in binding['binding']['generated'].items():test('F generated '+name,sha(ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/proposed-native-source/generated'/name)==pin)
for name,key in [('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256')]:test('F artifact read-only pin '+name,sha(ROOT/'.local/lade-fused-linear-v1/wasm-build'/name)==binding['binding'][key])
(OUT/'hook-check-results.json').write_text(json.dumps({'passed':True,'checks':checks,'scope':'Pure source parsing/hash/structure only; no compiler, packaging or material calls'},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks)}))
