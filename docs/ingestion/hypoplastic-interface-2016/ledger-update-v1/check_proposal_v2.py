"""Pure isolated receipt-resolution simulation; writes only this new packet."""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');OUT=Path(__file__).resolve().parent;SIM=OUT/'simulation-v2'
assert not SIM.exists(), 'Retain prior simulation; use a distinct study before repeating'
proposal=json.loads((OUT/'preservation-proposal-v2.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=['docs/ingestion/hypoplastic-interface-2016/DELIVERY.md','docs/ingestion/hypoplastic-interface-2016/CHECKLIST.md','docs/ingestion/hypoplastic-interface-2016/tracking-review-v1/decision.json','models/research/interface2016/hvwe2016-reconciled-fixed-local.json','catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json','docs/ingestion/hypoplastic-interface-2016/execution-v1/source-freeze-v2.json']
before={name:sha(ROOT/name) for name in protected}
def put(name,data):
 target=SIM/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
for item in proposal['archive_first_operations']:
 assert sha(ROOT/item['source'])==item['sha256'];put(item['canonical_target'],(ROOT/item['source']).read_bytes())
for c in proposal['consumers']:
 assert sha(ROOT/c['path'])==c['sha256'];put(c['path'],(ROOT/c['path']).read_bytes())
for item in proposal['sidecar_proposals']:
 assert sha(ROOT/item['proposal_file'])==item['proposed_sha256'];put(item['path'],(ROOT/item['proposal_file']).read_bytes())
sibling_checks=[]
for item in proposal['sidecar_proposals']:
 pins=item['documents']
 actual={q.relative_to(ROOT).as_posix():sha(q) for q in (ROOT/item['path']).parent.glob('*.json') if q.name!='source-archive-map.json'}
 assert all(pins.get(n)==h for n,h in actual.items())
 for n,h in actual.items():
  put(n,(ROOT/n).read_bytes());assert sha(SIM/n)==h
  sibling_checks.append({'path':n,'sha256':h})
for name,digest in proposal['live_ledger_pins'].items():
 assert sha(ROOT/name)==digest;draft=OUT/(Path(name).stem+'.draft.md');put(name,draft.read_bytes());assert sha(SIM/name)!=digest
sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
checks=[]
for c in proposal['consumers']:
 for name in c['documents']:
  expected=proposal['live_ledger_pins'][name];resolved=checked_receipt(SIM,c['path'],name,expected);assert sha(resolved)==expected
  assert resolved.relative_to(SIM).as_posix()=='catalogue/source-snapshots/'+expected+'/'+name
  checks.append({'consumer':c['path'],'original_path':name,'original_sha256':expected,'resolved':resolved.relative_to(SIM).as_posix()})
assert before=={name:sha(ROOT/name) for name in protected}
report={'passed':True,'simulation_only':True,'actual_root_ledger_or_receipt_changes':False,'proposed_maps':len(proposal['sidecar_proposals']),'consumer_documents':len(proposal['consumers']),'old_ledger_receipt_pairs_resolved_after_simulated_successor_replacement':len(checks),'checks':checks,'protected_live_files_unchanged':before,'sibling_receipt_document_pins_verified':sibling_checks,'successor_draft_hashes':{n:sha(OUT/n) for n in ['DELIVERY.draft.md','CHECKLIST.draft.md']},'git_build_material_browser_calls':0,'instruction':'No apply mode. Coordinator must recheck pins/current evidence and separately review final successor prose before archival/map installation.'}
(OUT/'proposal-check-results-v2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','protected_live_files_unchanged']},indent=2))
