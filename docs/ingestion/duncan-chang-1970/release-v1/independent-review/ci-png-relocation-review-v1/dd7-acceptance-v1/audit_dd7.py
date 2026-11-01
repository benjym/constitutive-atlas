"""Read-only dd7 published source and pure packet-test qualification."""
from pathlib import Path
import hashlib,json,sys,subprocess,importlib.util,io,unittest
root=Path(sys.argv[1]).resolve();context=Path(sys.argv[2]).resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
g=lambda *a:subprocess.check_output(['git',*a],cwd=root);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='dd7de01fa1695e1858de03a26aea1acabb5fa98e';assert g('rev-parse','HEAD').decode().strip()==base
packet=Path('docs/ingestion/duncan-chang-1970/release-v2/ci-png-relocation-v1');proposal=json.loads((context/packet/'relocation-proposal.json').read_text());plan=json.loads((context/packet/'preservation-v1/preservation-plan.json').read_text());pre=Path('docs/ingestion/duncan-chang-1970/release-v2');queries=[]
for e in proposal['images']:
 assert not (root/e['original_path']).exists();assert h(root/e['path'])==e['sha256'] and (root/e['path']).stat().st_size==e['bytes']
for e in proposal['original_proofs']:assert h(root/e['path'])==e['sha256']
for p,o in plan['planned_sidecars'].items():
 ours=json.loads((context/Path(o['proposed_path'])).read_text());remote=json.loads((root/p).read_text());assert all(remote['documents'].get(k)==v for k,v in ours['documents'].items());assert all(e in remote['entries'] for e in ours['entries'])
queries.extend((e['document'],e['original_path'],e['sha256']) for e in plan['bindings'])
merge=json.loads((root/pre/'merge-6fed-v1/repair-v2/plan.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in merge['bindings'] if e['document']!=str(pre/'merge-6fed-v1/repair-v1/plan.json'))
for ver in ['v1','v2','v3']:
 a=json.loads((root/pre/f'preservation-{ver}/preservation-plan.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in a['bindings'])
review=Path('docs/ingestion/duncan-chang-1970/release-v1/independent-review');a=json.loads((root/review/'merge6fed-affected-initial-results-v3.json').read_text());queries.extend((e['document'],e['path'],e['sha256']) for e in a['failures']+a['passed_predicates']);queries.extend((e['document'],e['path'],e['sha256']) for e in json.loads((root/review/'merge6fed-reverse-scan-v3.json').read_text())['missing_valid_edges'])
pp=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');a=json.loads((root/pp/'ci-compat-v3/CONTEXT_REPAIR.json').read_text());queries.extend((e['document'],e['path'],e['sha256']) for e in a['resolved']);a=json.loads((root/pp/'independent-review/ci-compat-v3/POSITIVE_REPAIR_INPUTS.json').read_text());queries.extend((d,e['path'],e['old_sha256']) for d,x in a['groups'].items() for e in x['pairs'])
remote=Path('docs/ingestion/norsand-1993/release-v1/layout-preservation-v1');a=json.loads((root/remote/'preservation.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in a['bindings']);a=json.loads((root/remote/'combined-preservation-check-v1.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in a['bindings'])
# The two basename image aliases and older output locator are actual normal receipts.
sha='27c004fc6c7d2e77e61722833aa94d4f38b15a9658c47241b4c6b64c45a46910'
for d in [str(pre/'browser-proof-v1.json'),str(review/'final-closeout-context-v2/isolated'/pre/'browser-proof-v1.json')]:queries.append((d,'response.png',sha))
# Query actual old-output locator through source record that explicitly contains it.
for d in [str(pre.parent/'release-v1/browser-public-mirrors-v1.json')]:
 custom=json.loads((root/d).read_text());assert h(root/d)=='b7d27c02ab5feb3d4b9b52e0ad44675393ff195bacec48af406303bc7e487b32'
errors=[]
for d,p,s in queries:
 try:checked_receipt(root,d,p,s)
 except Exception as e:errors.append({'document':d,'path':p,'sha256':s,'error':str(e)})
assert not errors,errors
assert not g('diff','--name-only','0cd28fc2',base,'--','cpp','atlas','schemas','models','tools','web','.github/workflows/verify.yml','tests','CMakeLists.txt')
assert (root/'tests/test_ingestion_packets.py').read_bytes()==g('show','0cd28fc2:tests/test_ingestion_packets.py')
spec=importlib.util.spec_from_file_location('dd7_packets',root/'tests/test_ingestion_packets.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([m.IngestionPackets('test_local_packet_receipts')]));assert result.wasSuccessful(),stream.getvalue()
print(json.dumps({'status':'PASS','source_commit':base,'normal_receipt_queries_passed':len(queries),'old_images_absent':3,'canonical_images_exact':3,'remote_maps_superset_all_five_accepted_proposals':True,'original_browser_proofs_reports_checkers_unchanged':True,'unmodified_pure_packet_test':'PASS actual dd7 tree','runtime_model_UI_tool_workflow_test_delta_from0cd':0,'custom_mirror_shape':'Original hash unchanged; custom crosswalk remains separately identified, not normal checked_receipt claim','limits':['No compiled calls/build/browser/remote actions','No duplicate corrective push needed','Exact dd7 run/full CI/Pages/live qualification still pending']},indent=2))
