from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def sha(b):return hashlib.sha256(b).hexdigest()
checks=[]
def ok(name,value):assert value,name;checks.append(name)
rows=json.loads((P/'source-delta.json').read_text())['files'];ok('five ledgers/five exact archives',len(rows)==10)
for row in rows:
 p=P/row['proposal'];b=p.read_bytes();ok('payload '+row['path'],sha(b)==row['sha256'] and len(b)==row['bytes'])
 base=W/row['path'];ok('preimage '+row['path'],(sha(base.read_bytes()) if base.is_file() else None)==row['preimage_sha256'])
 if row['path'].endswith('/DELIVERY.md') and not row['path'].startswith('catalogue/'):
  original=(W/row['path']).read_bytes();ok('original suffix verbatim '+row['path'],b.endswith(original))
  current=b.decode().split('## Historical ledger retained verbatim')[0]
  for gate in range(7):ok('current E'+str(gate)+' '+row['path'],f'- [X] **E{gate} ' in current)
  ok('E7 pending '+row['path'],'- [-] **E7 ' in current and '- [X] **E7 ' not in current)
  ok('E8 pending '+row['path'],'- [ ] **E8 ' in current and '- [X] **E8 ' not in current)
  ok('cleanup no false claim '+row['path'],'No path removal, reclaimed-space claim' in current)
for name,pin in json.loads((P/'evidence-pins.json').read_text()).items():ok('exact saved authority '+name,sha((ROOT/pin['path']).read_bytes())==pin['sha256'])
(P/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'checks_passed':checks,'source_or_shared_mutations':0,'actual_build_module_material_browser_remote_calls':0,'missing_model_ledger_paths':json.loads((P/'missing-paths.json').read_text()),'remaining':'Coordinator review/archive-first integration; exact E7/E8 actual receipts pending'},indent=2)+'\n');print(len(checks))
