"""Saved bytes only: no builds or artifact invocation."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());pins={}
for name in ['freeze-v3.json','native-first-build-receipt.json']:
 q=P/name;pins[str(q.relative_to(ROOT))]=h(q)
 for n,s in read(q)['files'].items():assert h(ROOT/n)==s,n
r=read(P/'native-legacy-exact-results.json');old=P.with_name('outer-predictor-v1');baseline=read(old/'native-legacy-results.json')['requests'][44]
cmd=baseline['command'].copy();cmd[0]=str(ROOT/'.local/lade-fused-linear-v1/native-build/atlas_lade_domain_candidate');assert r['command']==cmd
assert r['passed'] is True and r['returncode']==0 and r['timeout_seconds']==120 and 0<r['elapsed_seconds']<120
for key in ['stdout','stderr','baseline']:
 q=ROOT/r[key]['path'];assert h(q)==r[key]['sha256'];pins[str(q.relative_to(ROOT))]=h(q)
assert h(Path(cmd[0]))==r['exe_sha256'];assert (ROOT/r['stdout']['path']).read_bytes()==(ROOT/baseline['raw_path']).read_bytes()
a=read(ROOT/r['stdout']['path']);assert a['ok'] and 'elapsed_ms' not in a and a['diagnostics']['iterations']==1004 and a['diagnostics']['substeps']==64 and a['diagnostics']['rejected']==63
flags=(P/'native-first-build-configuration/flags.make').read_text();assert 'ATLAS_TEST_OUTER_BUDGET' not in flags and 'ATLAS_DISABLE_OUTER_REUSE' not in flags and '-O3' in flags
count=0
for q in (P/'proposed-native-source').rglob('*'):
 if q.is_file():assert q.read_bytes()==(ROOT/'.local/lade-fused-linear-v1/native-source'/q.relative_to(P/'proposed-native-source')).read_bytes();count+=1
pins[str((P/'native-legacy-exact-results.json').relative_to(ROOT))]=h(P/'native-legacy-exact-results.json')
out={'passed':True,'scope':'exact first native legacy compatibility prerequisite only','whole_response_byte_identical':True,'elapsed_seconds':r['elapsed_seconds'],'source_mirror_files':count,'first_build_receipt_files':len(read(P/'native-first-build-receipt.json')['files']),'production_default_budget':30,'pins':pins}
(P/'independent-review/saved-first-gate-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='pins'}))
