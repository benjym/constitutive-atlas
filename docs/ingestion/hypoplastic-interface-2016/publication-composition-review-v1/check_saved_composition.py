"""Independent source/hash audit and pure-check reassessment, no author writes."""
from pathlib import Path
import hashlib,json,collections,subprocess
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';A=P/'publication-composition-v1';OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert sha(A/'manifest.json')=='8e550aa525163bd732520bacc6e96a6f3424883f47d8eac3e6fefa567b0f2b27'
m=read(A/'manifest.json')
for pin in m['files']:assert sha(A/pin['path'])==pin['sha256'] and (A/pin['path']).stat().st_size==pin['bytes']
assert sha(A/'install-map.json')=='4456f57dcc131856ed4ea30184c077307031842bd94d35a23bfaa80fb5b0edcb'
install=read(A/'install-map.json');assert len(install['targets'])==49 and len({e['target'] for e in install['targets']})==49
kinds=collections.Counter(e['kind'] for e in install['targets'])
for e in install['targets']:
 assert sha(A/e['source'])==e['sha256'] and (A/e['source']).stat().st_size==e['bytes'] and e['mode']=='100644'
 if e['target'].startswith('catalogue/source-snapshots/'):assert Path(e['target']).parts[2]==e['sha256']
 # Every retained branch preimage is read-only authenticated against its actual local commit.
for side,revision in m['refs'].items():
 for e in install['targets']:
  if e['kind']!='shared-composition':continue
  f=A/'inputs'/side/e['target']
  raw=subprocess.check_output(['git','show',revision+':'+e['target']],cwd=ROOT);assert raw==f.read_bytes()
# Reproduce142 source assertions, redirect its report and all temporary directories into ONLY our packet.
source=(A/'check_composition.py').read_text();assert "(P/'check-results.json').write_text" in source
source=source.replace('dir=P','dir=OUT').replace("(P/'check-results.json').write_text","(OUT/'source-reassessment.json').write_text")
namespace={'__file__':str(A/'check_composition.py'),'__name__':'independent_saved_check','OUT':OUT};exec(compile(source,str(A/'check_composition.py'),'exec'),namespace);namespace['check']()
reassessment=read(OUT/'source-reassessment.json');assert reassessment['passed'] and reassessment['checks']==142
# All listed additional ledger-context originals really match coordinator-owned evidence.
closure=read(A/'required-ledger-closure.json')
for e in closure:assert sha(ROOT/e['path'])==e['sha256']==sha(A/e['retained_input'])
closeout='136636f14ce12b0dd83e65a8c37d3af9a5cc1381'
assert subprocess.check_output(['git','rev-parse',closeout+'^'],cwd=ROOT).decode().strip()=='dcc645785faa3c83d791fdad92e7f3a20cab9721'
for e in closure:
 raw=subprocess.check_output(['git','show',closeout+':'+e['path']],cwd=ROOT);assert hashlib.sha256(raw).hexdigest()==e['sha256']
ledgerpath='docs/ingestion/hypoplastic-interface-2016/tracking-review-v1/source-archive-map.json';old=read(A/'inputs/ledger-v3'/ledgerpath);union=read(A/'proposed'/ledgerpath)
assert all(union['documents'].get(n)==h for n,h in old['documents'].items()) and all(e in union['entries'] for e in old['entries'])
assert sha(A/'proposed'/ledgerpath)=='96bee2fcbc9706789684c784138946592eefd7a5632b9b3ecd7a16af44e6ffc2'
result={'passed':True,'manifest_files':len(m['files']),'install_targets':49,'target_kinds':dict(kinds),'pure_source_assertions':142,'historical_receipt_pairs':39,'catalogue_models':50,'approvals':28,'profiles':50,'ledger_original_document_pins_retained':len(old['documents']),'ledger_original_archive_entries_retained':len(old['entries']),'missing_dcc_ledger_documents_requiring_source_closure':sum(not e['present_in_tested_dcc6457'] for e in closure),'required_ledger_documents_verified_in_closeout_commit':len(closure),'closeout_commit':closeout,'author_shared_or_Git_writes':False,'module_material_package_browser_compiler_remote_calls':0,'scope':'Source composition acceptance only; fresh merged package/browser/CI/live evidence required.'}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
