"""Review retained followup observations; never execute the compiled runners."""
import json,math,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda n:json.loads((B/n).read_text())
msha=sha(B/'model.json');h=read('hydro-domain-results.json');hp=read('hydro-domain-policy.json')
assert h['model_sha256']==msha and h['policy_sha256']==sha(B/'hydro-domain-policy.json')
rows=[]
for c in h['cases']:
 K,n=(2300,.8) if c['set']=='dense' else (1600,.86)
 crit=-(60000/101325)**(1-n)/((1-n)*K)
 assert math.isclose(crit,c['critical_per_axis_strain'],rel_tol=1e-14)
 assert c['complete'] and len(c['requests'])==c['steps']
 assert all(r['response']['ok'] for r in c['requests'])
 fraction=c['fraction'];before=fraction<1
 pref=101325*((60000/101325)**(1-n)*(1-fraction))**(1/(1-n)) if before else None
 if before:assert math.isclose(pref,c['source_final_pressure_Pa'],rel_tol=1e-13)
 assert c['domain_event_fidelity_failure']==(not before)
 rows.append({k:c[k] for k in ['set','fraction','steps','complete','relative_pressure_error','domain_event_fidelity_failure']})
assert len(rows)==16 and not h['source_domain_gate_passed']
for label in ['dense','loose']:
 errors=[c['relative_pressure_error'] for c in h['cases'] if c['set']==label and c['fraction']==.5]
 assert len(errors)==4 and all(a>b for a,b in zip(errors,errors[1:]))
l=read('native-lifecycle-corrected-results.json');lp=read('lifecycle-corrected-policy.json')
assert l['model_sha256']==msha and l['policy_sha256']==sha(B/'lifecycle-corrected-policy.json')
assert len(l['checks'])==38 and l['passed'] and all(c['passed'] for c in l['checks'])
# Independently check the recorded failure/retry premise, separate from check booleans.
for start in [0,len(l['requests'])//2]:
 rr=l['requests'][start:start+len(l['requests'])//2]
 failure=rr[4];cmd=failure['command'];z0=list(map(float,cmd[cmd.index('--initial')+1].split(',')))
 assert '--integration-settings' in cmd and not failure['response']['ok'] and failure['response']['state']==z0
 assert all(not rr[i]['response']['ok'] for i in [5,6,7])
 assert rr[8]['response']['ok'] and rr[9]['response']['ok'] and rr[8]['response']['state']==rr[9]['response']['state']
w=read('wasm-results.json');assert w['model_sha256']==msha and w['policy_sha256']==sha(B/'wasm-policy.json')
assert w['native_triaxial_report_sha256']==sha(B/'native-triaxial-results.json') and w['native_lifecycle_report_sha256']==sha(B/'native-lifecycle-results.json')
assert len(w['records'])==56 and not w['passed']
failed=[r for r in w['records'] if not r['passed']];assert len(failed)==1
assert failed[0]['kind']=='lifecycle' and failed[0]['index']==20 and failed[0]['native_ok'] and not failed[0]['ok']
for r in w['records']:assert sha(r['raw_path'])==r['raw_sha256']
manifest=read('wasm-source-manifest.json');assert all(sha(r['path'])==r['sha256'] for r in manifest['files'])
result={'id':'REVIEW-lade-duncan-lifecycle-v2-followup','model_sha256':msha,'hydro_cases':rows,
 'hydro_crossing_failure_count':8,'hydro_interpretation':'Both sets, all four partitions complete at 1.25 critical strain: independently checked source-domain conformance failure. Interior errors decrease; no retrospective tolerance pass.',
 'corrected_lifecycle':{'retained_checks':38,'retained_passed':True,'scope':'Bounded corrected oracle and actual invalid/forced-failure cases; does not replace original failed study.'},
 'wasm':{'records':56,'failed_records':failed,'raw_hashes':'all 56 match','source_snapshot_hashes':f"all {len(manifest['files'])} match",'interpretation':'Actual retained backend status/state mismatch; native success versus Wasm failure remains unresolved, regardless of whether source should complete this crossing.'},
 'limits':['No native/Wasm execution','Corrected lifecycle assertions inspected as retained evidence, not independently rerun acceptance','No gate waiver or E5 approval']}
(B/'lifecycle-review'/'followup-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('followup hash/algebra review complete; source-domain and Wasm gates remain FAIL')
