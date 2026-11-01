"""Saved diagnostic and independent Python binary64 elimination replay only."""
from pathlib import Path
import json,hashlib,math,importlib.util,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];LOCAL=ROOT/'.local/lade-legacy-divergence-v1';read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def pin(q):pins[str(q.relative_to(ROOT))]=h(q)
for name in ['freeze-v2.json','native-build-receipt.json','wasm-build-receipt.json']:
 q=P/name;pin(q)
 for n,s in read(q)['files'].items():assert h(ROOT/n)==s,n
spec=importlib.util.spec_from_file_location('diagnostic_fidelity',P/'fidelity.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
e=read(P/'diagnostic-execution.json');pin(P/'diagnostic-execution.json');nr=e['records'][0];assert nr['status']==0 and nr['signal'] is None and nr['error'] is None and nr['elapsed_ms']<120000
assert h(LOCAL/'native-build/atlas_legacy_trace')==nr['exe_sha256']
for key in ['stdout','stderr']:assert h(ROOT/nr[key]['path'])==nr[key]['sha256']
m=ROOT/e['records'][1]['manifest'];pin(m);wr=read(m)['records'][0];assert wr['status']==0 and wr['signal'] is None and wr['error'] is None and wr['elapsed_ms']<120000 and wr['timeout_ms']==120000 and wr['maxBuffer']==67108864
for key in ['stdout','stderr']:assert h(Path(wr[key]['path']))==wr[key]['sha256']
for key in ['loader','wasm']:assert h(Path(wr['request'][key]))==wr['request'][key+'_sha256']
rows={};old=P.with_name('outer-predictor-v1');baseline=read(old/'native-legacy-results.json')['requests'][44]
assert nr['args']==baseline['command'][1:]
for name,out,err,expected in [('native',LOCAL/'native.stdout',LOCAL/'native.stderr',ROOT/baseline['raw_path']),('wasm',LOCAL/'wasm-raw/0.stdout',LOCAL/'wasm-raw/0.stderr',ROOT/'.local/lade-outer-predictor-v1/wasm-requests/native-legacy-results-44.json')]:
 assert mod.same_response(mod.parse_response(out.read_text()),mod.parse_response(expected.read_text()))
 rows[name]=[json.loads(s) for s in err.read_text().splitlines()];assert all(r['seq']==i for i,r in enumerate(rows[name]))
 for q in [out,err,expected]:pin(q)
assert len(rows['native'])==9184 and len(rows['wasm'])==3776
n,w=rows['native'],rows['wasm'];assert n[:2]==w[:2]
diffs=[(i,j) for i in range(8) for j in range(8) if n[2]['jac'][i][j]!=w[2]['jac'][i][j]];assert diffs==[(6,0),(6,1),(6,2)]
assert n[2]['residual']==w[2]['residual'] and n[11]['phase']=='line-residual' and w[11]['phase']=='line-evaluate'
assert all(n[i]['phase']==w[i]['phase'] for i in range(11))
def solve(row,fused):
 a=[[float.fromhex(v) for v in r] for r in row['jac']];b=[-float.fromhex(v) for v in row['residual']];N=len(b)
 for k in range(N):
  pivot=max(range(k,N),key=lambda i:abs(a[i][k]));a[k],a[pivot]=a[pivot],a[k];b[k],b[pivot]=b[pivot],b[k]
  for i in range(k+1,N):
   f=a[i][k]/a[k][k]
   for j in range(k+1,N):a[i][j]=math.fma(-f,a[k][j],a[i][j]) if fused else a[i][j]-f*a[k][j]
   b[i]=math.fma(-f,b[k],b[i]) if fused else b[i]-f*b[k]
 x=[0.]*N
 for i in reversed(range(N)):
  s=b[i]
  for j in range(i+1,N):s=math.fma(-a[i][j],x[j],s) if fused else s-a[i][j]*x[j]
  x[i]=s/a[i][i]
 return [v.hex() for v in x]
replay={}
for name,r in rows.items():
 expected=[float.fromhex(v).hex() for v in r[3]['residual']]
 replay[name]={str(fused):solve(r[2],fused) for fused in [False,True]}
 assert replay[name][str(name=='native')]==expected
assert replay['native']['True'][:6]==replay['wasm']['True'][:6] and replay['native']['False'][:6]==replay['wasm']['False'][:6]
out={'passed':True,'scope':'saved observational fidelity and first-system independent algebra; not complete repair proof','trace_rows':{k:len(v) for k,v in rows.items()},'first_jacobian_differences':diffs,'first_phase_difference_index':11,'fused_replay_matches_native_all8_delta_bits':True,'separate_replay_matches_Wasm_all8_delta_bits':True,'cross_matrix_stress_delta_independent_of_history_row_difference':True,'linear_replay':replay,'pins':pins}
(P/'independent-review/saved-diagnostic-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['linear_replay','pins']}))
