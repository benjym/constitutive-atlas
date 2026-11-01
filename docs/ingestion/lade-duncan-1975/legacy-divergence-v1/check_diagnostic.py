from pathlib import Path
import json,hashlib
from fidelity import parse_response,same_response
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];LOCAL=ROOT/'.local/lade-legacy-divergence-v1';P=ROOT/'docs/ingestion/lade-duncan-1975/outer-predictor-v1'
old=json.loads((P/'native-legacy-results.json').read_text())['requests'][44]
paths={'native':LOCAL/'native.stdout','wasm':LOCAL/'wasm-raw/0.stdout'}
expected={'native':ROOT/old['raw_path'],'wasm':ROOT/'.local/lade-outer-predictor-v1/wasm-requests/native-legacy-results-44.json'}
checks=[];trace={}
for backend in paths:
 actual=paths[backend];baseline=expected[backend]
 checks.append(dict(name=backend+'_whole_response_fidelity',passed=same_response(parse_response(actual.read_text()),parse_response(baseline.read_text())),actual_sha256=hashlib.sha256(actual.read_bytes()).hexdigest(),baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest()))
 stderr=LOCAL/('native.stderr' if backend=='native' else 'wasm-raw/0.stderr');rows=[json.loads(line) for line in stderr.read_text().splitlines()]
 checks.append(dict(name=backend+'_trace_sequence',passed=bool(rows) and all(x['seq']==i for i,x in enumerate(rows))))
 trace[backend]=rows
result={'scope':'bounded observational diagnostic, not numerical qualification','checks':checks,'passed':all(x['passed'] for x in checks),'trace_counts':{k:len(v) for k,v in trace.items()}}
(HERE/'diagnostic-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
