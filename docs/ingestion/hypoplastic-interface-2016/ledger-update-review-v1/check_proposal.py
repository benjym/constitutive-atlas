"""Independent read-only proposal/simulation/cleanup/provision assessment."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';A=P/'ledger-update-v1';OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
proposal=read(A/'preservation-proposal-v2.json');assert sha(A/'preservation-proposal-v2.json')=='5c8529009b607410acc533cd40bc2539dc5780579927ec003e7add390110b05d'
def contains(v,n,h):
 if isinstance(v,dict):return v.get(n)==h or (v.get('path')==n and any(v.get(k)==h for k in ['sha256','hash'])) or any(contains(x,n,h) for x in v.values())
 return isinstance(v,list) and any(contains(x,n,h) for x in v)
actual={}
for f in P.rglob('*.json'):
 if 'ledger-update-v1' in f.parts or 'ledger-update-review-v1' in f.parts or f.name=='source-archive-map.json':continue
 try:v=read(f)
 except (ValueError,UnicodeError):continue
 matches=[n for n,h in proposal['live_ledger_pins'].items() if contains(v,n,h)]
 if matches:actual[f.relative_to(ROOT).as_posix()]=matches
assert actual=={c['path']:c['documents'] for c in proposal['consumers']}
SIM=A/'simulation-v2';sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
for item in proposal['archive_first_operations']:
 assert sha(ROOT/item['source'])==item['sha256']==sha(SIM/item['canonical_target'])
count=0
for item in proposal['sidecar_proposals']:
 path=ROOT/item['proposal_file'];assert sha(path)==item['proposed_sha256'];mapping=read(path)
 assert sha(SIM/item['path'])==item['proposed_sha256']
 actualsiblings={f.relative_to(ROOT).as_posix():sha(f) for f in (ROOT/item['path']).parent.glob('*.json') if f.name!='source-archive-map.json'}
 assert all(mapping['documents'].get(n)==h for n,h in actualsiblings.items());count+=len(actualsiblings)
for c in proposal['consumers']:
 assert sha(ROOT/c['path'])==c['sha256']
 for n in c['documents']:assert sha(checked_receipt(SIM,c['path'],n,proposal['live_ledger_pins'][n]))==proposal['live_ledger_pins'][n]
for n,h in proposal['live_ledger_pins'].items():assert sha(ROOT/n)==h and sha(SIM/n)!=h
cleanup=read(P/'cleanup-v1/removal-receipt.json');assert cleanup['removed_confirmed'] and cleanup['observed_free_delta']==411381760 and not Path(cleanup['removed']).exists()
provision=read(P/'package-v2/implicit-existing-evidence-provision.json');release=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2')
for e in provision['files']:assert sha(Path(e['source']))==sha(release/e['path'])==e['sha256']
receiptname=provision['files'][0]['retained_existing_receipt'];implicit=read(release/receiptname)
for n,h in implicit['files'].items():assert sha(release/n)==h
result={'passed':True,'consumer_closure_documents':len(actual),'old_ledger_pairs':sum(map(len,actual.values())),'sidecar_sibling_JSON_pins':count,'proposed_sidecars':len(proposal['sidecar_proposals']),'live_ledgers_unchanged':True,'drafts_only':True,'cleanup_observed_free_delta':cleanup['observed_free_delta'],'existing_implicit_interface_files_exact':len(implicit['files']),'no_apply_compiled_material_browser_remote_calls':True}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
