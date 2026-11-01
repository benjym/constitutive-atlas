"""Read-only Git index/source audit of the exact merged release stage."""
from pathlib import Path
import hashlib,json,subprocess,sys,ast
r=Path(sys.argv[1]).resolve();pre=Path('docs/ingestion/duncan-chang-1970/release-v2');g=lambda *args:subprocess.check_output(['git',*args],cwd=r);h=lambda b:hashlib.sha256(b).hexdigest();rp=pre/'staging-v3/receipt.json';raw=(r/rp).read_bytes();assert h(raw)=='1549e09b7b8646aacf53ef030d190c20d19dc55b866466a22bc77d14380031a8';receipt=json.loads(raw)
assert g('rev-parse','HEAD').decode().strip()==receipt['first_parent'];assert g('rev-parse','MERGE_HEAD').decode().strip()==receipt['remote_parent'];assert not g('ls-files','-u')
selected={e['path']:e for e in receipt['files']};changed=set(g('diff','--cached','--name-only','HEAD','-z').decode().rstrip('\0').split('\0'));assert len(changed)==251 and changed==set(selected)|{str(rp)}
for p,e in selected.items():
 b=g('show',':'+p);assert h(b)==e['sha256'] and len(b)==e['bytes'] and b==(r/p).read_bytes()
assert g('show',':'+str(rp))==raw
# No runtime, scientific definition, UI, generator, workflow, or catalogue metadata reversion.
assert all(p.startswith(('docs/','catalogue/source-snapshots/','tests/')) or p.endswith('/source-archive-map.json') for p in changed)
for p in ['.github/workflows/verify.yml','catalogue/manifest.json','models/duncan-chang-1970-endpoint-average.json','catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json']:
 assert (r/p).read_bytes()==g('show',receipt['first_parent']+':'+p)
for folder in ['cpp','cmake','atlas','schemas','models','web','tools']:
 assert not g('diff','--cached','--name-only','HEAD','--',folder)
for p in ['tests/test_capacity.py','tests/test_classic_publications.py','tests/test_historical_generation.py','tests/test_publications.py','tests/test_trace_operator_evidence.py','tests/fixtures/current-fourteen-duncan-v1.json']:
 assert (r/p).read_bytes()==g('show',receipt['remote_parent']+':'+p)
def methods(b):return {n.name:ast.dump(n,include_attributes=False) for c in ast.parse(b).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods((r/'tests/test_catalogue.py').read_text());b=methods(g('show',receipt['remote_parent']+':tests/test_catalogue.py').decode());assert all(a[k]==v for k,v in b.items());assert a.keys()-b.keys()=={'test_implicit_path_route_requires_exact_approval'}
# Existing frozen source observation has only the disclosed provenance-map drift.
freeze=json.loads((r/pre/'package-source-freeze-v1.json').read_text());drift=[]
for p,d in freeze['files'].items():
 if h((r/p).read_bytes())!=d:
  drift.append(p);archive=r/'catalogue/source-snapshots'/d/p;assert h(archive.read_bytes())==d
assert drift==['catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json']
log=(r/pre/'merge-6fed-v1/focused-tests-v2.log').read_text();assert 'Ran 21 tests' in log and log.rstrip().endswith('OK')
print(json.dumps({'status':'PASS','first_parent':receipt['first_parent'],'remote_parent':receipt['remote_parent'],'staged_files':len(changed),'receipt_bound_files':len(selected),'receipt_excludes_only_itself':True,'all_staged_blobs_equal_working_and_receipt':True,'production_code_UI_model_workflow_catalogue_unchanged_from_accepted_parent':True,'remote_tests_and_fixture_exact':6,'remote_catalogue_methods_unchanged':len(b),'additional_accepted_negative_method':1,'package_freeze_provenance_drift':drift,'saved_affected_tests':21,'limitations':['Administrative reviewer additions require separate exact staged binding','Fresh full CI and live E8 still pending']},indent=2))
