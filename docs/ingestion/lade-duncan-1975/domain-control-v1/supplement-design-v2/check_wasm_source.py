"""Apply identical separately frozen elastic source gates to saved Wasm output."""
from pathlib import Path
import hashlib,json
import check_domain_supplement as audit
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
reports={n:json.loads((HERE/n).read_text()) for n in ['native-domain-results.json','native-supplement-results.json']}
wasm=json.loads((HERE/'wasm-results.json').read_text()); bindings={}
for row in wasm['records']:
    name=row['study']
    if name not in reports:continue
    command=reports[name]['requests'][row['index']]['command'];raw=ROOT/row['raw_path'];bindings[str(raw.relative_to(ROOT))]=hashlib.sha256(raw.read_bytes()).hexdigest()
    audit.audit({'command':command},json.loads(raw.read_text()),f'{name}_{row["index"]}')
for name,native in reports.items():
    selected=[row for row in wasm['records'] if row['study']==name]
    responses=[json.loads((ROOT/row['raw_path']).read_text()) for row in selected]
    audit.audit_prefix([native['requests'][row['index']] for row in selected],responses,'wasm_'+name)
report=dict(id='lade1975-wasm-source-supplement-v1',checks=audit.checks,passed=all(c['passed'] for c in audit.checks),raw_hashes=bindings,input_hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in [*reports,'wasm-results.json','SUPPLEMENT_POLICY.json','check_domain_supplement.py','check_wasm_source.py']})
(HERE/'wasm-source-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],checks=len(audit.checks),failures=[c for c in audit.checks if not c['passed']]),indent=2));raise SystemExit(0 if report['passed'] else 1)
