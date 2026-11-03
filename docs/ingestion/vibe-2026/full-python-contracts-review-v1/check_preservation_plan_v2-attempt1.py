from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=R/'docs/ingestion/vibe-2026/full-python-contracts-v1';h=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text());d=read(P/'preservation-plan-v2.json');bindings=d['bindings'];assert len(bindings)==178 and len(d['maps'])==81
for row in bindings:
 assert h((R/row['document']).read_bytes())==row['document_sha256']
 assert h((R/row['archived_path']).read_bytes())==row['sha256']
 assert row['archived_path']=='catalogue/source-snapshots/'+row['sha256']+'/'+row['original_path']
oldcount=0;newcount=0
for row in d['maps']:
 after=row['after'];path=row['path'];assert after['version']=='immutable-source-archive-map-0.1'
 if row['before_sha256']:
  oldcount+=1;raw=(R/row['before_archive']).read_bytes();assert h(raw)==row['before_sha256'];assert subprocess.check_output(['git','show','HEAD:'+path],cwd=R)==raw;old=json.loads(raw)
 else:newcount+=1;old={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 assert {k:v for k,v in after.items() if k not in ['documents','entries']}=={k:v for k,v in old.items() if k not in ['documents','entries']}
 assert all(after['documents'].get(k)==v for k,v in old['documents'].items())
 assert after['entries'][:len(old['entries'])]==old['entries']
 expected={(b['original_path'],b['sha256'],b['archived_path']) for b in bindings if str(Path(b['document']).parent/'source-archive-map.json')==path}
 added=after['entries'][len(old['entries']):];assert {(x['original_path'],x['sha256'],x['archived_path']) for x in added}==expected-{(x['original_path'],x['sha256'],x['archived_path']) for x in old['entries']}
 for key,value in after['documents'].items():
  if key not in old['documents']:assert h((R/key).read_bytes())==value
assert (oldcount,newcount)==(73,8)
r={'status':'accepted-bounded-additive-preservation-plan-only','plan_sha256':h((P/'preservation-plan-v2.json').read_bytes()),'bindings':178,'maps':81,'oldmaps_exactHEAD_and_canonicalarchive':73,'newmaps':8,'all_old_entries_and_documentpins_preserved':True,'all_added_entries_match_only_genuine_planned_bindings':True,'initial_test_bindings':len(d['initial_tests']),'tresca_repairs':len(d['tresca_repairs']),'map_reverse_consumer_bindings':178-len(d['initial_tests'])-len(d['tresca_repairs']),'preexisting_unresolved':d['preexisting_unresolved_summary']['primary'],'skipped_preexisting_doc_identity_mismatches':len(d['preexisting_unresolved_summary']['skipped_map_consumers']),'final_source_review_still_pending':True};(O/'preservation-plan-v2-structure-review.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
