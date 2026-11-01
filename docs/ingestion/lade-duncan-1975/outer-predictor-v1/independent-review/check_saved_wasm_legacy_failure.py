"""Saved bytes only, no material calls."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def pin(p):pins[str(p.relative_to(ROOT))]=h(p)
r=read(P/'wasm-results.json');pin(P/'wasm-results.json');m=ROOT/'.local/lade-outer-predictor-v1/wasm-bounded-literal/manifest.json';records=read(m)['records'];pin(m)
assert len(r['records'])==979 and len(records)==935 and r['passed'] is False and r['v4_passed'] is True and r['historical_legacy_passed'] is False
fails=[x for x in r['records'] if not x['passed']];assert len(fails)==1;f=fails[0];assert f['study']=='native-legacy-results.json' and f['index']==44
for row in records:
 assert row['status']==0 and row['signal'] is None and row['error'] is None and row['elapsed_ms']<120000
 for key in ['stdout','stderr']:
  q=Path(row[key]['path']);assert h(q)==row[key]['sha256']
for row in r['records']:
 if 'raw_path' in row:assert h(ROOT/row['raw_path'])==row['raw_sha256']
for name,sha in r['input_report_hashes'].items():assert h(P/name)==sha
assert h(P/'check_wasm_bounded.mjs')==r['checker_sha256']
for name,key in [('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256')]:assert h(ROOT/'.local/lade-outer-predictor-v1/wasm-build'/name)==r[key]
row=read(P/'native-legacy-results.json')['requests'][44];native=read(ROOT/row['raw_path']);w=read(ROOT/f['raw_path']);request=records[834]
assert read(Path(request['stdout']['path']))==w
assert request['request']['name']=='atlas_integrate' and request['request']['encoded_args']==[row['command'][row['command'].index('--model')+1],row['command'][row['command'].index('--parameters')+1],row['command'][row['command'].index('--initial')+1],row['command'][row['command'].index('--strain')+1]]
assert native['ok'] and not w['ok'] and w['state']==[60000,60000,60000,0,0,0,6,0]
assert max(abs(x-y)/(101325 if i<6 or i==7 else 40) for i,(x,y) in enumerate(zip(native['state'],w['state'])))==f['max_scaled_state_error']
for p in [ROOT/row['raw_path'],ROOT/f['raw_path'],P/'native-legacy-results.json',P/'proposed-native-source/include/atlas/solver.hpp',P/'regression-models/baseline-v2.json']:pin(p)
out={'verdict':'aggregate FAIL retained; current v4 literal partition PASS only','literal_requests':935,'report_records':979,'failed_worker_index_0based':834,'failed_report_legacy_index':44,'worker_elapsed_ms':request['elapsed_ms'],'native':native,'wasm':w,'pins':pins}
(P/'independent-review/saved-wasm-legacy-failure-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['pins','native','wasm']}))
