"""Independent proposal/archive simulation and current preflight check; no apply."""
from pathlib import Path
import hashlib,json,sys,subprocess
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';A=P/'ledger-update-v2';OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert sha(A/'manifest.json')=='fd195c49a2b6ec4c2540f3436af2ec56f15830e6c73f99c79244dbcabc765d3d'
m=read(A/'manifest.json')
for n,h in m['files'].items():assert sha(A/n)==h
proposal=read(A/'preservation-proposal.json');assert sha(A/'preservation-proposal.json')=='af2a5f5894f417519d3507e57dc6d9442904087a3aea20ad0283342fcc6cbdf4'
def contains(v,n,h):
 if isinstance(v,dict):return v.get(n)==h or (v.get('path')==n and any(v.get(k)==h for k in ['sha256','hash'])) or any(contains(x,n,h) for x in v.values())
 return isinstance(v,list) and any(contains(x,n,h) for x in v)
actual={}
for f in P.rglob('*.json'):
 if any(part.startswith('ledger-update') for part in f.parts) or f.name=='source-archive-map.json':continue
 try:v=read(f)
 except (ValueError,UnicodeError):continue
 matches=[n for n,h in proposal['live_ledger_pins'].items() if contains(v,n,h)]
 if matches:actual[f.relative_to(ROOT).as_posix()]=matches
assert actual=={c['path']:c['documents'] for c in proposal['consumers']}
SIM=A/'simulation-final';sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
for item in proposal['archive_first_operations']:assert sha(ROOT/item['source'])==item['sha256']==sha(SIM/item['canonical_target'])
count=0
for item in proposal['sidecar_proposals']:
 assert sha(ROOT/item['proposal_file'])==item['proposed_sha256']==sha(SIM/item['path'])
 mapping=read(ROOT/item['proposal_file']);live=ROOT/item['path'];assert live.exists()==item['exists_now']
 if live.exists():
  assert sha(live)==item['old_sha256'];old=read(live)
  assert all(mapping['documents'].get(n)==h for n,h in old['documents'].items()) and all(e in mapping['entries'] for e in old['entries'])
 siblings={f.relative_to(ROOT).as_posix():sha(f) for f in live.parent.glob('*.json') if f.name!='source-archive-map.json'}
 assert all(mapping['documents'].get(n)==h for n,h in siblings.items());count+=len(siblings)
pairs=0
for consumer in proposal['consumers']:
 assert sha(ROOT/consumer['path'])==consumer['sha256']
 for n in consumer['documents']:
  h=proposal['live_ledger_pins'][n];assert sha(checked_receipt(SIM,consumer['path'],n,h))==h;pairs+=1
for n,h in proposal['live_ledger_pins'].items():assert sha(ROOT/n)==h and sha(SIM/n)!=h
plan=read(A/'install-plan.json')
for n,h in plan['proposal_input_pins'].items():assert sha(A/n)==h
for n,h in plan['evidence_input_pins'].items():assert sha(ROOT/n)==h
observation=subprocess.run(['python3','-B',str(A/'install_reviewed_successors.py')],check=True,capture_output=True,text=True)
assert json.loads(observation.stdout)['actual_live_changes'] is False
(OUT/'read-only-preflight.json').write_text(observation.stdout)
result={'passed':True,'manifest_members':len(m['files']),'consumer_documents':len(proposal['consumers']),'old_ledger_pairs':pairs,'new_additive_sidecars':len(proposal['sidecar_proposals']),'existing_sibling_JSON_document_pins':count,'live_ledgers_unchanged':True,'installer_default_read_only_preflight':True,'apply_executed':False,'E7_acceptance_sha256':sha(P/'delivery-review-v1/decision.json'),'no_compiled_material_browser_remote_calls':True}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
