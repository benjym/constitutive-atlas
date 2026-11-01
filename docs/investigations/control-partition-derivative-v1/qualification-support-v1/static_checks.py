"""Read-only validation of the prepared packet; never calls a solver."""
import ast,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((BASE/'adapter-proof.json').read_text())
for row in proof:
    ast.parse((BASE/row['adapter']).read_text())
    assert sha(BASE/row['adapter'])==row['adapter_sha256']
    assert row['exact_reverse_substitution'] is True
    restored=(BASE/row['adapter']).read_text()
    for item in reversed(row['replacements']):
        a,b=item['original'],item['replacement']
        if b=='': restored=restored.replace("spec.loader.exec_module(m)\n\n","spec.loader.exec_module(m)\n"+a+"\n",1)
        else: assert restored.count(b)==1; restored=restored.replace(b,a)
    assert hashlib.sha256(restored.encode()).hexdigest()==row['source_sha256']
for name in ['prepare.py','adapters/prepare_sls_reports.py','static_checks.py']:
    ast.parse((BASE/name).read_text())
selection=json.loads((BASE/'support-selection.json').read_text())
sets=json.loads((BASE/'source-manifest-sets.json').read_text())
for profile,info in sets['profiles'].items():
    assert all(selection['files'][p]['sha256']==h for p,h in info['files'].items())
    assert hashlib.sha256(json.dumps(info['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==info['baseline_manifest_sha256']
if (BASE/'manifest.json').exists():
    manifest=json.loads((BASE/'manifest.json').read_text())
    assert all(sha(BASE/p)==h for p,h in manifest['files'].items())
print(json.dumps(dict(passed=True,source_only=True,adapters=len(proof),selected_files=len(selection['files']),missing_selection=selection['missing'],source_set_counts={p:len(v['files'])for p,v in sets['profiles'].items()},guarded_package_closure_proven=False),indent=2))
