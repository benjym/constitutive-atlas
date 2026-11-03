from pathlib import Path
import json,hashlib,copy,sys,subprocess
R=Path(__file__).resolve().parents[5];O=Path(__file__).parent;sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
B=R/'docs/ingestion/vibe-2026/main-integration-v1';before=B/'preimages/source-archive-map-before-vibe-documents.json';mp=R/'catalogue/agent-reviews/source-archive-map.json';receipt=B/'vibe-document-preservation-addition.json';rc=read(receipt);old=read(before);new=read(mp)
assert h(before)==rc['before_sha256']=='c8f01b36666babcc10ac8497da8f72186042bf1c090849998535e90c0ec41d56';assert h(mp)==rc['after_sha256']=='b86d20f19bca7ad1afc65a08985d60ee0a59a51ad070ae3790610280fb9d7bce'
expected={'catalogue/agent-reviews/vibe-2026-appendix-a-agent-v1.json':'17ba51ff302dd69c5f3bf651a64b47dcc7bbe2425461eb2a9d985f1fd63bfffe','catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json':'8e36c1984af615ece3ef4a05546871defbe05a64f6a483d295f9056f29f3ae99'}
assert rc['added_documents']==expected;restored=copy.deepcopy(new)
for path,sha in expected.items():
 assert path not in old['documents'] and restored['documents'].pop(path)==sha and h(R/path)==sha
 assert subprocess.check_output(['git','show','8543a0dbe:'+path],cwd=R)==(R/path).read_bytes()
assert restored==old;assert (json.dumps(restored,indent=2)+'\n').encode()==before.read_bytes();assert new['entries']==old['entries']
records=[]
for path in expected:
 doc=read(R/path)
 for f in doc['supporting_files']:
  resolved=checked_receipt(R,path,f['path'],f['sha256']);assert h(resolved)==f['sha256'];assert h(R/f['path'])==f['sha256']
  if path.endswith('v2.json'):records.append({'path':f['path'],'sha256':f['sha256'],'resolved':str(resolved.relative_to(R)),'direct_live_sha_matches':True})
assert len(records)==281
baseline=R/'docs/ingestion/vibe-2026/plot-presentation-v1/scientific-support-baseline-v1.json';bl=read(baseline);assert not bl['supporting_files'] and len(bl['failures'])==281;assert {f['path'] for f in bl['failures']}=={f['path'] for f in records};assert all(f['error']=='original evidence document changed after archival' for f in bl['failures'])
# Resolver itself retained byte-exact; no evidence policy modification.
assert subprocess.check_output(['git','show','8543a0dbe:atlas/evidence.py'],cwd=R)==(R/'atlas/evidence.py').read_bytes()
result={'status':'accepted','before_sha256':h(before),'map_sha256':h(mp),'addition_receipt_sha256':h(receipt),'added_documents':expected,'entries_and_all_other_bytes_after_reversal_preserved':True,'original_review_documents_unchanged_from_merged_commit':True,'resolver_unchanged_from_merged_commit':True,'v2_checked_receipts':len(records),'v2_direct_live_hashes':len(records),'supporting_files':records,'preserved_baseline':{'path':str(baseline.relative_to(R)),'sha256':h(baseline),'genuine_failures':len(bl['failures'])},'blocking_findings':[],'compiled_calls':0,'cleanup':'No temporary resources/processes/builds created; no sources or original evidence modified.'};(O/'decision.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={'files':[{'path':str(p.relative_to(R)),'sha256':h(p)} for p in [O/'audit.py',O/'decision.json',receipt,before,mp,baseline]]};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('manifest',h(O/'manifest.json'));print('decision',h(O/'decision.json'))
