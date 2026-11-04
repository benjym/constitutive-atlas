from pathlib import Path
import json,hashlib,importlib.util,sys
r=Path(__file__).resolve().parents[5];b=r/'docs/ingestion/manzari-dafalias-1997/delivery-v1';out=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=['tools/profile_source_compatibility_baseline.py','tools/build_interface2016_baseline_web.py','tools/test_interface2016_baseline_package.mjs']
old=json.loads((b/'direct-profile-compatibility-implementation-v1/bindings.json').read_text())['interface2016'];new=json.loads((b/'upstream-interface-compatibility-v1/bindings.json').read_text())['interface2016']
assert {k for k in set(old)|set(new) if old.get(k)!=new.get(k)}=={'source_files','proof_manifest_sha256'}
source=json.loads((b/'upstream-merge-review-v1/source-decision.json').read_text())
assert {k for k in old['source_files'] if old['source_files'][k]!=new['source_files'][k]}==set(source['changed_source_pins'])
for n,v in source['changed_source_pins'].items():assert old['source_files'][n]==v['qualified'] and new['source_files'][n]==v['current']==h(r/n)
assert (r/files[1]).read_bytes().replace(b'from profile_source_compatibility_baseline import',b'from profile_source_compatibility import')==(r/'tools/build_interface2016_web.py').read_bytes()
a=(r/files[2]).read_text().replace('upstream-interface-implementation-review-v1','direct-profile-compatibility-implementation-review-v1').replace('upstream-interface-compatibility-v1/bindings.json','direct-profile-compatibility-implementation-v1/bindings.json').replace('upstream-interface-compatibility-v1/manifest.json','direct-profile-compatibility-v1/manifest.json').replace('current17-baseline-interface-implementation-review-v1','current17-direct-profile-compatibility-implementation-review-v1');assert a==(r/'tools/test_interface2016_compatible_package.mjs').read_text()
eng=r/'web/engines/current17-baseline-compatible/interface2016';oldeng=r/'web/engines/current17-compatible/interface2016'
assert {p.relative_to(eng) for p in eng.rglob('*') if p.is_file()}=={p.relative_to(oldeng) for p in oldeng.rglob('*') if p.is_file()}
for p in eng.rglob('*'):
 if p.is_file() and p.name!='source-compatibility.json':assert p.read_bytes()==(oldeng/p.relative_to(eng)).read_bytes()
decision=dict(identity='current17-baseline-interface-implementation-review-v1',accepted=True,proof_manifest_sha256=h(b/'upstream-interface-compatibility-v1/manifest.json'),bindings_sha256=h(b/'upstream-interface-compatibility-v1/bindings.json'),implementation={n:h(r/n) for n in files},reviewer_run='/root/md1997_upstream_merge_review')
spec=importlib.util.spec_from_file_location('review_target',r/files[0]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);original=m.regular
m.regular=lambda root,name:json.dumps(decision).encode() if name==m.DECISION else original(root,name)
assert m.validate(r,eng,'interface2016')['qualification']['status']=='passed'
negative=[]
for name in decision:
 bad=dict(decision);bad[name]=None;m.regular=lambda root,n,bad=bad:json.dumps(bad).encode() if n==m.DECISION else original(root,n)
 try:m.validate(r,eng,'interface2016')
 except Exception:negative.append(name)
 else:raise AssertionError('accepted invalid '+name)
assert len(negative)==6
m.regular=original
spec=importlib.util.spec_from_file_location('guard',r/'tools/check_current_dependency_assets.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
assert len(g.selected_engines(current17_baseline=True))==3
for kw in [dict(plan_path=Path('x')),dict(plan_sha256='a'*64)]:
 try:g.selected_engines(current17_baseline=True,**kw)
 except ValueError:negative.append('guard-'+next(iter(kw)))
 else:raise AssertionError('guard accepted simultaneous historical/current selection')
report=dict(identity='interface-baseline-implementation-inspection-v1',source_only=True,compiled_calls=0,passed=True,negative_fixtures=negative,implementation=decision['implementation'],integration_bindings={n:h(r/n) for n in ['tools/build_web.py','tools/check_current_dependency_assets.py','tools/check_native_fixture_contracts.py','.github/workflows/pages.yml','.github/workflows/qualification.yml']},checks=['exact7 reviewed source pin updates only; explicit proof identity update','builder reverses byte-exact by import replacement','checker reverses byte-exact by evidence/identity replacement; numerical body unchanged','retained engine files except exact source row byte-identical','actual validator positive uses in-memory decision fixture only','six malformed decision fields rejected','current guard selection returns3 routes; rejects mixed plan selections'],blocking_findings=[],scope_limit='actual bundled package/runtime execution and hosted integration gates remain coordinator responsibility')
(out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
print('PASS source implementation audit; decision '+h(out/'decision.json'))
