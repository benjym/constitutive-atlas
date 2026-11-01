from pathlib import Path
import json,hashlib,sys,subprocess,tempfile,importlib.util
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/web-tmd2-reporting-agent-v1';O=P/'independent-review/final-v1';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sys.path.insert(0,str(R))
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
# Saved parent checker itself performs all historical checked_receipt/shaped snapshot checks.
z=subprocess.run(['python3','-B',str(P/'check_saved.py')],cwd=R,text=True,capture_output=True);assert z.returncode==0,z.stderr
plan=read(P/'archive-plan-v2.json');installation=read(P/'installation.json');prospective=read(P/'independent-review/prospective-receipt.json');addendum=read(P/'independent-review/addendum-v2-receipt.json')
assert installation['passed']and installation['prospective_receipt_sha256']==sha(P/'independent-review/prospective-receipt.json')and installation['addendum_receipt_sha256']==sha(P/'independent-review/addendum-v2-receipt.json')
assert sha(P/'archive-plan-v2.json')==addendum['binding']['archive_plan_v2_sha256']and sha(P/'preserve_sources_v2.py')==addendum['binding']['installer_v2_sha256']
for p,h in installation['installed'].items():assert sha(R/p)==h==prospective['binding']['candidates'][p]
for p,m in plan['maps'].items():
 if p in plan['prior']:
  old=read(R/'catalogue/source-snapshots'/plan['prior'][p]/p);assert all(m['documents'].get(k)==v for k,v in old['documents'].items())and all(e in m['entries']for e in old['entries'])
for p,h in plan['prior'].items():assert (P/'prior-source'/p).read_bytes()==(R/'catalogue/source-snapshots'/h/p).read_bytes()
assert (P/'archive-apply-v2.stderr.txt').read_text()==''and 'Applied exact additive preservation'in(P/'archive-apply-v2.stdout.txt').read_text()
assert 'Plan or source identities changed'in(P/'archive-apply.stderr.txt').read_text()
# Re-run only installed Python projection/archive tests; no solver/runtime.
tests=subprocess.run(['python3','-B','-m','unittest','tests.test_web_benchmark','tests.test_web_tmd2_review','tests.test_evidence_archives','-v'],cwd=R,text=True,capture_output=True);assert tests.returncode==0,tests.stderr;assert 'Ran 23 tests'in tests.stderr
package=read(P/'package-manifest.json');site=Path(package['path']);baseline=read(R/'docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json');assert package['baseline_manifest_sha256']==sha(R/'docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json')
assert len(package['files'])==957 and {str(x.relative_to(site))for x in site.rglob('*')if x.is_file()}==set(package['files'])
for p,x in package['files'].items():assert sha(site/p)==x['sha256']and(site/p).stat().st_size==x['bytes']
a=baseline['files'];b=package['files'];assert sorted(set(b)-set(a))==package['added']==['benchmark-tmd2/review/decision.json','benchmark-tmd2/review/review.html','benchmark-tmd2/review/review.md'];assert not(set(a)-set(b));assert sorted(p for p in set(a)&set(b)if a[p]!=b[p])==package['changed']==['index.html','tmd2.html']
from tools.build_benchmark import bundle
with tempfile.TemporaryDirectory(prefix='tmd2-final-pure-consumer-')as t:
 pins=bundle(Path(t));assert pins==package['benchmark_public_assets']
 assert (Path(t)/'tmd2.html').read_bytes()==(site/'tmd2.html').read_bytes()
 for p,h in pins.items():assert sha(Path(t)/'benchmark-tmd2'/p)==h==sha(site/'benchmark-tmd2'/p)
assert(site/'index.html').read_bytes()==(R/'web/index.html').read_bytes()
review=R/'docs/benchmarks/kfs-tmd2-reporting-agent-v1';decision=read(review/'decision.json')
assert(site/'benchmark-tmd2/review/decision.json').read_bytes()==(review/'decision.json').read_bytes()and(site/'benchmark-tmd2/review/review.md').read_bytes()==(review/'README.md').read_bytes()
# Exact browser captures read by parent checker; inspect purpose/dimensions/links independently.
for name,width in [('desktop-observation.json',1280),('mobile-observation.json',390),('review-observation.json',1280),('mobile-review-observation.json',390)]:
 d=read(P/'browser'/name);assert d['width']==d['documentWidth']==width
assert 'favicon.ico'in(P/'browser/all-console.txt').read_text()and '404'in(P/'browser/all-console.txt').read_text()
# Historical direct-live source-map mismatch is preserved; verify exact archived replay view.
history=read(P/'historical-replay.json');view=Path(history['view']);reviewrel=Path('docs/benchmarks/kfs-tmd2-reporting-agent-v1');statusrel=Path('docs/benchmarks/kfs-tmd2-reporting-status-v1');reviewmanifest=read(R/reviewrel/'manifest.json');wanted={}
def add(p,h):
 assert p not in wanted or wanted[p]==h;wanted[p]=h
for p,h in reviewmanifest['public_inputs'].items():add(p,h)
for p,h in reviewmanifest['outputs'].items():add(str(reviewrel/p),h)
for name in ['manifest.json','check-results.json','private-check-results.json']:add(str(reviewrel/name),sha(R/reviewrel/name))
for p,h in read(R/statusrel/'integration.json')['files'].items():add(p,h)
for p,h in read(R/statusrel/'parent-inputs.json').items():add(p,h)
for name in ['integration.json','check_saved.py','parent-inputs.json','parent-replays.json','parent-review-check-private.json']:add(str(statusrel/name),sha(R/statusrel/name))
assert len(wanted)==165 and set(wanted)==set(history['files'])and {str(p.relative_to(view))for p in view.rglob('*')if p.is_file()}==set(wanted)
archived=[]
for p,h in wanted.items():
 row=history['files'][p];assert row['sha256']==h and sha(view/p)==h and sha(R/row['selected'])==h
 original=R/p;expected=p if original.is_file()and sha(original)==h else str(Path('catalogue/source-snapshots')/h/p);assert row['selected']==expected
 if expected!=p:archived.append(p)
assert archived==history['archived_inputs']==['docs/reviews/tmd2-web-snapshot-v1/source-archive-map.json']
for row in history['results']:
 assert row['returncode']==0
 for stream in ['stdout','stderr']:assert sha(P/(row['id']+'-historical.'+stream+'.txt'))==row[stream+'_sha256']
 if row['id'].startswith('scientific-'):
  expected=R/reviewrel/('private-check-results.json'if row['id'].endswith('private')else'check-results.json');assert read(P/(row['id']+'-historical.stdout.txt'))==read(expected)
# No reviewer private-data access: saved private aggregates compared only. Original public/status scripts are pure saved checks.
for id,script in [('scientific-public',view/reviewrel/'check_saved.py'),('coordinator-status',view/statusrel/'check_saved.py')]:
 replay=subprocess.run(['python3','-B',str(script)],cwd=view,capture_output=True,text=True);assert replay.returncode==0 and replay.stdout==(P/(id+'-historical.stdout.txt')).read_text()and replay.stderr==''
failures=read(P/'retained-live-path-failures.json');assert len(failures)==2 and all(x['returncode']==1 for x in failures)
for n in ['scientific','coordinator']:assert 'source-archive-map.json'in(P/(n+'-live-path-failure.stderr.txt')).read_text()
print(json.dumps({'passed':True,'saved_parent_check':json.loads(z.stdout),'installed_pure_tests':23,'preserved_prior_paths':32,'old_map_entries_and_docpins_additive':True,'package_inventory_sizes_hashes_exact':957,'normal_benchmark_consumer_reproduced_exact_output':True,'public_review_exact_assets':3,'desktop_mobile_pages_widths':[1280,390],'original_apply_guard_failure_retained':True,'favicon404_retained':True,'reviewer_compiled_calls':0,'reviewer_builds':0,'reviewer_browser_actions':0,'fresh_full_engine_package_reviewed':False,'scientific_rereview_or_live_delivery':False,'historical_replay_view_public_files':165,'historical_archived_input_count':1,'original_public_status_scripts_replayed':True,'saved_private_result_unchanged':True,'direct_live_hash_failures_retained':2},indent=2))
