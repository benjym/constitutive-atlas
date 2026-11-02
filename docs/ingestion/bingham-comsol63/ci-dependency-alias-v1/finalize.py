"""Seal owned candidates only. No installation or process execution."""
from pathlib import Path
import difflib,gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda n,o:(H/n).write_text(json.dumps(o,indent=2)+'\n')
assert 'Ran 55 tests' in (H/'portable-mock-tests.log').read_text() and (H/'portable-mock-tests.log').read_text().rstrip().endswith('OK')
for n in ['SOURCE-GUARDS.json','SAVED-DEPFILE-PROOF.json']:assert json.loads((H/n).read_text())['passed']
assert json.loads((H/'SUMMARY.json').read_text())['primary_edges']==0
files={};diffs=[]
for q in sorted((H/'candidates').rglob('*')):
 if not q.is_file():continue
 n=q.relative_to(H/'candidates').as_posix();live=R/n;files[n]={'before_sha256':sha(live) if live.exists() else None,'sha256':sha(q),'candidate':'candidates/'+n}
 diffs.extend(difflib.unified_diff(live.read_text().splitlines(True) if live.exists() else [],q.read_text().splitlines(True),fromfile='before/'+n,tofile='candidate/'+n))
assert len(files)==3;assert sha(R/'.github/workflows/verify.yml')==sha(H/'before/.github/workflows/verify.yml');assert sha(R/'tools/record_cmake_profile_build.py')==sha(H/'before/tools/record_cmake_profile_build.py');(H/'candidates.diff').write_text(''.join(diffs));save('INSTALLATION.json',{'installed':False,'files':files,'preservation_map_changes':0,'requires_independent_review':True})
mentions=json.loads(gzip.decompress((H/'binding-mentions.json.gz').read_bytes()));rows=[]
for n,v in mentions.items():
 reason='Immutable preparation/candidate namespace, bytes unchanged' if v['excluded_by'] else ('Historical installed transition, not a recognized path/hash pair' if n.endswith('installation-v3/RECEIPT.json') else 'Absolute immutable candidate/private-context copy pin, not live root-relative workflow')
 rows.append({'document':n,**v,'classification':reason})
save('MENTION-CLASSIFICATION.json',{'initial_mentions':len(rows),'preexisting_mentions':len(rows)-1,'active_current_workflow_consumers':0,'affected_sibling_maps':0,'reverse_edges':0,'records':rows,'later_own_packet_references':'New installation/source bindings and manifest records describe this proposal; they are not historical live consumers.'})
pins=['tools/record_cmake_profile_build.py','.github/workflows/verify.yml','docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/response-symlink-fix-v1/tests/test_build_receipts.py','docs/ingestion/bingham-comsol63/live-release-v1/macos-native-attempt1-raw.log','docs/ingestion/bingham-comsol63/live-release-v1/macos-wasm-attempt1-raw.log','docs/ingestion/bingham-comsol63/live-release-v1/FAILED-MACOS-ARTIFACT.json','runtimes/physical-time-v2/include/atlas/schedule.hpp']
save('SOURCE-BINDINGS.json',{'source_files':{n:sha(R/n) for n in pins},'root_current_context':'main40b607ba CI failed recorder prior to numerical consumer; exact SDK failure depfile unacquired','old_method_count':40,'new_method_count':15,'compiler_tool_material_build_remote_calls':0})
allfiles={q.relative_to(H).as_posix():sha(q) for q in H.rglob('*') if q.is_file() and q.name!='MANIFEST.json' and '__pycache__' not in q.parts};save('MANIFEST.json',{'identity':'bingham-ci-dependency-alias-v1','status':'prospective-source-only-review-request','files':allfiles,'installation_sha256':sha(H/'INSTALLATION.json'),'independent_acceptance_claimed':False});print(json.dumps({'manifest_sha256':sha(H/'MANIFEST.json'),'files':len(allfiles),'candidates':files},indent=2))
